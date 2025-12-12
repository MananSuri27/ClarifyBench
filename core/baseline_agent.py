from typing import Dict, List, Any, Tuple, Optional, NamedTuple
import logging
import copy
from dataclasses import dataclass
from datetime import datetime
from core.tool_registry import ToolRegistry
from core.tool_executor import ToolExecutor, ToolExecutionResult
from core.plugin_manager import PluginManager
from llm.provider import LLMProvider

logger = logging.getLogger(__name__)


# Import shared data types
from core.types import ToolCall, ClarificationQuestion


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    message: str
    type: str = "completed"  # "completed", "clarification", "error"
    tool_calls: List[Dict] = None
    context: Dict = None
    question_obj: ClarificationQuestion = None
    
    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.context is None:
            self.context = {}


class StepTracker:
    """Tracks a single agentic step (reason -> disambiguate -> execute)."""
    
    def __init__(self, step_index: int):
        self.step_index = step_index
        self.reason_data = None
        self.disambiguation_data = None
        self.execution_data = None
        self.llm_interactions = []
    
    def record_llm_interaction(self, interaction_type: str, prompt: str, response: dict, metadata: dict = None):
        """Record an LLM interaction within this step."""
        self.llm_interactions.append({
            "interaction_type": interaction_type,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def record_reason(self, chain_of_thought: str, tool_call: ToolCall):
        self.reason_data = {
            "chain_of_thought": chain_of_thought,
            "selected_tool": {
                "name": tool_call.tool_name,
                "args": tool_call.arguments
            }
        }
    
    def record_disambiguation(self, disambiguation_result):
        """Record disambiguation attempt and results."""
        self.disambiguation_data = {
            "required": disambiguation_result.get("required", False),
            "certainty_score": disambiguation_result.get("certainty_score", 1.0),
            "candidates_generated": disambiguation_result.get("candidates_generated", 0),
            "selected_question": disambiguation_result.get("selected_question")
        }
    
    def record_execution(self, tool_call: ToolCall, result: ToolExecutionResult):
        self.execution_data = {
            "attempted": True,
            "tool_call": {"name": tool_call.tool_name, "args": tool_call.arguments},
            "result": result.to_dict(),
            "observation_added": result.message if result.success else f"Error: {result.message}"
        }
    
    def to_dict(self) -> Dict:
        return {
            "step_index": self.step_index,
            "reason": self.reason_data,
            "disambiguation": self.disambiguation_data,
            "tool_execution": self.execution_data,
            "llm_interactions": self.llm_interactions
        }


class TurnTracker:
    """Tracks a single turn (user input -> agent response)."""
    
    def __init__(self, turn_index: int, raw_user_input: str):
        self.turn_index = turn_index
        self.raw_user_input = raw_user_input
        self.steps = []
        self.turn_outcome = None
        self.user_response = None
    
    def start_new_step(self) -> StepTracker:
        step = StepTracker(len(self.steps))
        self.steps.append(step)
        return step
    
    def set_outcome(self, outcome: str):
        self.turn_outcome = outcome
    
    def set_user_response(self, clarification_text: str, response_type: str = "clarification"):
        self.user_response = {
            "clarification_text": clarification_text,
            "response_type": response_type
        }
    
    def to_dict(self) -> Dict:
        return {
            "turn_index": self.turn_index,
            "raw_user_input": self.raw_user_input,
            "agentic_steps": [step.to_dict() for step in self.steps],
            "turn_outcome": self.turn_outcome,
            "user_response": self.user_response
        }


class RequestTracker:
    """Tracks a single request (initial query or follow-up)."""
    
    def __init__(self, request_index: int, request_text: str, request_type: str):
        self.request_index = request_index
        self.request_text = request_text
        self.request_type = request_type
        self.turns = []
        self.request_result = None
    
    def start_new_turn(self, raw_user_input: str) -> TurnTracker:
        turn = TurnTracker(len(self.turns), raw_user_input)
        self.turns.append(turn)
        return turn
    
    def set_result(self, success: bool, final_message: str, tool_calls_executed: List[Dict]):
        self.request_result = {
            "success": success,
            "final_message": final_message, 
            "tool_calls_executed": tool_calls_executed,
            "total_turns": len(self.turns),
            "total_steps": sum(len(turn.steps) for turn in self.turns)
        }
    
    def to_dict(self) -> Dict:
        return {
            "request_index": self.request_index,
            "request_text": self.request_text,
            "request_type": self.request_type,
            "turns": [turn.to_dict() for turn in self.turns],
            "request_result": self.request_result
        }


class ConversationTracker:
    """Tracks the full conversation with nested structure."""
    
    def __init__(self):
        self.requests = []
        self.current_request = None
    
    def start_new_request(self, text: str, request_type: str) -> RequestTracker:
        request = RequestTracker(len(self.requests), text, request_type)
        self.requests.append(request)
        self.current_request = request
        return request
    
    def _extract_all_llm_interactions(self) -> List[Dict]:
        """Extract all LLM interactions across the entire conversation."""
        all_interactions = []
        
        for req_idx, request in enumerate(self.requests):
            for turn_idx, turn in enumerate(request.turns):
                for step_idx, step in enumerate(turn.steps):
                    for interaction in step.llm_interactions:
                        all_interactions.append({
                            **interaction,
                            "request_index": req_idx,
                            "turn_index": turn_idx,
                            "step_index": step_idx
                        })
        
        return all_interactions
    
    def export_full_structure(self) -> Dict:
        """Export the full nested structure with LLM trace."""
        total_turns = sum(len(req.turns) for req in self.requests)
        total_steps = sum(sum(len(turn.steps) for turn in req.turns) for req in self.requests)
        
        return {
            "requests": [req.to_dict() for req in self.requests],
            "llm_trace": self._extract_all_llm_interactions(),
            "metrics": {
                "total_requests": len(self.requests),
                "total_turns": total_turns,
                "total_steps": total_steps,
                "total_llm_calls": len(self._extract_all_llm_interactions()),
                "avg_turns_per_request": total_turns / len(self.requests) if self.requests else 0,
                "avg_steps_per_turn": total_steps / total_turns if total_turns else 0
            }
        }
    
    def export_compatibility_format(self) -> Dict:
        """Export flattened data for backward compatibility."""
        conversation = []
        questions = []
        all_candidate_questions = []
        final_tool_calls = []
        all_tool_call_attempts = []
        
        for req in self.requests:
            # Add initial user message
            conversation.append({
                "role": "user",
                "message": req.request_text,
                "type": req.request_type,
                "request_index": req.request_index,
                "turn_index": 0
            })
            
            for turn in req.turns:
                # Process each step in the turn
                for step in turn.steps:
                    # Record tool call attempts
                    if step.execution_data:
                        exec_data = step.execution_data
                        all_tool_call_attempts.append({
                            "tool_call": exec_data["tool_call"],
                            "was_executed": True,
                            "success": exec_data["result"]["success"],
                            "reason": "executed",
                            "execution_result": exec_data["result"],
                            "request_index": req.request_index,
                            "turn_index": turn.turn_index,
                            "step_index": step.step_index
                        })
                        
                        # Record successful tool calls
                        if exec_data["result"]["success"]:
                            final_tool_calls.append({
                                **exec_data["tool_call"],
                                "request_index": req.request_index,
                                "turn_index": turn.turn_index,
                                "step_index": step.step_index,
                                "success": True
                            })
                    
                    # Record questions (minimal for baseline)
                    if step.disambiguation_data and step.disambiguation_data.get("selected_question"):
                        q_data = step.disambiguation_data["selected_question"]
                        questions.append({
                            **q_data,
                            "request_index": req.request_index,
                            "turn_index": turn.turn_index,
                            "step_index": step.step_index
                        })
                
                # Add agent response
                if turn.turn_outcome == "needs_clarification":
                    agent_message = "I need clarification."
                    for step in turn.steps:
                        if step.disambiguation_data and step.disambiguation_data.get("selected_question"):
                            agent_message = step.disambiguation_data["selected_question"]["question_text"]
                            break
                    
                    conversation.append({
                        "role": "agent",
                        "message": agent_message,
                        "type": "clarification",
                        "request_index": req.request_index,
                        "turn_index": turn.turn_index
                    })
                    
                    # Add user clarification if provided
                    if turn.user_response:
                        conversation.append({
                            "role": "user",
                            "message": turn.user_response["clarification_text"],
                            "type": "clarification_response",
                            "request_index": req.request_index,
                            "turn_index": turn.turn_index
                        })
                elif turn.turn_outcome == "completed":
                    conversation.append({
                        "role": "agent",
                        "message": req.request_result["final_message"] if req.request_result else "Completed",
                        "type": "action_response",
                        "request_index": req.request_index,
                        "turn_index": turn.turn_index
                    })
        
        return {
            "conversation": conversation,
            "questions": questions,
            "all_candidate_questions": all_candidate_questions,
            "final_tool_calls": final_tool_calls,
            "all_tool_call_attempts": all_tool_call_attempts
        }


class ReactAgent:
    """
    BASELINE VERSION: Simplified ReAct agent that uses direct LLM reasoning
    without sophisticated uncertainty calculation or question generation.
    
    Maintains same interface as the original for drop-in compatibility.
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
        plugin_manager: PluginManager,
        config: Dict[str, Any] = None
    ):
        """Initialize a simplified ReAct agent."""
        self.llm = llm_provider
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor
        self.plugin_manager = plugin_manager
        self.config = config or {}
        self.max_steps = self.config.get("max_steps", 10)
        
        # Add virtual tools (final_answer and ask_user)
        self._add_virtual_tools()
        
        # Initialize conversation tracker
        self.conversation_tracker = ConversationTracker()
        
        # Track current step for LLM logging
        self._current_step_tracker = None
        self._last_question = None  # For compatibility
        self._all_candidate_questions = []  # Track questions for compatibility
    
    def _add_virtual_tools(self):
        """Add virtual tools (final_answer and ask_user) to base plugin."""
        try:
            base_plugin = None
            for plugin in self.plugin_manager.plugins.values():
                if hasattr(plugin, '_add_virtual_tool'):
                    base_plugin = plugin
                    break

            if base_plugin:
                # Add final_answer virtual tool
                base_plugin._add_virtual_tool({
                    "name": "final_answer",
                    "description": "Provide final answer to the user and complete the task",
                    "arguments": [
                        {
                            "name": "answer",
                            "description": "The final answer to provide to the user",
                            "domain": {"type": "string", "importance": 1.0},
                            "required": True
                        }
                    ]
                })

                # Add ask_user virtual tool
                base_plugin._add_virtual_tool({
                    "name": "ask_user",
                    "description": "Ask the user for clarification or additional information",
                    "arguments": [
                        {
                            "name": "question",
                            "description": "The question to ask the user",
                            "domain": {"type": "string", "importance": 1.0},
                            "required": True
                        }
                    ]
                })

                logger.info("Added virtual tools: final_answer, ask_user")
        except Exception as e:
            logger.warning(f"Could not add virtual tools: {e}")
    
    def _call_llm_with_tracking(self, prompt: str, interaction_type: str, **kwargs):
        """Wrapper for all LLM calls that automatically tracks prompts/responses."""
        response = self.llm.generate_json(prompt=prompt, **kwargs)
        
        # Track this interaction in current step
        if self._current_step_tracker:
            self._current_step_tracker.record_llm_interaction(
                interaction_type=interaction_type,
                prompt=prompt,
                response=response,
                metadata={
                    "model": getattr(self.llm, 'model_name', 'unknown'),
                    "token_count": len(prompt.split())
                }
            )
        
        return response
    
    def _get_plugin_descriptions(self) -> str:
        """Extract plugin descriptions from the plugin manager."""
        plugin_descriptions = []
        
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            description = None
            
            if hasattr(plugin, 'description'):
                description = plugin.description
            elif hasattr(plugin, 'config') and isinstance(plugin.config, dict):
                description = plugin.config.get('description')
            elif hasattr(plugin, 'metadata') and isinstance(plugin.metadata, dict):
                description = plugin.metadata.get('description')
            elif plugin.__class__.__doc__:
                description = plugin.__class__.__doc__.strip()
            elif hasattr(plugin, 'get_description'):
                try:
                    description = plugin.get_description()
                except Exception as e:
                    logger.debug(f"Failed to get description from {plugin_name}: {e}")
            
            if description:
                plugin_descriptions.append(f"**{plugin_name}**: {description}")
            else:
                plugin_descriptions.append(f"**{plugin_name}**: Plugin for {plugin_name} operations")
        
        if plugin_descriptions:
            return "\n".join(plugin_descriptions)
        else:
            return "No plugin descriptions available."
    
    def _reason(self, request: str, observations: List[str]) -> Tuple[str, str, ToolCall]:
        """
        SIMPLIFIED REASONING: Let LLM choose which tool to call, then map virtual tools to action types.

        Returns:
            (reasoning, action_type, tool_call_or_question)
        """
        obs_text = "\n".join(f"- {obs}" for obs in observations) if observations else "None"
        plugin_descriptions = self._get_plugin_descriptions()

        prompt = f"""You are an AI assistant. Help with the user's request by calling appropriate tools.

REQUEST: {request}

OBSERVATIONS:
{obs_text}

AVAILABLE TOOLS:
{self.tool_registry.get_tool_descriptions()}

Choose a tool to call:
- Use regular tools to complete the task. Don't call tools redundantly.
- Use ask_user if you need more information, such as when the user didn't specify appropriate details, and default arguments are not acceptable.
- Use final_answer when done, to give an answer to the user.

Respond in JSON:
{{
    "reasoning": "Your thinking",
    "tool_call": {{
        "tool_name": "tool_name",
        "arguments": {{"arg": "value"}}
    }}
}}
"""

        response = self._call_llm_with_tracking(
            prompt=prompt,
            interaction_type="reasoning",
            response_model={
                "reasoning": "string",
                "tool_call": {
                    "tool_name": "string",
                    "arguments": {}
                }
            },
            max_tokens=2000
        )

        reasoning = response.get("reasoning", "")
        tool_call_data = response.get("tool_call", {})

        tool_name = tool_call_data.get("tool_name", "final_answer")
        arguments = tool_call_data.get("arguments", {})

        # Map virtual tools to action types for downstream processing
        if tool_name == "ask_user":
            question_text = arguments.get("question", "Could you provide more details?")
            return reasoning, "ask_question", question_text
        elif tool_name == "final_answer":
            tool_call = ToolCall("final_answer", arguments)
            return reasoning, "final_answer", tool_call
        else:
            # Regular tool call
            tool_call = ToolCall(tool_name, arguments)
            return reasoning, "tool_call", tool_call
    
    def _handle_error(self, error_result: ToolExecutionResult, request: str, context: Dict) -> Dict:
        """Simplified error handling - generate clarification question via LLM."""
        
        prompt = f"""You encountered an error while trying to help with a user request. Generate a helpful clarification question.

USER REQUEST: {request}

ERROR DETAILS: {error_result.message}

Generate a natural, helpful question to ask the user that might help resolve this error. Be specific and reference what went wrong.

Respond in JSON format:
{{
    "question": "Your clarification question for the user"
}}
"""
        
        try:
            response = self._call_llm_with_tracking(
                prompt=prompt,
                interaction_type="error_clarification",
                response_model={"question": "string"},
                max_tokens=500
            )
            question = response.get("question", f"I encountered an error: {error_result.message}. Could you provide more information?")
        except Exception:
            # Fallback if LLM fails
            question = f"I encountered an error: {error_result.message}. Could you provide more information or clarify your request?"
        
        return {
            "needs_clarification": True,
            "question": question
        }
    
    def run(self, request: str, context: Dict = None) -> AgentResult:
        """
        Execute the simplified ReAct loop for a single request.
        """
        context = context or {"observations": []}
        observations = context["observations"]
        
        # Start tracking this turn
        turn_tracker = self.conversation_tracker.current_request.start_new_turn(request)
        
        for step in range(self.max_steps):
            step_tracker = turn_tracker.start_new_step()
            self._current_step_tracker = step_tracker
            
            # SIMPLIFIED REASON phase
            reasoning, action_type, result = self._reason(request, observations)
            
            if action_type == "ask_question":
                # Need to ask user a question
                question_text = result
                
                # Create question object
                dummy_question = ClarificationQuestion(
                    question_id='baseline_q_1',
                    question_text=question_text
                )
                
                # Record as if we did disambiguation (for compatibility)
                step_tracker.record_disambiguation({
                    "required": True,
                    "certainty_score": 0.5,  # Baseline: always uncertain when asking
                    "candidates_generated": 1,
                    "selected_question": {
                        "question_id": "baseline_q_1",
                        "question_text": question_text,
                        "target_args": [],
                        "metrics": {"evpi": 0.0, "regret_reduction": 0.0, "ucb_score": 0.0}
                    }
                })
                
                self._last_question = dummy_question
                turn_tracker.set_outcome("needs_clarification")
                return AgentResult(
                    success=False,
                    message=question_text,
                    type="clarification",
                    question_obj=dummy_question
                )
            
            # We have a tool call (either real tool or final_answer)
            tool_call = result
            step_tracker.record_reason(reasoning, tool_call)
            
            # Record minimal disambiguation (no uncertainty for baseline)
            step_tracker.record_disambiguation({
                "required": False,
                "certainty_score": 1.0,  # Baseline: always certain when not asking
                "candidates_generated": 0
            })
            
            # Check if final answer
            if tool_call.tool_name == "final_answer":
                step_tracker.record_execution(tool_call, ToolExecutionResult(
                    tool_name="final_answer",
                    success=True,
                    message=tool_call.arguments.get("answer", "Task completed"),
                    output=tool_call.arguments.get("answer", "Task completed")
                ))
                turn_tracker.set_outcome("completed")
                return AgentResult(
                    success=True,
                    message=tool_call.arguments.get("answer", "Task completed"),
                    type="completed",
                    context=context
                )
            
            # Execute tool
            execution_result = self.tool_executor.execute_tool_call(tool_call)
            step_tracker.record_execution(tool_call, execution_result)
            
            # Handle errors simply
            if not execution_result.success:
                error_action = self._handle_error(execution_result, request, context)
                if error_action["needs_clarification"]:
                    turn_tracker.set_outcome("needs_clarification")
                    return AgentResult(
                        success=False,
                        message=error_action["question"],
                        type="error_clarification"
                    )
                else:
                    observations.append(f"Error with {tool_call.tool_name}: {execution_result.message}")
                    continue
            
            # Success - add observation and continue
            observations.append(f"Tool {tool_call.tool_name} executed successfully: {execution_result.message}")
            if execution_result.output:
                observations.append(f"Output: {execution_result.output}")
            context["observations"] = observations
        
        # Max steps reached
        turn_tracker.set_outcome("completed")
        return AgentResult(
            success=True,
            message="Task completed (max steps reached)",
            type="completed",
            context=context
        )
    
    def process_clarification(self, original_request: str, clarification: str, question: str) -> str:
        """Process user clarification and return enriched request."""
        # Record the clarification in current turn
        if (self.conversation_tracker.current_request and 
            self.conversation_tracker.current_request.turns):
            current_turn = self.conversation_tracker.current_request.turns[-1]
            current_turn.set_user_response(clarification, "clarification")
        
        # Simply append clarification to original request
        return f"User request:{original_request}\nUser was asked: {question} \nClarification: {clarification}"
    
    def get_full_conversation_data(self) -> Dict:
        """Get the full nested conversation structure."""
        return self.conversation_tracker.export_full_structure()
    
    def get_compatibility_data(self) -> Dict:
        """Get flattened data for backward compatibility."""
        return self.conversation_tracker.export_compatibility_format()
    
    def start_new_request(self, request_text: str, request_type: str = "initial") -> RequestTracker:
        """Start tracking a new request."""
        return self.conversation_tracker.start_new_request(request_text, request_type)
    
    def complete_current_request(self, success: bool, message: str, tool_calls: List[Dict] = None):
        """Mark the current request as completed."""
        if self.conversation_tracker.current_request:
            self.conversation_tracker.current_request.set_result(
                success=success,
                final_message=message,
                tool_calls_executed=tool_calls or []
            )