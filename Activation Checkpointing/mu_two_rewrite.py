"""Phase 3 - Activation-checkpoint graph rewriter (mu-TWO).

Consumes the recomps dict produced by Phase 2 and splices
each candidate's recompute subgraph into the joint forward+backward graph,
just before the candidate's first backward use.

Implemented:
  3.1  replace_subsequent_uses_of  - rewire backward users only.
  3.2  convert_inplace_to_outofplace - relu_/etc -> relu/etc (correctness fix).
  3.3  _splice_one_candidate       - splice one candidate's recompute subgraph.
  3.4  apply_activation_checkpointing - driver, ordered + invariant-checked.
  3.5  verify_correctness          - dual-tolerance gradient comparison.

"""

from typing import Any, Dict, List, Sequence, Set

import torch
import torch.fx as fx
from torch._functorch.partitioners import _extract_graph_with_inputs_outputs

from mu_two_select import CandidateInfo


#### Optional AOTOutput (Make it compatible to all version)  
try:
    from torch._functorch._aot_autograd.descriptors import AOTOutput
    _HAS_AOT_OUTPUT = True
except ImportError:  # torch < ~2.5
    AOTOutput = None  # type: ignore
    _HAS_AOT_OUTPUT = False


#####  3.1  replace_subsequent_uses_of                    
def replace_subsequent_uses_of(
    graph: fx.Graph, # linked with subgraph
    old_node: fx.Node, # the node that need recomputed 
    new_node: fx.Node, # the new recomputed node (with subgraph calculated)
) -> None:
    """For each user of old_node that comes AFTER new_node, replace its input with 
    new_node. Forward consumers keep using old_node. Its tensor drops (save space)
    via refcount once no later node references it.
    """
    old_node_users = set(old_node.users)
    for node in reversed(graph.nodes): # backward
        if node is new_node: # we get the first point we use the recompute node
            break
        if node in old_node_users: # rewind the target node user to the new node
            node.replace_input_with(old_node, new_node)



#### 3.2  Convert in-place forward ops to out-of-place equivalents

# Mapping from in-place ops to their out-of-place counterparts.

# In-place ops mutate their input and return the SAME tensor.

# For example, z = relu_(y) （in-place)
# new_z = relu_(y) -> this y is relu_(y) 
# The recompute does not just produce new_z. It also mutates the source y again.
# Also, since z is not a distinct tensor from y, the extractor may not have
# a clean output value to return for z.


INPLACE_TO_OUTOFPLACE = {
    torch.ops.aten.relu_.default: torch.ops.aten.relu.default,
}

def convert_inplace_to_outofplace(gm: fx.GraphModule) -> int:
    """Replace in-place forward ops with their out-of-place equivalents.

    Mutates node.target only
    Returns the number of nodes converted.
    """
    count = 0
    for node in gm.graph.nodes:
        if node.op == "call_function" and node.target in INPLACE_TO_OUTOFPLACE:
            node.target = INPLACE_TO_OUTOFPLACE[node.target]
            count += 1
    if count > 0: # recomplie the graph as new element is added
        gm.graph.lint()
        gm.recompile()
    return count



