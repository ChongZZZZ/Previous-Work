"""Phase 2 - Activation-checkpoint candidate selection (mu-TWO).

Implemented:
  2.1  CandidateInfo                - schema for one recompute candidate.
  2.2  walk_srcs                    - find a candidate's recompute frontier.
  2.3  build_candidates             - assemble the initial candidate dict.
  2.4  t_alive_when_cand_recomputes - Alg F sharing check.
  2.4  _absorb_chain                - cascade body for Algs E / F.
  2.4  simulate_peak_with_recompute - Alg G specialization for swap=empty.
  2.4  _update_recomps              - Alg E.
  2.4  _update_candidates           - Alg F (with sharing).
  2.5  select_recompute_set         - greedy main entry.
"""

import warnings
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple
import torch.fx as fx


#### 2.1  CandidateInfo                                                          
@dataclass
class CandidateInfo:
    """One recomputation candidate. 
    
    Mutated in place by the cascade-update steps （Algs E / F) when other
    candidates are picked, so ``ratio`` is a derived property rather than a
    stored field.
    """

    node: fx.Node
    size_bytes: int
    recomp_srcs: Set[fx.Node] = field(default_factory=set) # Need to be calculated from
    recomp_middle: Set[fx.Node] = field(default_factory=set) # Intermediate steps (if being previous recomputed)
    recomp_time: float = 0.0  # Single time for recomputation
    recomp_cnt: int = 1 # Number of times for recomputation
    total_recomp_time: float = 0.0 # recomp_time* recomp_cnt
    shared_recomp_srcs: Set[fx.Node] = field(default_factory=set) 
    # subset of recomp_srcs whose providers are themselves recomputed
    # candidates; their bwd-window copy is reused instead of re-running

    @property
    def recompute_ratio(self) -> float:
        # recompute_ratio = memory_size / total_recomp_time (used for greedy selection)
        if self.total_recomp_time <= 0:
            return 0.0
        return self.size_bytes / self.total_recomp_time



#### 2.2  Source-walking helper      
def walk_srcs(
    profiler, # profiler from Phase 1
    candidate: fx.Node, # single activation 
    retained_activations: Set[fx.Node], # activation exclude previous ones
) -> Tuple[Set[fx.Node], Set[fx.Node], float]:
    """ Create recompute profile for one single activation candidiate

    BFS upward from ``candidate`` through ``all_input_nodes``. Each visited
    node is classified as either:
      - a placeholder, a get_attr, or a retained activation 
            goes into recomp_srcs (the BFS terminates this branch)
      - a transient OTHER forward op
            goes into recomp_middle

    Returns
    -------
    recomp_srcs   : Set[fx.Node] - the frontier; alive when backward needs c.
    recomp_middle : Set[fx.Node] - OTHER forward ops on the recompute chain.
    recomp_time   : float        - sum of avg_runtime over middle | {c} (ms).
    """
    recomp_srcs: Set[fx.Node] = set()
    recomp_middle: Set[fx.Node] = set()
    visited: Set[fx.Node] = {candidate}
    queue = list(candidate.all_input_nodes)  # all of its source code

    while queue:
        n = queue.pop()
        if n in visited:
            continue
        visited.add(n)
        if n.op in ("placeholder", "get_attr") or n in retained_activations:
            recomp_srcs.add(n)
        else:
            recomp_middle.add(n) # no use in backward （released even if AC is not there)
            queue.extend(n.all_input_nodes)

    # Compute time for each activation 
    recomp_time = profiler.avg_runtime.get(candidate, 0.0) + sum(profiler.avg_runtime.get(m, 0.0) for m in recomp_middle)
    
    return recomp_srcs, recomp_middle, recomp_time

#### 2.3  Initial candidate construction                                    
def build_candidates(profiler) -> Dict[fx.Node, CandidateInfo]:
    """Assemble the initial candidate dict from all activation nodes.

    For each ACT, walks its recompute frontier under the assumption that 
    every *other* activation is retained.

    Later will be mutated by greedy alg and AC recompute
    """
    # Initial state: every ACT is assumed retained
    # Greedy will revise this
    retained_activations: Set[fx.Node] = set(profiler.activation_nodes)
    candidates: Dict[fx.Node, CandidateInfo] = {}

    for c in profiler.activation_nodes:
        size = profiler.activation_lifetimes[c]["size_bytes"]
        if not size:
            continue
        recomp_srcs, recomp_middle, recomp_time = walk_srcs(profiler, c, retained_activations - {c})
        candidates[c] = CandidateInfo(
            node=c,
            size_bytes=size,
            recomp_srcs=recomp_srcs,
            recomp_middle=recomp_middle,
            recomp_time=recomp_time,
            recomp_cnt=1,
            total_recomp_time=recomp_time,
        )
    return candidates


