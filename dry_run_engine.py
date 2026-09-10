from typing import List, Dict, Any

class DryRunEngine:
    def __init__(self, raw_trace_data: List[Dict[str, Any]] = None):
        self.steps = raw_trace_data or []

    @classmethod
    def generate_trace_from_analysis(cls, parsed_analysis: Dict[str, Any]) -> "DryRunEngine":
        """Generates normalized step-by-step execution trace objects."""
        trace_steps = []
        raw_steps = parsed_analysis.get("dry_run_steps", [])
        
        for idx, step in enumerate(raw_steps, start=1):
            trace_steps.append({
                "step": idx,
                "line": step.get("line_number", 1),
                "action": step.get("action_description", "Executing instruction"),
                "variables": step.get("variables_state", {}),
                "var_changes": step.get("variable_changes", {}),
                "condition": step.get("condition_evaluation", None),
                "iteration": step.get("loop_iteration", None),
                "call_stack": step.get("call_stack", ["main()"]),
                "output": step.get("output_produced", None)
            })
            
        if not trace_steps:
            # Fallback default simulation trace if trace list is empty
            trace_steps = [{
                "step": 1,
                "line": 1,
                "action": "Program start",
                "variables": {},
                "var_changes": {},
                "condition": None,
                "iteration": None,
                "call_stack": ["main()"],
                "output": "Execution Started"
            }]
            
        return cls(trace_steps)

    def get_total_steps(self) -> int:
        return len(self.steps)

    def get_step(self, step_index: int) -> Dict[str, Any]:
        if 0 <= step_index < len(self.steps):
            return self.steps[step_index]
        return self.steps[0]

    def get_variable_history(self, var_name: str) -> List[Any]:
        """Extracts history timeline for a specific variable."""
        history = []
        for step in self.steps:
            if var_name in step["variables"]:
                val = step["variables"][var_name]
                if not history or history[-1] != val:
                    history.append(val)
        return history