#### 3.3  Single-candidate splicer (from activation checkpoint.py)                                  
def _splice_one_candidate(
    gm: fx.GraphModule,
    ci: CandidateInfo, # the one that need to be recomputed
    profiler,
    name_to_node: Dict[str, fx.Node],
    retained: Set[fx.Node],
    spliced_recomp_names: Set[str],
    initial_node_by_name: Dict[str, fx.Node],
) -> None:
    """Splice ci's recompute subgraph into gm.graph before its first bwd use.
    """
    

    # refs into the gm the profiler ran on
    c = ci.node
    first_bw_idx = profiler.activation_lifetimes[c]["first_bwd_use_idx"]
    first_bw_node = profiler.nodes[first_bw_idx] 
    
    # Translate refs through initial_node_by_name so all graph
    # mutations below act on the target gm.
    c_target = initial_node_by_name[c.name]
    first_bw_node_target = initial_node_by_name[first_bw_node.name]
    recomp_srcs_target = [initial_node_by_name[s.name] for s in ci.recomp_srcs]

    ### Splice-time invariant 
    for s in ci.recomp_srcs:
        is_static = s.op in ("placeholder", "get_attr")
        is_retained = s in retained
        is_shared = s in ci.shared_recomp_srcs
        assert is_static or is_retained or is_shared, (
            f"{s.name} is not a valid source for recomputing {c.name} "
            f"(not static/retained/shared) "
        )
    for s in ci.shared_recomp_srcs:
        assert s.name in spliced_recomp_names, ( # if not recomputed, then it cannot be shared source
            f"shared source {s.name} for {c.name} has not been spliced yet -- "
            f"splice ordering bug"
        )
        
        # need to be combined to the new node
        # if it is computed, it need
        assert name_to_node[s.name] is not s, (
            f"shared source {s.name} for {c.name}: name_to_node still points "
            f"at the ORIGINAL forward node, not the recomputed copy "
            f"step missed"
        )

    ### Extract subgraph 
    extract_kwargs: Dict[str, Any] = {
        "joint_graph": gm.graph,
        "inputs": recomp_srcs_target,
        "outputs": [c_target],
    }

    # ensure the compatibility of new version and old version
    # new version need AOTOutput
    if _HAS_AOT_OUTPUT:
        extract_kwargs["outputs_descs"] = [AOTOutput()]
        
    # default method in python
    recompute_subgraph = _extract_graph_with_inputs_outputs(**extract_kwargs)

    ### Splice nodes
    with gm.graph.inserting_before(first_bw_node_target):
        for n in recompute_subgraph.nodes:
            if n.op in ("placeholder", "output"):
                continue
            
            # arg_transform uses name_to_node to map each fx.Node arg
            # from the extracted subgraph back to its counterpart in
            # the live gm.graph (so the copied node reads from live nodes,
            # not from dangling subgraph nodes).
            
            # Copy the nodes of the new sub-graph to old graph and transform its
            # inputs to match the old-graph inputs. The arg_transform function
            # will pass the input arguments of the new node and will expect a
            # mapping to the nodes of the old graph.
            new_node = gm.graph.node_copy(n, arg_transform=lambda arg: name_to_node[arg.name])
            
            # We are add the end of the subgraph (complete recomputing)
            if n.name == c.name:
                # Rewire backward consumers of the target candidate to read
                # from new_node. 
                replace_subsequent_uses_of(
                    gm.graph, old_node=c_target, new_node=new_node
                )
                
            # Rebind name_to_node[n.name] from original to recomputed copy
            # so any later candidate that has referenced by the same name 
            # picks up the recomputed copy.
            name_to_node[n.name] = new_node

    spliced_recomp_names.add(c.name)


#### 3.4  Driver                                                            

def apply_activation_checkpointing(
    gm: fx.GraphModule,
    recomps: Dict[fx.Node, CandidateInfo],
    profiler,
) -> fx.GraphModule:
    """Splice all selected candidates' recompute subgraphs into gm.graph.

    Pre-pass: convert_inplace_to_outofplaceruns first. Doing this after 
    the profiler ran is safe: node identity and graph structure are preserved.

    Returns the same gm (mutated in place + recompiled). Empty recomps
    is a no-op shortcut.
    """
    if not recomps:
        return gm

    n_converted = convert_inplace_to_outofplace(gm)
    if n_converted > 0:
        print(f"[AC] converted {n_converted} in-place op(s) to out-of-place")

    #  snapshot of target gm at start (stable)
    #  profiler gm and current gm might not be the same one (need name to match)
    initial_node_by_name: Dict[str, fx.Node] = {n.name: n for n in gm.graph.nodes}
    #  same as initial_node_by_name
    #  later get recomputed
    name_to_node: Dict[str, fx.Node] = dict(initial_node_by_name)
    # retained activations
    retained: Set[fx.Node] = set(profiler.activation_nodes) - set(recomps.keys())
    spliced_recomp_names: Set[str] = set()

    # sort according to the first use in backward then by id (break tie)
    ordered = sorted(
        recomps.values(),
        key=lambda ci: (
            profiler.activation_lifetimes[ci.node]["first_bwd_use_idx"],
            profiler.node_to_idx[ci.node],
        ),
    )

    # for each node that need to be recomputed
    for ci in ordered:
        _splice_one_candidate(
            gm, ci, profiler, name_to_node, retained, spliced_recomp_names,
            initial_node_by_name=initial_node_by_name,
        )

    gm.graph.lint()
    gm.recompile()
    return gm



