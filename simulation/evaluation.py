from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


SimulationVisualizer = None

class SimulationEvaluator:
    """Class for evaluating simulation results."""
    
    def __init__(self):
        """Initialize a simulation evaluator."""
        pass

    def _values_match(self, actual_val, gt_val):
        """Compare two values with type coercion."""
        # Handle lists
        if isinstance(actual_val, list) and isinstance(gt_val, list):
            if len(actual_val) != len(gt_val):
                return False
            return all(self._values_match(a, g) for a, g in zip(actual_val, gt_val))
        
        # Handle dicts
        if isinstance(actual_val, dict) and isinstance(gt_val, dict):
            return self._params_match(actual_val, gt_val)
        
        # Handle None/null variations
        if actual_val is None or gt_val is None:
            return (actual_val is None and str(gt_val).lower() in ["none", "null"]) or \
                   (gt_val is None and str(actual_val).lower() in ["none", "null"]) or \
                   (actual_val is None and gt_val is None)
        
        # Handle boolean variations
        if isinstance(actual_val, bool) or isinstance(gt_val, bool):
            return str(actual_val).lower() == str(gt_val).lower()
        
        # Try numeric comparison
        try:
            # Handle scientific notation and precision
            return abs(float(str(gt_val)) - float(str(actual_val))) < 1e-10
        except (ValueError, TypeError):
            pass
        
        # Fall back to string comparison (strip whitespace)
        return str(actual_val).strip() == str(gt_val).strip()

    def _params_match(self, actual_params, gt_params):
        """Compare parameters with type coercion for numeric values."""
        # Handle DEFAULT parameter case
        if "DEFAULT" in gt_params and len(gt_params) == 1:
            if len(actual_params) == 1:
                gt_val = gt_params["DEFAULT"]
                actual_val = list(actual_params.values())[0]
                return self._values_match(actual_val, gt_val)
        
        if len(actual_params) != len(gt_params):
            return False
        
        for key, gt_val in gt_params.items():
            if key not in actual_params:
                return False
            
            if not self._values_match(actual_params[key], gt_val):
                return False
                
        return True

    def _extract_final_planned_calls(self, attempts: List[Dict]) -> List[Dict]:
        """Extract the final planned state of each unique tool call."""
        tool_call_map = {}
        
        for attempt in attempts:
            tool_call = attempt.get("tool_call", {})
            tool_name = tool_call.get("tool_name", "")
            arguments = tool_call.get("arguments", {})
            
            # Create a signature based on tool name and arguments structure
            # We use argument keys to identify the "same" tool call across attempts
            arg_keys = sorted(arguments.keys())
            signature = f"{tool_name}:{arg_keys}"
            
            # Keep the latest version of each unique tool call
            # Later attempts in the list will overwrite earlier ones
            tool_call_map[signature] = tool_call
        
        return list(tool_call_map.values())
    
    # def _extract_final_planned_calls(self, attempts: List[Dict]) -> List[Dict]:
    #     """
    #     Extract the final planned state of each unique tool call.
        
    #     Strategy:
    #     1. Group attempts by tool name and argument structure
    #     2. For each group, take the latest attempt that was planned to be executed
    #     3. Return the tool call from that attempt
    #     """
    #     # Group attempts by tool signature
    #     tool_groups = {}
        
    #     for i, attempt in enumerate(attempts):
    #         tool_call = attempt.get("tool_call", {})
    #         tool_name = tool_call.get("tool_name", "")
    #         arguments = tool_call.get("arguments", {})
            
    #         # Create a more specific signature that considers both tool name and argument keys
    #         # This helps distinguish between different calls to the same tool
    #         arg_keys = tuple(sorted(arguments.keys()))
    #         signature = (tool_name, arg_keys)
            
    #         # Store attempt with its index for ordering
    #         if signature not in tool_groups:
    #             tool_groups[signature] = []
    #         tool_groups[signature].append((i, attempt))
        
    #     # For each group, get the latest planned tool call
    #     final_tool_calls = []
    #     for signature, group_attempts in tool_groups.items():
    #         # Sort by index to get chronological order
    #         group_attempts.sort(key=lambda x: x[0])
            
    #         # Take the latest attempt (highest index)
    #         latest_attempt = group_attempts[-1][1]
    #         tool_call = latest_attempt.get("tool_call", {})
            
    #         # Only include if it's a valid tool call
    #         if tool_call.get("tool_name"):
    #             final_tool_calls.append(tool_call)
        
    #     return final_tool_calls

    def _extract_executed_calls(self, attempts: List[Dict]) -> List[Dict]:
        """Extract only tool calls that were actually executed."""
        return [
            a["tool_call"] for a in attempts 
            if a.get("was_executed", False)
        ]

    def _extract_successful_executions(self, attempts: List[Dict]) -> List[Dict]:
        """Extract only tool calls that executed successfully."""
        return [
            a for a in attempts 
            if a.get("was_executed", False) and a.get("success", False)
        ]

    def _calculate_execution_metrics(self, attempts: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics about execution attempts."""
        if not attempts:
            return {
                "total_attempts": 0,
                "executed_attempts": 0,
                "successful_attempts": 0,
                "duplicate_attempts": 0,
                "execution_rate": 0.0,
                "success_rate": 0.0,
                "execution_success": False
            }
        
        total_attempts = len(attempts)
        executed_attempts = len([a for a in attempts if a.get("was_executed")])
        successful_attempts = len([a for a in attempts if a.get("success")])
        duplicate_attempts = len([a for a in attempts if a.get("reason") == "duplicate"])
        failed_attempts = len([a for a in attempts if a.get("was_executed") and not a.get("success")])
        
        # Calculate rates
        execution_rate = executed_attempts / total_attempts if total_attempts > 0 else 0.0
        success_rate = successful_attempts / executed_attempts if executed_attempts > 0 else 0.0
        
        # Overall execution success means at least one tool was executed successfully
        # and no executed tools failed
        execution_success = successful_attempts > 0 and failed_attempts == 0
        
        return {
            "total_attempts": total_attempts,
            "executed_attempts": executed_attempts,
            "successful_attempts": successful_attempts,
            "failed_attempts": failed_attempts,
            "duplicate_attempts": duplicate_attempts,
            "execution_rate": execution_rate,
            "success_rate": success_rate,
            "execution_success": execution_success,
            "attempt_breakdown": {
                "new_executions": len([a for a in attempts if a.get("reason") == "new tool call" and a.get("was_executed")]),
                "clarification_executions": len([a for a in attempts if a.get("reason") == "new tool call after clarification" and a.get("was_executed")]),
                "skipped_duplicates": duplicate_attempts,
                "validation_failures": len([a for a in attempts if not a.get("was_executed") and a.get("reason") != "duplicate"])
            }
        }
    
    def evaluate_simulation(
        self,
        simulation_data: Dict[str, Any],
        simulation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a simulation run using ONLY tool call attempts.
        
        Args:
            simulation_data: Original simulation data
            simulation_result: Result of the simulation
            
        Returns:
            Evaluation metrics
        """
        metrics = {}
        
        # Extract ground truth
        ground_truth = simulation_data.get("ground_truth_tool_calls", [])
        
        # Check if ground truth has turn information
        has_turn_info = any("turn" in tc for tc in ground_truth)
        
        # For backward compatibility, if no turn info is present, assume all are from turn 1
        if not has_turn_info:
            ground_truth = [{"turn": 1, **tc} for tc in ground_truth]
        
        # Extract data from tool call attempts - THIS IS THE ONLY SOURCE
        all_tool_call_attempts = simulation_result.get("all_tool_call_attempts", [])
        final_tool_calls = simulation_result.get("final_tool_calls", [])
        
        # Extract conversation and questions
        conversation = simulation_result.get("conversation", [])
        questions = simulation_result.get("questions", [])
        all_candidate_questions = simulation_result.get("all_candidate_questions", [])
        
        # Calculate ALL metrics directly from attempts
        attempt_metrics = self._calculate_attempt_based_metrics(all_tool_call_attempts, ground_truth, final_tool_calls)
        conversation_metrics = self._calculate_conversation_metrics(conversation)

        # Combine all metrics
        metrics.update(attempt_metrics)
        metrics["conversation"] = conversation_metrics

        return metrics
    def _calculate_validity_metrics(
        self,
        final_tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate validity metrics - whether tool calls are executable.
        
        Args:
            final_tool_calls: Final tool calls from the simulation
            
        Returns:
            Validity metrics
        """
        metrics = {}
        
        valid_count = 0
        total_count = len(final_tool_calls)
        
        for tc in final_tool_calls:
            # Check if tool has all required parameters (not <UNK>)
            is_valid = True
            arguments = tc.get("arguments", tc.get("parameters", {}))
            
            # For this simulation, we consider a tool call valid if it doesn't have <UNK> values
            for param, value in arguments.items():
                if value == "<UNK>":
                    is_valid = False
                    break
            
            if is_valid:
                valid_count += 1
        
        metrics["total_tool_calls"] = total_count
        metrics["valid_tool_calls"] = valid_count
        metrics["validity_rate"] = valid_count / total_count if total_count > 0 else 0.0
        metrics["all_valid"] = valid_count == total_count
        
        return metrics
    
    def _calculate_correctness_metrics_for_final_calls(
        self,
        ground_truth: List[Dict[str, Any]],
        final_tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate correctness metrics for final tool calls - whether tool calls match ground truth.
        
        Args:
            ground_truth: Ground truth tool calls (with turn information)
            final_tool_calls: Final tool calls from the simulation
            
        Returns:
            Correctness metrics for final calls
        """
        if not ground_truth:
            return {
                "exact_match": False,
                "tool_match_rate": 0.0,
                "param_match_rate": 0.0,
                "tools_fully_matched_rate": 0.0
            }
            
        # Create sets of tool names for comparison
        gt_tool_names = {tc.get("tool_name") for tc in ground_truth}
        actual_tool_names = {tc.get("name", tc.get("tool_name")) for tc in final_tool_calls}
        
        # Calculate tool match rate
        if not gt_tool_names:
            tool_match_rate = 0.0
        else:
            # Calculate intersection
            matching_tools = gt_tool_names.intersection(actual_tool_names)
            tool_match_rate = len(matching_tools) / len(gt_tool_names)
        
        # Calculate parameter match rate
        total_params = 0
        matching_params = 0
        
        for gt_tc in ground_truth:
            gt_tool_name = gt_tc.get("tool_name")
            gt_params = gt_tc.get("parameters", {})
            
            # Find matching tool call
            matching_tc = None
            for tc in final_tool_calls:
                if tc.get("name", tc.get("tool_name")) == gt_tool_name:
                    matching_tc = tc
                    break
            
            if matching_tc:
                actual_params = matching_tc.get("args", matching_tc.get("arguments", matching_tc.get("parameters", {})))
                
                # Count parameters
                for param_name, gt_value in gt_params.items():
                    total_params += 1
                    
                    if param_name in actual_params:
                        actual_val = actual_params[param_name]
                        if self._values_match(actual_val, gt_value):
                            matching_params += 1
                        # Check if one is a single-element list containing the other
                        elif (isinstance(actual_val, list) and len(actual_val) == 1 and actual_val[0] == gt_value) or \
                            (isinstance(gt_value, list) and len(gt_value) == 1 and gt_value[0] == actual_val):
                            # Single-element list matches the other value
                            matching_params += 1

        
        param_match_rate = matching_params / total_params if total_params > 0 else 0.0
        

        # Check for exact match of tool calls (success)
        exact_match = self._check_exact_match(ground_truth, final_tool_calls)
        
        return {
            "exact_match": exact_match,
            "tool_match_rate": tool_match_rate,
            "param_match_rate": param_match_rate,
            "tools_fully_matched_rate": 1.0 if tool_match_rate == 1.0 else 0.0
        }

    def _calculate_correctness_metrics_for_all_attempts(
        self,
        ground_truth: List[Dict[str, Any]],
        all_attempts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate correctness metrics for ALL attempts (not just successful ones).
        
        Args:
            ground_truth: Ground truth tool calls
            all_attempts: All tool call attempts (successful and failed)
            
        Returns:
            Correctness metrics for all attempts
        """
        if not ground_truth:
            return {
                "exact_match": False,
                "tool_match_rate": 0.0,
                "param_match_rate": 0.0,
                "tools_fully_matched_rate": 0.0
            }
        
        # Convert all attempts to comparable format
        actual_calls = []
        for attempt in all_attempts:
            tool_call = attempt.get("tool_call", {})
            call_signature = {
                "tool_name": tool_call.get("name", tool_call.get("tool_name", "")),
                "parameters": tool_call.get("args", tool_call.get("arguments", {}))
            }
            actual_calls.append(call_signature)
        
        # Create sets of tool names for comparison
        gt_tool_names = {tc.get("tool_name") for tc in ground_truth}
        actual_tool_names = {tc.get("tool_name") for tc in actual_calls}
        
        # Calculate tool match rate
        if not gt_tool_names:
            tool_match_rate = 0.0
        else:
            # Calculate intersection
            matching_tools = gt_tool_names.intersection(actual_tool_names)
            tool_match_rate = len(matching_tools) / len(gt_tool_names)
        
        # Calculate parameter match rate
        total_params = 0
        matching_params = 0
        
        for gt_tc in ground_truth:
            gt_tool_name = gt_tc.get("tool_name")
            gt_params = gt_tc.get("parameters", {})
            
            # Find matching tool call
            matching_tc = None
            for tc in actual_calls:
                if tc.get("tool_name") == gt_tool_name:
                    matching_tc = tc
                    break
            
            if matching_tc:
                actual_params = matching_tc.get("parameters", {})
                
                # Count parameters
                for param_name, gt_value in gt_params.items():
                    total_params += 1
                    
                    if param_name in actual_params:
                        actual_val = actual_params[param_name]
                        if self._values_match(actual_val, gt_value):
                            matching_params += 1
                        # Check if one is a single-element list containing the other
                        elif (isinstance(actual_val, list) and len(actual_val) == 1 and actual_val[0] == gt_value) or \
                            (isinstance(gt_value, list) and len(gt_value) == 1 and gt_value[0] == actual_val):
                            # Single-element list matches the other value
                            matching_params += 1

        
        param_match_rate = matching_params / total_params if total_params > 0 else 0.0
        
        # Check for exact match - need to compare against actual_calls format
        exact_match = self._check_exact_match_for_attempts(ground_truth, actual_calls)
        
        return {
            "exact_match": exact_match,
            "tool_match_rate": tool_match_rate,
            "param_match_rate": param_match_rate,
            "tools_fully_matched_rate": 1.0 if tool_match_rate == 1.0 else 0.0
        }

    def _check_exact_match_for_attempts(
        self,
        ground_truth: List[Dict[str, Any]],
        actual_calls: List[Dict[str, Any]]
    ) -> bool:
        """Check if there's an exact match between ground truth and actual calls from attempts."""
        if len(ground_truth) != len(actual_calls):
            return False
            
        # Check each tool call
        for gt_tc in ground_truth:
            gt_tool_name = gt_tc.get("tool_name")
            gt_params = gt_tc.get("parameters", {})
            
            # Find matching tool call
            matching_tc = None
            for tc in actual_calls:
                if tc.get("tool_name") == gt_tool_name:
                    matching_tc = tc
                    break
            
            if not matching_tc:
                return False
                
            # Compare parameters
            actual_params = matching_tc.get("parameters", {})
            
            # Check for missing or extra parameters
            if set(gt_params.keys()) != set(actual_params.keys()):
                return False
                
            # Check parameter values
            for param_name, gt_value in gt_params.items():
                if param_name not in actual_params or actual_params[param_name] != gt_value:
                    return False
        
        return True

    def _check_exact_match(
        self,
        ground_truth: List[Dict[str, Any]],
        final_tool_calls: List[Dict[str, Any]]
    ) -> bool:
        """Check if there's an exact match between ground truth and final tool calls."""
        if len(ground_truth) != len(final_tool_calls):
            return False
            
        # Check each tool call
        for gt_tc in ground_truth:
            gt_tool_name = gt_tc.get("tool_name")
            gt_params = gt_tc.get("parameters", {})
            
            # Find matching tool call
            matching_tc = None
            for tc in final_tool_calls:
                if tc.get("name", tc.get("tool_name")) == gt_tool_name:
                    matching_tc = tc
                    break
            
            if not matching_tc:
                return False
                
            # Compare parameters
            actual_params = matching_tc.get("args", matching_tc.get("arguments", matching_tc.get("parameters", {})))
            
            # Check for missing or extra parameters
            if set(gt_params.keys()) != set(actual_params.keys()):
                return False
                
            # Check parameter values
            for param_name, gt_value in gt_params.items():
                if param_name not in actual_params or actual_params[param_name] != gt_value:
                    return False
        
        return True
    
    def _calculate_conversation_metrics(
        self,
        conversation: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate metrics for the conversation - excluding automated messages.
        
        Args:
            conversation: List of conversation turns
            
        Returns:
            Conversation metrics
        """
        metrics = {}
        
        # Only count human-relevant turns - exclude execution and confirmation messages
        human_relevant_turns = []
        for turn in conversation:
            if turn.get("type") not in ["execution", "execution_result", "confirmation", "execution_retry", "execution_error"]:
                human_relevant_turns.append(turn)
        
        metrics["total_turns"] = len(human_relevant_turns)
        
        # Count user turns
        user_turns = [turn for turn in human_relevant_turns if turn.get("role") == "user"]
        metrics["user_turns"] = len(user_turns)
        
        # Count agent turns (excluding automated)
        agent_turns = [turn for turn in human_relevant_turns if turn.get("role") == "agent"]
        metrics["agent_turns"] = len(agent_turns)
        
        # Count clarification questions
        clarification_turns = [
            turn for turn in human_relevant_turns 
            if turn.get("role") == "agent" and turn.get("type") == "clarification"
        ]
        metrics["clarification_questions"] = len(clarification_turns)
        
        # Count follow-up requests
        follow_up_turns = [
            turn for turn in human_relevant_turns 
            if turn.get("role") == "user" and turn.get("type") == "follow_up"
        ]
        metrics["follow_up_requests"] = len(follow_up_turns)
        
        return metrics
    
    def _calculate_question_metrics(
        self,
        questions: List[Dict[str, Any]],
        all_candidate_questions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate metrics for the questions.

        Args:
            questions: List of questions with metrics
            all_candidate_questions: List of all candidate questions (including rejected ones)

        Returns:
            Question metrics (removed for baseline - not applicable)
        """
        # Question metrics removed - not applicable for baseline agent
        return {}
    
    def _calculate_state_based_success(
        self,
        simulation_data: Dict[str, Any],
        successful_attempts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate state-based success by comparing final states.
        
        Applies GT tool calls and actual tool calls to initial config,
        then compares the resulting states.
        
        Args:
            simulation_data: Original simulation data with initial_config and ground_truth
            successful_attempts: List of successful tool call attempts
            
        Returns:
            State-based success metrics
        """
        try:
            # Extract initial config and ground truth
            initial_config = simulation_data.get("initial_config", {})
            ground_truth = simulation_data.get("ground_truth_tool_calls", [])
            
            if not initial_config or not ground_truth:
                return {
                    "state_based_success": False,
                    "error": "Missing initial_config or ground_truth"
                }
            
            # Get the plugin to simulate state changes
            # For now, we'll do a simple comparison assuming the plugin can simulate
            # In a full implementation, we'd need to actually execute the tool calls
            
            # Extract successful tool calls in the right format
            actual_tool_calls = []
            for attempt in successful_attempts:
                tool_call = attempt.get("tool_call", {})
                # Convert to ground truth format for comparison
                converted_call = {
                    "tool_name": tool_call.get("name", tool_call.get("tool_name", "")),
                    "parameters": tool_call.get("args", tool_call.get("arguments", {}))
                }
                actual_tool_calls.append(converted_call)
            
            # For now, do a simplified comparison
            # In a full implementation, we'd simulate both sequences and compare states
            state_match = self._compare_tool_sequences(ground_truth, actual_tool_calls)
            
            return {
                "state_based_success": state_match,
                "gt_tool_count": len(ground_truth),
                "actual_tool_count": len(actual_tool_calls),
                "sequences_identical": ground_truth == actual_tool_calls
            }
            
        except Exception as e:
            return {
                "state_based_success": False,
                "error": f"State comparison failed: {str(e)}"
            }
    
    def _calculate_coverage_success(
        self,
        ground_truth: List[Dict[str, Any]],
        successful_attempts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate coverage success - whether all GT tool calls exist in final results.
        
        Args:
            ground_truth: Ground truth tool calls
            successful_attempts: List of successful tool call attempts
            
        Returns:
            Coverage success metrics
        """
        if not ground_truth:
            return {
                "coverage_success": True,
                "coverage_rate": 1.0,
                "missing_calls": [],
                "covered_calls": []
            }
        
        # Convert successful attempts to comparable format
        actual_calls = []
        for attempt in successful_attempts:
            tool_call = attempt.get("tool_call", {})
            call_signature = {
                "tool_name": tool_call.get("name", tool_call.get("tool_name", "")),
                "parameters": tool_call.get("args", tool_call.get("arguments", {}))
            }
            actual_calls.append(call_signature)
        
        # Check coverage for each GT call
        covered_calls = []
        missing_calls = []
        
        for gt_call in ground_truth:
            gt_tool_name = gt_call.get("tool_name", "")
            gt_params = gt_call.get("parameters", {})
            
            # Look for exact match in actual calls
            found_match = False
            for actual_call in actual_calls:
                if (actual_call.get("tool_name") == gt_tool_name and 
                    self._params_match(actual_call.get("parameters", {}), gt_params)):
                    found_match = True
                    break
            
            if found_match:
                covered_calls.append(gt_call)
            else:
                missing_calls.append(gt_call)
        
        coverage_rate = len(covered_calls) / len(ground_truth) if ground_truth else 1.0
        coverage_success = len(missing_calls) == 0
        
        return {
            "coverage_success": coverage_success,
            "coverage_rate": coverage_rate,
            "covered_calls": covered_calls,
            "missing_calls": missing_calls,
            "total_gt_calls": len(ground_truth),
            "covered_count": len(covered_calls),
            "missing_count": len(missing_calls)
        }
    
    def _calculate_coverage_success_for_final_calls(
        self,
        ground_truth: List[Dict[str, Any]],
        final_tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate coverage success for final tool calls (planned calls).

        Args:
            ground_truth: Ground truth tool calls
            final_tool_calls: Final planned tool calls

        Returns:
            Coverage success metrics for final calls
        """
        if not ground_truth:
            return {
                "coverage_success": True,
                "coverage_rate": 1.0,
                "total_gt_calls": 0,
                "covered_count": 0,
                "missing_count": 0
            }

        # Convert final calls to comparable format
        actual_calls = []
        for call in final_tool_calls:
            call_signature = {
                "tool_name": call.get("name", call.get("tool_name", "")),
                "parameters": call.get("args", call.get("arguments", call.get("parameters", {})))
            }
            actual_calls.append(call_signature)

        # Check coverage for each GT call
        covered_count = 0

        for gt_call in ground_truth:
            gt_tool_name = gt_call.get("tool_name", "")
            gt_params = gt_call.get("parameters", {})

            # Look for exact match in actual calls
            found_match = False
            for actual_call in actual_calls:
                if (actual_call.get("tool_name") == gt_tool_name and
                    self._params_match(actual_call.get("parameters", {}), gt_params)):
                    found_match = True
                    break

            if found_match:
                covered_count += 1

        missing_count = len(ground_truth) - covered_count
        coverage_rate = covered_count / len(ground_truth) if ground_truth else 1.0
        coverage_success = missing_count == 0

        return {
            "coverage_success": coverage_success,
            "coverage_rate": coverage_rate,
            "total_gt_calls": len(ground_truth),
            "covered_count": covered_count,
            "missing_count": missing_count
        }
    
    def _calculate_coverage_success_for_all_attempts(
        self,
        ground_truth: List[Dict[str, Any]],
        all_attempts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate coverage success for ALL attempts (not just successful ones).
        
        Args:
            ground_truth: Ground truth tool calls
            all_attempts: All tool call attempts (successful and failed)
            
        Returns:
            Coverage success metrics for all attempts
        """
        if not ground_truth:
            return {
                "coverage_success": True,
                "coverage_rate": 1.0,
                "missing_calls": [],
                "covered_calls": []
            }
        
        # Convert all attempts to comparable format
        actual_calls = []
        for attempt in all_attempts:
            tool_call = attempt.get("tool_call", {})
            call_signature = {
                "tool_name": tool_call.get("name", tool_call.get("tool_name", "")),
                "parameters": tool_call.get("args", tool_call.get("arguments", {}))
            }
            actual_calls.append(call_signature)
        
        # Check coverage for each GT call
        covered_calls = []
        missing_calls = []
        
        for gt_call in ground_truth:
            gt_tool_name = gt_call.get("tool_name", "")
            gt_params = gt_call.get("parameters", {})
            
            # Look for exact match in actual calls
            found_match = False
            for actual_call in actual_calls:
                if (actual_call.get("tool_name") == gt_tool_name and 
                    self._params_match(actual_call.get("parameters", {}), gt_params)):
                    found_match = True
                    break
            
            if found_match:
                covered_calls.append(gt_call)
            else:
                missing_calls.append(gt_call)
        
        coverage_rate = len(covered_calls) / len(ground_truth) if ground_truth else 1.0
        coverage_success = len(missing_calls) == 0
        
        return {
            "coverage_success": coverage_success,
            "coverage_rate": coverage_rate,
            "covered_calls": covered_calls,
            "missing_calls": missing_calls,
            "total_gt_calls": len(ground_truth),
            "covered_count": len(covered_calls),
            "missing_count": len(missing_calls)
        }
    
    def _compare_tool_sequences(
        self,
        gt_sequence: List[Dict[str, Any]],
        actual_sequence: List[Dict[str, Any]]
    ) -> bool:
        """
        Compare two tool call sequences for equivalence.
        
        This is a simplified comparison - in a full implementation,
        we'd simulate the actual state changes.
        
        Args:
            gt_sequence: Ground truth tool call sequence
            actual_sequence: Actual tool call sequence
            
        Returns:
            True if sequences are equivalent
        """
        # Simple approach: check if sequences are identical
        if len(gt_sequence) != len(actual_sequence):
            return False
        
        # Sort both sequences by tool name and parameters for comparison
        # This handles cases where order doesn't matter
        def sort_key(call):
            tool_name = call.get("tool_name", "")
            params = call.get("parameters", {})
            # Create a sortable string representation
            param_str = str(sorted(params.items())) if params else ""
            return f"{tool_name}:{param_str}"
        
        sorted_gt = sorted(gt_sequence, key=sort_key)
        sorted_actual = sorted(actual_sequence, key=sort_key)
        
        return sorted_gt == sorted_actual
    
    def _calculate_attempt_based_metrics(
        self, 
        attempts: List[Dict[str, Any]], 
        ground_truth: List[Dict[str, Any]],
        final_tool_calls: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate all metrics directly from tool call attempts.
        """
        if not attempts:
            return {
                "execution": {"total_attempts": 0, "execution_success": False},
                "validity": {"all_valid": False, "validity_rate": 0.0},
                "correctness": {"exact_match": False, "tool_match_rate": 0.0},
                "success": False
            }
        
        # 1. EXECUTION METRICS - what actually happened
        executed_attempts = [a for a in attempts if a.get("was_executed")]
        successful_attempts = [a for a in attempts if a.get("success")]
        duplicate_attempts = [a for a in attempts if a.get("reason") == "duplicate"]
        
        execution_metrics = {
            "total_attempts": len(attempts),
            "executed_attempts": len(executed_attempts),
            "successful_attempts": len(successful_attempts),
            "duplicate_attempts": len(duplicate_attempts),
            "execution_rate": len(executed_attempts) / len(attempts),
            "success_rate": len(successful_attempts) / len(executed_attempts) if executed_attempts else 0.0,
            "execution_success": len(successful_attempts) > 0 and len(executed_attempts) == len(successful_attempts)
        }
        
        
        # 3. CORRECTNESS METRICS - do the final calls match ground truth?
        # Only calculate correctness for final calls (not all attempts)
        correctness_final = self._calculate_correctness_metrics_for_final_calls(ground_truth, final_tool_calls or [])

        # Use final call correctness metrics directly
        correctness_metrics = {
            "exact_match": correctness_final.get("exact_match", False),
            "tool_match_rate": correctness_final.get("tool_match_rate", 0.0),
            "param_match_rate": correctness_final.get("param_match_rate", 0.0),
            "tools_fully_matched_rate": correctness_final.get("tools_fully_matched_rate", 0.0)
        }
        
        # 4. NEW SUCCESS METRICS
        # Skip state-based success for now as it's not implemented
        # state_metrics = {
        #     "state_based_success": False,
        #     "note": "State-based comparison not implemented yet"
        # }
        
        # Coverage success - only calculate for final calls
        coverage_final = self._calculate_coverage_success_for_final_calls(ground_truth, final_tool_calls or [])

        # Use final call coverage metrics directly
        coverage_metrics = {
            "coverage_success": coverage_final.get("coverage_success", False),
            "coverage_rate": coverage_final.get("coverage_rate", 0.0),
            "total_gt_calls": coverage_final.get("total_gt_calls", 0),
            "covered_count": coverage_final.get("covered_count", 0),
            "missing_count": coverage_final.get("missing_count", 0)
        }
        
        # Overall success: correctness + execution
        success = (
            correctness_metrics["exact_match"] and
            execution_metrics["execution_success"]
        )

        return {
            "execution": execution_metrics,
            "correctness": correctness_metrics,
            "coverage": coverage_metrics,
            "success": success
        }
    
    """Class for visualizing simulation results."""
    
    def __init__(self):
        """Initialize a simulation visualizer."""
        pass
    
    def visualize_conversation(
        self,
        conversation: List[Dict[str, Any]]
    ) -> str:
        """
        Visualize the conversation in a pretty format.
        
        Args:
            conversation: List of conversation turns
            
        Returns:
            Formatted conversation string
        """
        if not conversation:
            return "No conversation recorded."
            
        lines = []
        
        for i, turn in enumerate(conversation):
            role = turn.get("role", "unknown")
            message = turn.get("message", "")
            turn_type = turn.get("type", "")
            
            if role == "user":
                prefix = "User"
                if turn_type == "initial":
                    prefix = "User (initial)"
                elif turn_type == "follow_up":
                    prefix = "User (follow-up)"
                elif turn_type == "clarification_response":
                    prefix = "User (clarification)"
                    
                lines.append(f"\n{prefix}: {message}")
                
            elif role == "agent":
                prefix = "Agent"
                if turn_type:
                    prefix = f"Agent ({turn_type})"
                lines.append(f"\n{prefix}: {message}")
                
            else:
                lines.append(f"\n{role}: {message}")
        
        return "\n".join(lines)
    
    def visualize_questions(
        self,
        questions: List[Dict[str, Any]],
        all_candidate_questions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Visualize the questions and their metrics.
        
        Args:
            questions: List of questions with metrics
            all_candidate_questions: List of all candidate questions
            
        Returns:
            Formatted questions string
        """
        if not questions and not all_candidate_questions:
            return "No questions asked."
            
        lines = ["Questions and Metrics:"]
        
        if all_candidate_questions:
            lines.append(f"\nTotal candidate questions: {len(all_candidate_questions)}")
            lines.append(f"Total selected questions: {len(questions)}")
            lines.append(f"Selection rate: {len(questions)/len(all_candidate_questions):.2f} if all_candidate_questions else 'N/A'")
            
            # Display selected questions
            if questions:
                lines.append("\nSelected Questions:")
                for i, q in enumerate(questions):
                    question_text = q.get("question_text", "")
                    target_args = q.get("target_args", [])
                    metrics = q.get("metrics", {})
                    
                    # Format target arguments
                    target_args_str = ", ".join([f"{tool}.{arg}" for tool, arg in target_args])
                    
                    # Format metrics
                    evpi = metrics.get("evpi", 0.0)
                    regret_reduction = metrics.get("regret_reduction", 0.0)
                    ucb_score = metrics.get("ucb_score", 0.0)
                    
                    lines.append(f"\nQuestion {i+1}: {question_text}")
                    lines.append(f"Target Arguments: {target_args_str}")
                    lines.append(f"Metrics: EVPI={evpi:.4f}, Regret Reduction={regret_reduction:.4f}, UCB Score={ucb_score:.4f}")
        else:
            # Legacy format with only selected questions
            for i, q in enumerate(questions):
                question_text = q.get("question_text", "")
                target_args = q.get("target_args", [])
                metrics = q.get("metrics", {})
                
                # Format target arguments
                target_args_str = ", ".join([f"{tool}.{arg}" for tool, arg in target_args])
                
                # Format metrics
                evpi = metrics.get("evpi", 0.0)
                regret_reduction = metrics.get("regret_reduction", 0.0)
                ucb_score = metrics.get("ucb_score", 0.0)
                
                lines.append(f"\nQuestion {i+1}: {question_text}")
                lines.append(f"Target Arguments: {target_args_str}")
                lines.append(f"Metrics: EVPI={evpi:.4f}, Regret Reduction={regret_reduction:.4f}, UCB Score={ucb_score:.4f}")
        
        return "\n".join(lines)
    
    def visualize_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        title: str = "Tool Calls",
        all_tool_call_attempts: List[Dict[str, Any]] = None
    ) -> str:
        """
        Visualize tool calls in a pretty format.
        
        Args:
            tool_calls: List of tool calls
            title: Title for the visualization
            all_tool_call_attempts: List of all tool call attempts (successful and failed)
            
        Returns:
            Formatted tool calls string
        """
        lines = []
        
        if all_tool_call_attempts:
            lines.append(f"All Tool Call Attempts: {len(all_tool_call_attempts)}")
            successful_attempts = sum(1 for a in all_tool_call_attempts if a.get("was_executed", False) and a.get("success", False))
            lines.append(f"Successful Attempts: {successful_attempts}")
            lines.append(f"Failed Attempts: {sum(1 for a in all_tool_call_attempts if a.get('was_executed', False) and not a.get('success', False))}")
            lines.append(f"Skipped Attempts: {sum(1 for a in all_tool_call_attempts if not a.get('was_executed', False))}")
            
            # Add detailed visualization of attempts if desired
            # (omitted for brevity)
            
        if not tool_calls:
            lines.append(f"\n{title}: None")
            return "\n".join(lines)
            
        lines.append(f"\n{title}:")
        
        for i, tc in enumerate(tool_calls):
            tool_name = tc.get("tool_name", "")
            arguments = tc.get("arguments", tc.get("parameters", {}))
            
            # Format parameters
            params_str = ", ".join([f"{k}={v}" for k, v in arguments.items()])
            
            lines.append(f"\n{i+1}. {tool_name}({params_str})")
        
        return "\n".join(lines)
    
    def visualize_metrics(
        self,
        metrics: Dict[str, Any]
    ) -> str:
        """
        Visualize evaluation metrics in a pretty format.
        
        Args:
            metrics: Evaluation metrics
            
        Returns:
            Formatted metrics string
        """
        validity = metrics.get("validity", {})
        correctness = metrics.get("correctness", {})
        conversation = metrics.get("conversation", {})
        questions = metrics.get("questions", {})
        
        lines = ["Evaluation Metrics:"]
        
        # Validity metrics
        lines.append("\nValidity Metrics:")
        lines.append(f"- Total Tool Calls: {validity.get('total_tool_calls', 0)}")
        lines.append(f"- Valid Tool Calls: {validity.get('valid_tool_calls', 0)}")
        lines.append(f"- Validity Rate: {validity.get('validity_rate', 0.0):.2f}")
        lines.append(f"- All Valid: {'Yes' if validity.get('all_valid', False) else 'No'}")
        
        # Correctness metrics - updated for new structure
        lines.append("\nCorrectness Metrics:")
        
        # Check if we have the new structure with attempts and final_calls
        if isinstance(correctness.get("attempts"), dict) or isinstance(correctness.get("final_calls"), dict):
            # New structure
            correctness_attempts = correctness.get("attempts", {})
            correctness_final = correctness.get("final_calls", {})
            
            lines.append(f"- Overall Exact Match: {'Yes' if correctness.get('exact_match', False) else 'No'}")
            lines.append(f"- Overall Tool Match Rate: {correctness.get('tool_match_rate', 0.0):.2f}")
            lines.append(f"- Overall Parameter Match Rate: {correctness.get('param_match_rate', 0.0):.2f}")
            
            lines.append(f"\nCorrectness from All Attempts:")
            lines.append(f"- Exact Match: {'Yes' if correctness_attempts.get('exact_match', False) else 'No'}")
            lines.append(f"- Tool Match Rate: {correctness_attempts.get('tool_match_rate', 0.0):.2f}")
            lines.append(f"- Parameter Match Rate: {correctness_attempts.get('param_match_rate', 0.0):.2f}")
            
            lines.append(f"\nCorrectness from Final Planned Calls:")
            lines.append(f"- Exact Match: {'Yes' if correctness_final.get('exact_match', False) else 'No'}")
            lines.append(f"- Tool Match Rate: {correctness_final.get('tool_match_rate', 0.0):.2f}")
            lines.append(f"- Parameter Match Rate: {correctness_final.get('param_match_rate', 0.0):.2f}")
        else:
            # Legacy structure
            lines.append(f"- Exact Match: {'Yes' if correctness.get('exact_match', False) else 'No'}")
            lines.append(f"- Tool Match Rate: {correctness.get('tool_match_rate', 0.0):.2f}")
            lines.append(f"- Parameter Match Rate: {correctness.get('param_match_rate', 0.0):.2f}")
        
        # New success metrics
        state_based = metrics.get("state_based", {})
        coverage = metrics.get("coverage", {})
        
        lines.append("\nNew Success Metrics:")
        lines.append(f"- Coverage Success (Overall): {'Yes' if metrics.get('coverage_success', False) else 'No'}")
        
        # Coverage details for attempts
        coverage_attempts = coverage.get("attempts", {})
        lines.append(f"\nCoverage from All Attempts:")
        lines.append(f"- Coverage Rate: {coverage_attempts.get('coverage_rate', 0.0):.2f}")
        lines.append(f"- Coverage Success: {'Yes' if coverage_attempts.get('coverage_success', False) else 'No'}")
        lines.append(f"- Missing GT Calls: {coverage_attempts.get('missing_count', 0)}/{coverage_attempts.get('total_gt_calls', 0)}")
        
        # Coverage details for final calls
        coverage_final = coverage.get("final_calls", {})
        lines.append(f"\nCoverage from Final Planned Calls:")
        lines.append(f"- Coverage Rate: {coverage_final.get('coverage_rate', 0.0):.2f}")
        lines.append(f"- Coverage Success: {'Yes' if coverage_final.get('coverage_success', False) else 'No'}")
        lines.append(f"- Missing GT Calls: {coverage_final.get('missing_count', 0)}/{coverage_final.get('total_gt_calls', 0)}")
        
        # Overall success
        lines.append(f"\nSuccess Summary:")
        lines.append(f"- Traditional Success: {'Yes' if metrics.get('success', False) else 'No'}")
        lines.append(f"- Coverage Success: {'Yes' if metrics.get('coverage_success', False) else 'No'}")
        lines.append(f"- Any Success: {'Yes' if metrics.get('any_success', False) else 'No'}")
        
        # Conversation metrics
        lines.append(f"\nConversation Metrics:")
        lines.append(f"- Total Turns (Human-Relevant): {conversation.get('total_turns', 0)}")
        lines.append(f"- User Turns: {conversation.get('user_turns', 0)}")
        lines.append(f"- Agent Turns: {conversation.get('agent_turns', 0)}")
        lines.append(f"- Clarification Questions: {conversation.get('clarification_questions', 0)}")
        lines.append(f"- Follow-up Requests: {conversation.get('follow_up_requests', 0)}")
        
        # Question metrics
        lines.append(f"\nQuestion Metrics:")
        lines.append(f"- Total Questions: {questions.get('total', 0)}")
        lines.append(f"- Total Candidate Questions: {questions.get('total_candidates', 0)}")
        if questions.get('total_candidates', 0) > 0:
            lines.append(f"- Selection Rate: {questions.get('total', 0) / questions.get('total_candidates', 1):.2f}")
        lines.append(f"- Average EVPI: {questions.get('average_evpi', 0.0):.4f}")
        lines.append(f"- Average Regret Reduction: {questions.get('average_regret_reduction', 0.0):.4f}")
        lines.append(f"- Average UCB Score: {questions.get('average_ucb_score', 0.0):.4f}")
        
        # Tool call attempt metrics 
        lines.append(f"\nTool Call Attempt Metrics:")
        lines.append(f"- Total Tool Call Attempts: {metrics.get('num_tool_call_attempts', 0)}")
        
        return "\n".join(lines)
    """Class for visualizing simulation results."""
    
    def __init__(self):
        """Initialize a simulation visualizer."""
        pass
    
    def visualize_conversation(
        self,
        conversation: List[Dict[str, Any]]
    ) -> str:
        """
        Visualize the conversation in a pretty format.
        
        Args:
            conversation: List of conversation turns
            
        Returns:
            Formatted conversation string
        """
        if not conversation:
            return "No conversation recorded."
            
        lines = []
        
        for i, turn in enumerate(conversation):
            role = turn.get("role", "unknown")
            message = turn.get("message", "")
            turn_type = turn.get("type", "")
            
            if role == "user":
                prefix = "User"
                if turn_type == "initial":
                    prefix = "User (initial)"
                elif turn_type == "follow_up":
                    prefix = "User (follow-up)"
                elif turn_type == "clarification_response":
                    prefix = "User (clarification)"
                    
                lines.append(f"\n{prefix}: {message}")
                
            elif role == "agent":
                prefix = "Agent"
                if turn_type:
                    prefix = f"Agent ({turn_type})"
                lines.append(f"\n{prefix}: {message}")
                
            else:
                lines.append(f"\n{role}: {message}")
        
        return "\n".join(lines)
    
    def visualize_questions(
        self,
        questions: List[Dict[str, Any]],
        all_candidate_questions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Visualize the questions and their metrics.
        
        Args:
            questions: List of questions with metrics
            all_candidate_questions: List of all candidate questions
            
        Returns:
            Formatted questions string
        """
        if not questions and not all_candidate_questions:
            return "No questions asked."
            
        lines = ["Questions and Metrics:"]
        
        if all_candidate_questions:
            lines.append(f"\nTotal candidate questions: {len(all_candidate_questions)}")
            lines.append(f"Total selected questions: {len(questions)}")
            lines.append(f"Selection rate: {len(questions)/len(all_candidate_questions):.2f} if all_candidate_questions else 'N/A'")
            
            # Display selected questions
            if questions:
                lines.append("\nSelected Questions:")
                for i, q in enumerate(questions):
                    question_text = q.get("question_text", "")
                    target_args = q.get("target_args", [])
                    metrics = q.get("metrics", {})
                    
                    # Format target arguments
                    target_args_str = ", ".join([f"{tool}.{arg}" for tool, arg in target_args])
                    
                    # Format metrics
                    evpi = metrics.get("evpi", 0.0)
                    regret_reduction = metrics.get("regret_reduction", 0.0)
                    ucb_score = metrics.get("ucb_score", 0.0)
                    
                    lines.append(f"\nQuestion {i+1}: {question_text}")
                    lines.append(f"Target Arguments: {target_args_str}")
                    lines.append(f"Metrics: EVPI={evpi:.4f}, Regret Reduction={regret_reduction:.4f}, UCB Score={ucb_score:.4f}")
        else:
            # Legacy format with only selected questions
            for i, q in enumerate(questions):
                question_text = q.get("question_text", "")
                target_args = q.get("target_args", [])
                metrics = q.get("metrics", {})
                
                # Format target arguments
                target_args_str = ", ".join([f"{tool}.{arg}" for tool, arg in target_args])
                
                # Format metrics
                evpi = metrics.get("evpi", 0.0)
                regret_reduction = metrics.get("regret_reduction", 0.0)
                ucb_score = metrics.get("ucb_score", 0.0)
                
                lines.append(f"\nQuestion {i+1}: {question_text}")
                lines.append(f"Target Arguments: {target_args_str}")
                lines.append(f"Metrics: EVPI={evpi:.4f}, Regret Reduction={regret_reduction:.4f}, UCB Score={ucb_score:.4f}")
        
        return "\n".join(lines)
    
    def visualize_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        title: str = "Tool Calls",
        all_tool_call_attempts: List[Dict[str, Any]] = None
    ) -> str:
        """
        Visualize tool calls in a pretty format.
        
        Args:
            tool_calls: List of tool calls
            title: Title for the visualization
            all_tool_call_attempts: List of all tool call attempts (successful and failed)
            
        Returns:
            Formatted tool calls string
        """
        lines = []
        
        if all_tool_call_attempts:
            lines.append(f"All Tool Call Attempts: {len(all_tool_call_attempts)}")
            successful_attempts = sum(1 for a in all_tool_call_attempts if a.get("was_executed", False) and a.get("success", False))
            lines.append(f"Successful Attempts: {successful_attempts}")
            lines.append(f"Failed Attempts: {sum(1 for a in all_tool_call_attempts if a.get('was_executed', False) and not a.get('success', False))}")
            lines.append(f"Skipped Attempts: {sum(1 for a in all_tool_call_attempts if not a.get('was_executed', False))}")
            
            # Add detailed visualization of attempts if desired
            # (omitted for brevity)
            
        if not tool_calls:
            lines.append(f"\n{title}: None")
            return "\n".join(lines)
            
        lines.append(f"\n{title}:")
        
        for i, tc in enumerate(tool_calls):
            tool_name = tc.get("tool_name", "")
            arguments = tc.get("arguments", tc.get("parameters", {}))
            
            # Format parameters
            params_str = ", ".join([f"{k}={v}" for k, v in arguments.items()])
            
            lines.append(f"\n{i+1}. {tool_name}({params_str})")
        
        return "\n".join(lines)