#### Paper Algs  E / F                      
def t_alive_when_cand_recomputes(
    profiler,
    t_node: fx.Node,
    cand_node: fx.Node,
) -> bool:
    """Paper Alg F — sharing check.

    Whether cand can REUSE the recomputed copy of t or must instead absorb t's entire chain.

    The recomputed copy of t lives in memory between [t.first_bwd_use_idx, t.last_bwd_use_idx]. 
    cand will trigger its own recompute at cand.first_bwd_use_idx. 
    If that timestamp falls inside t's window, t's copy is still alive, sharing is possible.
    """
    t_lt = profiler.activation_lifetimes[t_node]
    cand_lt = profiler.activation_lifetimes[cand_node]
    return (
        t_lt["first_bwd_use_idx"]
        <= cand_lt["first_bwd_use_idx"]
        <= t_lt["last_bwd_use_idx"]
    )


def _absorb_chain(
    target: "CandidateInfo",
    t_node: fx.Node,
    t_info: "CandidateInfo",
) -> None:
    """
    Absorb the chain if the source node is being recomputed by paper Alg E and Alg F.
    """
    target.recomp_srcs.discard(t_node) # remove t_node from src since it is being recomputed
    target.recomp_srcs |= t_info.recomp_srcs # add t's src nodes to target's src nodes
    
    # We first know that s in t.shared_recomp_srcs, where s.first_bwd_use <= t.first_bwd_use <= s.last_bwd_use
    # We assume s.first_bwd_use <= target.first_bwd_use <= s.last_bwd_use
    # But we will recheck this in select recompute set
    target.shared_recomp_srcs |= t_info.shared_recomp_srcs 
    
    target.recomp_middle |= t_info.recomp_middle | {t_node}  # all need to be re-executed when target recomputes
    target.recomp_time += t_info.recomp_time # Accumulate t.recomp_time into target.recomp_time
    # Refresh target.total_recomp_time so recompute_ratio stays consistent 
    target.total_recomp_time = target.recomp_time * target.recomp_cnt 

def simulate_peak_with_recompute(
    profiler,
    recomp_set: Set[fx.Node],
) -> int:
    """Predict forward+backward peak memory if recomp_set is recomputed.

    Per-node lifetime rule:
      - Node not in recomp_set:
            lifetime = [producer_idx, max(user idx)]   
      - Node in recomp_set:
            original  lives [producer_idx,    last_fwd_use_idx]
            recompute lives [first_bwd_use_idx, last_bwd_use_idx]

    Returns the maximum live bytes across [0, opt_idx)
    """
    n = len(profiler.nodes)
    opt_idx = profiler.node_to_idx[profiler.optimizer_node]
    live = [0] * n

    for node, size in profiler.node_output_bytes.items():
        if size == 0:
            continue
        start = profiler.node_to_idx[node] # its birth time
        end = max(  # last use time
            (profiler.node_to_idx[u] for u in node.users),
            default=start,
        )
        if node in recomp_set:
            lt = profiler.activation_lifetimes[node]
            # original tensor (freed after last_fwd_use)
            for i in range(start, lt["last_fwd_use_idx"] + 1):
                live[i] += size
            # recomputed copy  (lives only inside its backward window)
            for i in range(lt["first_bwd_use_idx"], lt["last_bwd_use_idx"] + 1):
                live[i] += size
        else:
            for i in range(start, end + 1):
                live[i] += size

    return max(live[:opt_idx]) if opt_idx > 0 else max(live) # check for peak


def _update_recomps(
    t_node: fx.Node,
    t_info: "CandidateInfo",
    recomps: Dict[fx.Node, "CandidateInfo"],
) -> int:
    """Paper Alg E — update existing recomps when t is just picked.

    Returns
    -------
    recomp_cnt : int
        Starts at 1 ; +1 for each existing rp that depends on t.
    """
    recomp_cnt = 1  # since it is chosen to be computed
    for rp in recomps.values(): # view current recompute lists
        if rp is t_info:
            continue
        # if the newly selected recompute nodes in previous recompute node source
        if t_node in rp.recomp_srcs:
            _absorb_chain(rp, t_node, t_info) # we update the chain of the old recompute node
            recomp_cnt += 1 # the newly selected recompute node need to be recompute
    return recomp_cnt