##### 3.5  Verification helper                                                    
def _flatten_tensors(obj: Any) -> List[torch.Tensor]:
    """Recursively pull all tensors out of a nested tuple / list / dict."""
    if isinstance(obj, torch.Tensor):
        return [obj]
    if isinstance(obj, dict):
        out: List[torch.Tensor] = []
        for v in obj.values():
            out.extend(_flatten_tensors(v))
        return out
    if isinstance(obj, (tuple, list)):
        out = []
        for item in obj:
            out.extend(_flatten_tensors(item))
        return out
    return []


def _clone_args(args: Sequence[Any]) -> List[Any]:
    """Deep-clone all tensors in ``args``; pass through everything else."""
    return [a.clone() if isinstance(a, torch.Tensor) else a for a in args]


def verify_correctness(
    original_gm: fx.GraphModule,
    modified_gm: fx.GraphModule,
    args: Sequence[Any],
    atol: float = 1e-5,
    rtol: float = 1e-4,
    loose_atol: float = 0.5,
    loose_rtol: float = 1e-2,
) -> bool:
    """Run both graphs on INDEPENDENTLY cloned inputs; compare all output tensors.

    Why clone: the traced graph includes optimizer steps that mutate parameter
    and state tensors in place. Without cloning, the first execution would
    change the shared state before the second starts, making the comparison
    vacuous.

    Why two tolerance levels:
      tight  (atol/rtol)  for fwd / bwd outputs (loss, gradients).
      loose  (loose_atol/loose_rtol) for optimizer-updated params + states. (adam will make the thing larger)


    Returns True iff zero "hard failures"
    """
    args_orig = _clone_args(args)
    args_mod = _clone_args(args)

    with torch.no_grad():
        orig_out = original_gm(*args_orig)
        orig_tensors = [t.clone() for t in _flatten_tensors(orig_out)]

    with torch.no_grad():
        mod_out = modified_gm(*args_mod)
        mod_tensors = [t.clone() for t in _flatten_tensors(mod_out)]

    if len(orig_tensors) != len(mod_tensors):
        print(
            f"[verify] tensor count mismatch: {len(orig_tensors)} vs {len(mod_tensors)}"
        )
        return False
    if not orig_tensors:
        print("[verify] no tensor outputs to compare")
        return True

    n_tight = n_loose = n_fail = 0
    max_diffs: List[float] = []
    for i, (o, m) in enumerate(zip(orig_tensors, mod_tensors)):
        if o.shape != m.shape:
            print(f"[verify] tensor {i}: shape mismatch ({o.shape} vs {m.shape})")
            n_fail += 1
            continue
        d = (o - m).abs().max().item()
        max_diffs.append(d)
        if torch.allclose(o, m, atol=atol, rtol=rtol):
            n_tight += 1
        elif torch.allclose(o, m, atol=loose_atol, rtol=loose_rtol): 
            n_loose += 1
        else:
            print(f"[verify] tensor {i}: FAIL (max|delta|={d:.3e})")
            n_fail += 1

    print(
        f"[verify] {n_tight} tight match, {n_loose} loose match "
        f"(optimizer drift), {n_fail} failure(s) of {len(orig_tensors)} tensors"
    )
    if max_diffs:
        print(f"[verify] max|delta| across all tensors: {max(max_diffs):.3e}")
    return n_fail == 0
