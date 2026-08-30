from collections import defaultdict
from enum import Enum
from typing import Dict, Any
import torch
import torch.fx as fx


class OP(str, Enum):
    CALL_FUNCTION = "call_function"
    CALL_MODULE = "call_module"
    CALL_METHOD = "call_method"
    GET_ATTR = "get_attr"
    OUTPUT = "output"
    PLACEHOLDER = "placeholder"


class NodeType(Enum):
    """
    NodeType is a enum that records the type of the tensors in the graph.
    """

    PARAM = 0
    ACT = 1
    GRAD = 2
    OTHER = 3
    OPT_STATE = 4


# This is an example graph_profiler that extends the fx.Interpreter class, it
# will perform graph execution by running the graph node by node.


class GraphProfiler(fx.Interpreter):
    def __init__(self, module: fx.GraphModule, garbage_collect_values: bool = True):
        super().__init__(module, garbage_collect_values)

        # You should perform the static analysis of the graph here. In
        # particular you might want to find the intermediate
        # nodes/activations/feature_maps in the graph that will be defined as
        # those nodes which are not parameters (not placeholder node types) but
        # are created during the forward pass and are also used in the backward
        # pass for computation.

        # The boundary between the forward pass and backward pass can be
        # identified by locating the node '%sep : [num_users=1] =
        # call_function[target=torch.ops.separator.sep.default]' which will
        # define the end of the forward pass. You will see the loss function
        # after this operation and then you will encounter a node named,
        # '%sep_backward : [num_users=1] =
        # call_function[target=torch.ops.separator.sep_backward.default]'. This
        # node marks the beginning of the backward pass.

        # For these intermediate nodes in the graph, you will record their last
        # use in the forward pass and their first use in the backward pass.

        # The parameters of the models are the placeholder (input) nodes of the
        # graph. Note that not all the placeholder nodes of the graph are
        # parameters. The optimizer's states and the input mini-batch are also
        # placeholder nodes that given as inputs to the graph.

        # The parameters and gradients of the model can be otained using the
        # optimizer node's arguments. The optimizer node can be identified by
        # the node '%_fused_adam : [num_users=3] =
        # call_function[target=torch.ops.aten._fused_adam.default]'.
        # The argument at position 0 is the list of parameter nodes, while the
        # argument at position 1 is the list of gradient nodes.

        
        # for node in self.module.graph.nodes:
        #     print("Node name: ", node.name)
        #     print("Node type: ", node.op)
        #     print("Node target: ", node.target)
        #     print("Input to this node", node.all_input_nodes)
        #     print("Users of this node: ", node.users)
        
        # Create node list and index map
        self.nodes = list(self.module.graph.nodes)
        self.node_to_idx = {node: idx for idx, node in enumerate(self.nodes)} # record the sequence

        # Find boundary nodes
        self.sep_node = None # end of forward
        self.sep_backward_node = None # start of backward
        self.optimizer_node = None # optimizer node

        for node in self.nodes:
            if node.target == torch.ops.separator.sep.default:
                self.sep_node = node
            elif node.target == torch.ops.separator.sep_backward.default:
                self.sep_backward_node = node
            elif '_fused_adam' in str(node.target):
                self.optimizer_node = node

        sep_idx = self.node_to_idx[self.sep_node]
        sep_bwd_idx = self.node_to_idx[self.sep_backward_node]
        opt_idx = self.node_to_idx[self.optimizer_node]

        # Classify each node into a region
        self.forward_nodes = set()
        self.backward_nodes = set()
        self.optimizer_nodes = set()

        # Categorize the regions
        for node in self.nodes:
            idx = self.node_to_idx[node]
            if idx <= sep_idx:
                self.forward_nodes.add(node)
            elif idx >= sep_bwd_idx and idx < opt_idx:
                self.backward_nodes.add(node)
            elif idx >= opt_idx and node.op != OP.OUTPUT:
                self.optimizer_nodes.add(node)

        # Classify nodes using the optimizer
        self.param_nodes = set(self.optimizer_node.args[0])
        self.grad_nodes = set(self.optimizer_node.args[1])

        # Optimizer states:
        self.opt_state_nodes = set()
        for arg in self.optimizer_node.args[2:]:
            if isinstance(arg, (list, tuple)): #  skip the hyperparameters just float
                for n in arg:
                    if isinstance(n, fx.Node):
                        self.opt_state_nodes.add(n)

        # Build a per-node type map
        self.node_type: Dict[fx.Node, NodeType] = {}
        for node in self.nodes:
            if node in self.param_nodes:
                self.node_type[node] = NodeType.PARAM
            elif node in self.grad_nodes:
                self.node_type[node] = NodeType.GRAD
            elif node in self.opt_state_nodes:
                self.node_type[node] = NodeType.OPT_STATE
            else:
                self.node_type[node] = NodeType.OTHER

        # Identify activations
        self.activation_nodes = set()
        for node in self.forward_nodes:
            # Not a placeholder or get_attr (both are stable sources -- alive
            # throughout fwd+bwd, never worth recomputing). Excluding get_attr
            # here keeps the activation set consistent with mu_two_select's
            # walk_srcs, which terminates BFS at placeholder/get_attr.
            if node.op == OP.PLACEHOLDER or node.op == OP.GET_ATTR:
                continue
            # Not a param, grad, or opt_state
            if node in self.param_nodes or node in self.grad_nodes or node in self.opt_state_nodes:
                continue
            # Must have at least one user in the backward region
            has_backward_user = any(user in self.backward_nodes for user in node.users)
            if has_backward_user:
                self.activation_nodes.add(node)
                self.node_type[node] = NodeType.ACT

        # Record activation lifetimes 
        self.activation_lifetimes: Dict[fx.Node, Dict] = {}
        for node in self.activation_nodes:
            producer_idx = self.node_to_idx[node] # when it is create

            # last use in the forward pass
            fwd_user_indices = []
            for user in node.users:              
                if user in self.forward_nodes:    # in the forward region
                    idx = self.node_to_idx[user]  # get their position
                    fwd_user_indices.append(idx)
            last_fwd_use_idx = max(fwd_user_indices) if fwd_user_indices else producer_idx

            # first and last use in the backward
            bwd_user_indices = []
            for user in node.users:
                if user in self.backward_nodes:
                    idx = self.node_to_idx[user]
                    bwd_user_indices.append(idx)
            first_bwd_use_idx = min(bwd_user_indices)
            last_bwd_use_idx = max(bwd_user_indices)

            self.activation_lifetimes[node] = {
                "producer_idx": producer_idx,
                "last_fwd_use_idx": last_fwd_use_idx,
                "first_bwd_use_idx": first_bwd_use_idx,
                "last_bwd_use_idx": last_bwd_use_idx,
                "size_bytes": None,
            }

        # Initialize runtime measurement
        self.node_runtimes: Dict[fx.Node, list] = defaultdict(list) #execution times per iter
        self.node_mem: Dict[fx.Node, list] = defaultdict(list) # per-node list of memory snapshots
        self.node_output_bytes: Dict[fx.Node, int] = {} #per-node output tensor size in bytes

    def run(
        self,
        *args,
        initial_env: Dict[fx.Node, Any] | None = None,
        enable_io_processing: bool = True
    ) -> Any:
        return super().run(
            *args, initial_env=initial_env, enable_io_processing=enable_io_processing
        )

    @staticmethod
    def _tensor_bytes(result) -> int:
        #Recursively compute total bytes of a run_node result.

        if isinstance(result, torch.Tensor): # a single tensor
            return result.numel() * result.element_size()
        if isinstance(result, (tuple, list)): # list of tensors
            return sum(GraphProfiler._tensor_bytes(r) for r in result)
        return 0

    def run_node(self, n: fx.Node) -> Any:
        # If you are in the backward pass region and one of the feature maps 'x'
        # was swapped out, and if node 'n' will use this feature map 'x' as one
        # of its inputs then you swap 'x' back to the GPU memory here.

        # you can start measuring the run-time and memory usage of a node here
        torch.cuda.synchronize()
        mem_before = torch.cuda.memory_allocated()

        start_event = torch.cuda.Event(enable_timing=True)
        end_event = torch.cuda.Event(enable_timing=True)

        start_event.record()
        result = super().run_node(n)
        end_event.record()
        torch.cuda.synchronize() # blocks the CPU until all queued GPU operations comple

        mem_after = torch.cuda.memory_allocated()

        elapsed_ms = start_event.elapsed_time(end_event)
        self.node_runtimes[n].append(elapsed_ms)
        self.node_mem[n].append({"mem_before": mem_before, "mem_after": mem_after})

        # Record output size 
        if n not in self.node_output_bytes: # only need to calculate once
            self.node_output_bytes[n] = self._tensor_bytes(result)
            if n in self.activation_lifetimes and self.activation_lifetimes[n]["size_bytes"] is None:# fill up the size of the activation
                self.activation_lifetimes[n]["size_bytes"] = self.node_output_bytes[n]

        # you can end measuring the run-time of a node here HINT: Use
        # torch.cuda.Events for doing time measurements of operations.

        # If you are in the forward pass region and if the current node 'n' is
        # the last user of a feature map 'x', then it should be swapped out to
        # the CPU memory here.

        return result

    def aggregate_stats(self) -> None:
        # You are expected run the profiler for x warm-up iterations and y
        # actual measurement iterations. The run-time measurement then needs to
        # be averaged over the y runs.
        self.avg_runtime: Dict[fx.Node, float] = {}
        self.avg_mem_delta: Dict[fx.Node, float] = {}
        for node in self.nodes:
            # Average runtime across profiling iterations
            times = self.node_runtimes[node]
            self.avg_runtime[node] = sum(times) / len(times) if times else 0.0

            # Average memory delta across profiling iterations
            mems = self.node_mem[node]
            if mems:
                deltas = [m["mem_after"] - m["mem_before"] for m in mems]
                self.avg_mem_delta[node] = sum(deltas) / len(deltas)
            else:
                self.avg_mem_delta[node] = 0.0

        # Track every node's output from creation to last use
        num_nodes = len(self.nodes)
        opt_idx = self.node_to_idx[self.optimizer_node]

        # Try to track size of each category 
        self.liveness = {
            "params":      [0] * num_nodes,
            "activations": [0] * num_nodes,
            "grads":       [0] * num_nodes,
            "opt_states":  [0] * num_nodes,
            "other":       [0] * num_nodes,
        }

        for node in self.nodes:
            size = self.node_output_bytes.get(node, 0)
            if size == 0:
                continue
            
            
            start = self.node_to_idx[node]
            # search for last use as when it is freed
            if node.users:
                end = max(self.node_to_idx[u] for u in node.users)
            else:
                end = start

            ntype = self.node_type.get(node, NodeType.OTHER)
            if ntype == NodeType.PARAM:
                cat = "params"
            elif ntype == NodeType.ACT:
                cat = "activations"
            elif ntype == NodeType.GRAD:
                cat = "grads"
            elif ntype == NodeType.OPT_STATE:
                cat = "opt_states"
            else:
                cat = "other"

            # add the memory for that specific category throughout the nodes existence
            for i in range(start, end + 1):
                self.liveness[cat][i] += size

        # Compute total memory
        self.total_liveness = [
            sum(self.liveness[cat][i] for cat in self.liveness)
            for i in range(num_nodes)
        ]
        self.peak_step = max(range(num_nodes), key=lambda i: self.total_liveness[i])
        self.peak_memory = self.total_liveness[self.peak_step]

        # Forward+backward peak (what activation checkpointing targets)
        self.fwd_bwd_peak_step = max(range(opt_idx), key=lambda i: self.total_liveness[i])
        self.fwd_bwd_peak_memory = self.total_liveness[self.fwd_bwd_peak_step]

    def _get_region(self, node: fx.Node) -> str:
        if node in self.forward_nodes:
            return "forward"
        elif node in self.backward_nodes:
            return "backward"
        elif node in self.optimizer_nodes:
            return "optimizer"
        return "other"

    # mainly just collect data
    def print_stats(self) -> None:
        import csv
        # Node states
        header = ["idx", "name", "op", "region", "type", "avg_ms", "output_bytes", "avg_mem_delta"]
        rows = []
        for node in self.nodes:
            idx = self.node_to_idx[node]
            rows.append([
                idx,
                node.name,
                node.op,
                self._get_region(node),
                self.node_type.get(node, NodeType.OTHER).name,
                f"{self.avg_runtime.get(node, 0.0):.4f}",
                self.node_output_bytes.get(node, 0),
                f"{self.avg_mem_delta.get(node, 0.0):.0f}",
            ])

        with open("node_stats.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        # Activation lifetime table
        act_header = ["name", "size_bytes", "producer_idx", "last_fwd_use", "first_bwd_use", "last_bwd_use", "idle_steps"]
        act_rows = []
        for node, lt in self.activation_lifetimes.items():
            idle = lt["first_bwd_use_idx"] - lt["last_fwd_use_idx"]
            act_rows.append([
                node.name,
                lt["size_bytes"] or 0,
                lt["producer_idx"],
                lt["last_fwd_use_idx"],
                lt["first_bwd_use_idx"],
                lt["last_bwd_use_idx"],
                idle,
            ])

        with open("activation_lifetimes.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(act_header)
            writer.writerows(act_rows)

        # Peak memory summary
        peak = self.peak_step
        fwd_bwd_peak = self.fwd_bwd_peak_step
        with open("peak_memory_summary.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["category", "bytes"])
            writer.writerow(["peak_step", peak])
            writer.writerow(["peak_node", self.nodes[peak].name])
            writer.writerow(["total", self.peak_memory])
            writer.writerow(["params", self.liveness["params"][peak]])
            writer.writerow(["activations", self.liveness["activations"][peak]])
            writer.writerow(["grads", self.liveness["grads"][peak]])
            writer.writerow(["opt_states", self.liveness["opt_states"][peak]])
            writer.writerow(["other", self.liveness["other"][peak]])
            writer.writerow(["fwd_bwd_peak_step", fwd_bwd_peak])
            writer.writerow(["fwd_bwd_peak_node", self.nodes[fwd_bwd_peak].name])
            writer.writerow(["fwd_bwd_peak", self.fwd_bwd_peak_memory])
            writer.writerow(["fwd_bwd_params", self.liveness["params"][fwd_bwd_peak]])
            writer.writerow(["fwd_bwd_activations", self.liveness["activations"][fwd_bwd_peak]])
            writer.writerow(["fwd_bwd_grads", self.liveness["grads"][fwd_bwd_peak]])
            writer.writerow(["fwd_bwd_opt_states", self.liveness["opt_states"][fwd_bwd_peak]])
            writer.writerow(["fwd_bwd_other", self.liveness["other"][fwd_bwd_peak]])


    def reset_stats(self) -> None:
        # The statistics must be cleared out after x warm-up iterations and
        # reset before the actual measurement begins.
        # Only clear runtime measurement and keep static analysis data
        self.node_runtimes = defaultdict(list)
        self.node_mem = defaultdict(list)