def _update_candidates(
    t_node: fx.Node,
    t_info: "CandidateInfo",
    candidates: Dict[fx.Node, "CandidateInfo"],
    recomps: Dict[fx.Node, "CandidateInfo"],
    profiler,
) -> None:
    """Paper Alg F (with sharing) — update remaining candidates when t is picked.

    cand.updateRecomputeRatio()is auto-satisfied here:
        recompute_ratio is a @property derived from total_recomp_time.
    """
    for cand in candidates.values():
        # Case 1: t is in cand's recompute sources
        if t_node in cand.recomp_srcs:
            if t_alive_when_cand_recomputes(profiler, t_node, cand.node):
                # if we recompte cand, we can directly use t (since it is computed)
                cand.shared_recomp_srcs.add(t_node)
                continue
            # Add the chain of t
            _absorb_chain(cand, t_node, t_info)
            cand.total_recomp_time = cand.recomp_time # default setting one time after absorbing
            
            for rp in recomps.values():
                if cand.node in rp.recomp_srcs: # if previous recompute node use it, add on
                    cand.total_recomp_time += cand.recomp_time
                    
        # Case 2: cand is a source for t
        if cand.node in t_info.recomp_srcs:
            cand.total_recomp_time = t_info.recomp_cnt * cand.recomp_time


#### 2.5  Greedy entry point — paper Alg B
def select_recompute_set(
    profiler,
    mem_limit_bytes: int,
) -> Dict[fx.Node, CandidateInfo]:
    """Greedy recompute selection — paper Alg B

    Picks candidates in decreasing recompute_ratio order, applies the
    cascade updates (Alg E + Alg F), and stops once the simulated
    forward+backward peak meets the memory limit.
    
    If candidates are exhausted but the predicted peak still exceeds the target. 
        Treat the result as best-effort.
    
    Returns
    -------
    recomps : Dict[fx.Node, CandidateInfo]
        Activations chosen to be discarded after their last forward use and
        recomputed in backward. Everything in profiler.activation_nodes
        not in recomps.keys() is implicitly retained. 
        Returns {} if the baseline peak already meets mem_limit_bytes.
    """
    candidates = build_candidates(profiler) # build initial data
    recomps: Dict[fx.Node, CandidateInfo] = {}

    if simulate_peak_with_recompute(profiler, set()) <= mem_limit_bytes:
        return recomps

    while candidates:
        # use geedy to pick the one with maximum compute_ratio
        t_node, t_info = max(candidates.items(), key=lambda kv: kv[1].recompute_ratio)

        # move t from candidates torecomps
        del candidates[t_node]
        recomps[t_node] = t_info

        # Algorithm E
        recomp_cnt = _update_recomps(t_node, t_info, recomps)
        t_info.recomp_cnt = recomp_cnt
        t_info.total_recomp_time = t_info.recomp_time * recomp_cnt

        # Algorithm F
        _update_candidates(t_node, t_info, candidates, recomps, profiler)

        if simulate_peak_with_recompute(profiler, set(recomps)) <= mem_limit_bytes:
            break

    final_peak = simulate_peak_with_recompute(profiler, set(recomps))
    if final_peak > mem_limit_bytes: ## cannot satified the target memory
        warnings.warn(
            f"select_recompute_set: exhausted {len(recomps)} candidates "
            f"but predicted peak {final_peak} still exceeds limit "
            f"{mem_limit_bytes}. Caller should treat this as best-effort.",
            stacklevel=2,
        )


    # Every entry in recomp_srcs falls into exactly one of three legal classes:
    #   1. placeholder / get_attr  -- always alive (static graph input)
    #   2. retained activation     -- not in recomps, kept around fwd->bwd
    #   3. shared recomputed src   -- another recomputed candidate whose bwd
    #                                  window covers ci.first_bwd_use_idx
    retained = set(profiler.activation_nodes) - set(recomps.keys())
    for ci in recomps.values():
        # shared_recomp_src is a subset of recomp_srcs
        assert ci.shared_recomp_srcs <= ci.recomp_srcs, (
            f"subset invariant violated for {ci.node.name}: "
            f"shared_recomp_srcs - recomp_srcs = "
            f"{[n.name for n in ci.shared_recomp_srcs - ci.recomp_srcs]}"
        )
        
        # Every recomp_src is static, retained, or shared.
        for s in ci.recomp_srcs:
            is_static = s.op in ("placeholder", "get_attr")
            is_retained = s in retained
            is_shared = s in ci.shared_recomp_srcs
            assert is_static or is_retained or is_shared, (
                f"recomp_srcs invariant violated: src {s.name} for "
                f"recomputed {ci.node.name} is neither static, retained, "
                f"nor shared — see activation_checkpoint.py:73-75"
            )
            
        # Every shared src is itself recomputed and bwd-window-valid.
        for s in ci.shared_recomp_srcs:
            # we first check the existence of s that we can shared
            assert s in recomps, (
                f"shared_recomp_srcs invariant violated: src {s.name} for "
                f"recomputed {ci.node.name} is marked shared but is not "
                f"itself a recomputed candidate"
            )
            # we then check the timing （as whether we have to use this)
            assert t_alive_when_cand_recomputes(profiler, s, ci.node), (
                f"shared_recomp_srcs invariant violated: shared src {s.name} "
                f"for recomputed {ci.node.name} has a backward window that "
                f"does NOT cover {ci.node.name}."
            )

    return recomps
