from typing import Dict, List, Any, Tuple, Optional
import logging
import sys
from .provider import LLMProvider

logger = logging.getLogger(__name__)

class UserSimulator:
    """Class for simulating user responses in testing."""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        ground_truth: Dict[str, Any],
        user_intent: Optional[str] = None
    ):
        """
        Initialize a user simulator.
        
        Args:
            llm_provider: Provider for LLM interactions
            ground_truth: Ground truth data for simulation
            user_intent: Optional user intent description
        """
        self.llm = llm_provider
        self.ground_truth = ground_truth
        self.user_intent = user_intent or "No specific intent provided."
        
        # Store the original query
        self.original_query = ground_truth.get("user_query", "")
        
        # Extract ground truth tool calls
        self.gt_tool_calls = ground_truth.get("ground_truth_tool_calls", [])
        
        # Track which tool calls have been completed
        self.completed_tool_calls = set()
        
        # Extract potential follow-up queries
        self.potential_follow_ups = ground_truth.get("potential_follow_ups", [])
        self.current_follow_up_index = 0
        
        # Extract context information
        self.context = {
            k: v for k, v in ground_truth.items() 
            if k not in ["user_query", "user_intent", "ground_truth_tool_calls", "potential_follow_ups"]
        }
        
        # Track conversation turn for intent isolation
        self.current_turn = 1
    
    def get_response_to_question(self, question: str) -> Optional[str]:
        """
        Generate a simulated user response to a clarification question.
        
        Args:
            question: The question asked by the agent
            
        Returns:
            Simulated user response or None if user has no more requests
        """
        # Check if this is an "anything else" question
        if self._is_follow_up_question(question):
            # In the case of "anything else" questions, we should either:
            # 1. Return the next follow-up request if there is one
            # 2. Return None to indicate the conversation should end
            
            # Check if we have a follow-up request
            if self.potential_follow_ups and self.current_follow_up_index < len(self.potential_follow_ups):
                next_follow_up = self.potential_follow_ups[self.current_follow_up_index]
                self.current_follow_up_index += 1
                logger.info(f"Using predefined follow-up in response to 'anything else' question: {next_follow_up}")
                self.current_turn += 1
                return next_follow_up
            else:
                # No more follow-ups, indicate conversation should end
                logger.info("No more follow-ups, ending conversation")
                return None
        
        # This is a specific clarification question, not a general "anything else" question
        # Get only the ground truth relevant to the current turn to avoid leaking future intentions
        current_turn_ground_truth = self._get_current_turn_ground_truth()
        
        # Create a prompt for the LLM to generate a realistic user response
        prompt = f"""
You are simulating a user who is interacting with an AI assistant.

Original query: "{self.original_query}"

User's intent for the CURRENT request: {self.user_intent}

Information needed for the CURRENT request (do not reveal future intentions):
{current_turn_ground_truth}

Additional context:
{self.context}

The AI assistant has asked the following specific question:
"{question}"

Generate a realistic user response to this SPECIFIC question. The response should:
1. Be natural and conversational
2. ONLY provide information that directly answers the specific question asked
3. NOT mention any future requests or intentions the user might have
4. ONLY focus on the current task, not on future tasks
5. Be concise and to the point

IMPORTANT: Never reveal future intentions. Respond ONLY to the specific question asked.

NEVER BREAK CHARACTER. DO NOT THINK OUT LOUD. Respond directly as the user would:
"""
        
        # Generate the response
        response = self.llm.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.4  # Lower temperature for more deterministic responses
        )
        
        return response.strip()
        
    def get_next_request(self, conversation_history: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a simulated follow-up request based on the conversation so far.
        
        Args:
            conversation_history: List of conversation turns so far
            
        Returns:
            Simulated user request or None if the user would have no more requests
        """
        # If we have predefined follow-ups, use the next one
        if self.potential_follow_ups and self.current_follow_up_index < len(self.potential_follow_ups):
            next_follow_up = self.potential_follow_ups[self.current_follow_up_index]
            self.current_follow_up_index += 1
            logger.info(f"Using predefined follow-up: {next_follow_up}")
            self.current_turn += 1
            return next_follow_up
        
        # Format conversation history
        formatted_history = ""
        if conversation_history:
            history_lines = []
            for turn in conversation_history:
                role = turn.get("role", "unknown")
                message = turn.get("message", "")
                history_lines.append(f"{role.capitalize()}: {message}")
            formatted_history = "\n".join(history_lines)
            
        # Create a prompt for the LLM to decide if the user would have a follow-up
        prompt = f"""
You are simulating a user who is interacting with an AI assistant.

Original query: "{self.original_query}"

User's intent: {self.user_intent}

Previous conversation:
{formatted_history}

Based on the conversation so far and the user's intent, decide if the user would have a follow-up request.
Consider:
1. Has everything the user wanted been accomplished?
2. Is there a logical next step the user might want to take?
3. Has the agent clearly indicated that they've completed all necessary tasks?

If you believe the user would have a follow-up request, provide it in a natural, conversational way.
If you believe the conversation is complete, respond with "CONVERSATION_COMPLETE".

NEVER BREAK CHARACTER, DO NOT THINK!

Decision:
"""
        
        # Generate the decision
        decision = self.llm.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.4
        )
        
        decision = decision.strip()
        
        # Check if the decision indicates completion
        if "CONVERSATION_COMPLETE" in decision or "conversation complete" in decision.lower():
            logger.info("LLM determined conversation is complete")
            return None
            
        logger.info(f"Generated follow-up request: {decision}")
        self.current_turn += 1
        return decision
    
    def _is_follow_up_question(self, message: str) -> bool:
        """
        Determine if a message is asking if the user wants anything else.
        
        Args:
            message: Message to analyze
            
        Returns:
            True if it's a follow-up question, False otherwise
        """
        message = message.lower()
        
        # Check for standard patterns that indicate asking if user wants anything else
        patterns = [
            "anything else",
            "something else",
            "can i help you with anything else",
            "is there anything else",
            "would you like me to help with anything else",
            "would you like me to do anything else",
            "is there something else",
            "do you have any other requests",
            "any other tasks",
            "what else can i do for you"
        ]
        
        # Check if message contains a question mark and any of the patterns
        contains_question_mark = "?" in message
        contains_pattern = any(pattern in message for pattern in patterns)
        
        return contains_question_mark and contains_pattern
    
    def _get_current_turn_ground_truth(self) -> str:
        """
        Get ground truth relevant to the current turn only.
        
        Returns:
            String representation of current turn ground truth
        """
        # Extract ground truth for current turn
        current_turn_gt = []
        for call in self.gt_tool_calls:
            # If the call has turn information
            turn = call.get("turn", 1)  # Default to turn 1 if not specified
            if turn == self.current_turn:
                current_turn_gt.append(call)
        
        # If no turn-specific ground truth, use the first tool call
        if not current_turn_gt and self.gt_tool_calls:
            if self.current_turn == 1:
                current_turn_gt = [self.gt_tool_calls[0]]
        
        return str(current_turn_gt)