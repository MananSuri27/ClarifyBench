from typing import Dict, List, Any, Union, Optional
import abc
import json
import re
import logging

logger = logging.getLogger(__name__)

class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""
    
    @abc.abstractmethod
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text from the LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        pass
    
    @abc.abstractmethod
    def generate_json(
        self,
        prompt: str,
        response_model: Dict[str, Any],
        max_tokens: int = 1000,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate structured JSON from the LLM.
        
        Args:
            prompt: Input prompt
            response_model: Expected structure of the response
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated JSON as a dictionary
        """
        pass
    
    def repair_json(self, json_str: str) -> str:
        """
        Attempt to repair malformed JSON from LLM responses.
        
        Args:
            json_str: The potentially malformed JSON string
            
        Returns:
            Repaired JSON string
        """
        # Skip if the string is empty
        if not json_str:
            return json_str
            
        # Try to extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
        if json_match:
            json_str = json_match.group(1)
        
        # Fix unescaped quotes within strings
        json_str = re.sub(r'(?<!\\)"(?=(.*?".*?"))', r'\"', json_str)
        
        # Fix trailing commas in objects and arrays
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*\]', ']', json_str)
        
        # Fix missing quotes around property names
        json_str = re.sub(r'(\s*?)(\w+)(\s*?):', r'\1"\2"\3:', json_str)
        
        # Handle special cases like NaN, Infinity, -Infinity which are not valid JSON
        json_str = re.sub(r'\bNaN\b', '"NaN"', json_str)
        json_str = re.sub(r'\bInfinity\b', '"Infinity"', json_str)
        json_str = re.sub(r'\b-Infinity\b', '"-Infinity"', json_str)
        
        return json_str

    def safe_parse_json(self, json_str: str, default: Dict = None) -> Dict[str, Any]:
        """
        Safely parse JSON with fallback to repair or default value.
        
        Args:
            json_str: The JSON string to parse
            default: Default value to return if parsing fails
            
        Returns:
            Parsed JSON as a dictionary, or the default value if parsing fails
        """
        if default is None:
            default = {}
            
        # Debug output to help identify the problem
        logger.debug(f"Attempting to parse JSON: {json_str[:500]}...")
        
        # First, try to extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
        if json_match:
            extracted_json = json_match.group(1)
            try:
                return json.loads(extracted_json)
            except json.JSONDecodeError:
                # If extraction failed, continue with the repair process
                logger.debug("Extracted JSON from code block but it's still invalid")
                json_str = extracted_json  # Use the extracted JSON for further repairs
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parsing failed: {e}")
            
            # Print detailed debug information about the error
            try:
                lines = json_str.splitlines()
                if e.lineno <= len(lines):
                    problem_line = lines[e.lineno-1]
                    pointer = ' ' * (e.colno-1) + '^'
                    logger.warning(f"Problematic line ({e.lineno}): {problem_line}")
                    logger.warning(f"Position: {pointer}")
            except Exception as debug_e:
                logger.warning(f"Error during debug output: {debug_e}")
            
            try:
                # Attempt to repair the JSON
                repaired = self.repair_json(json_str)
                logger.debug(f"Repaired JSON: {repaired[:500]}...")
                return json.loads(repaired)
            except Exception as repair_e:
                logger.error(f"Failed to parse JSON even after repair: {repair_e}")
                logger.debug(f"Original JSON string: {json_str}")
                return default
        
    def enhance_json_prompt(self, prompt: str, response_model: Dict[str, Any]) -> str:
        """
        Enhance a prompt with clearer instructions for JSON output.
        
        Args:
            prompt: Original prompt
            response_model: Expected structure of the response
            
        Returns:
            Enhanced prompt
        """
        model_str = json.dumps(response_model, indent=2)
        
        json_instructions = f"""
IMPORTANT: You MUST respond with valid JSON only. No explanation text before or after. 
Your response should be properly formatted JSON that matches exactly this structure:

{model_str}

Do not include any explanatory text or markdown formatting. Only return the JSON object.
"""
        # If prompt already ends with structure instructions, just add clarity
        if "Return your response as a JSON" in prompt:
            return prompt + "\n" + json_instructions
        else:
            return prompt + "\n\n" + json_instructions
        
    def generate_tool_calls(
        self,
        user_query: str,
        tool_descriptions: str,
        conversation_history: List[Dict[str, Any]] = None,
        max_tokens: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Generate tool calls from a user query.
        
        Args:
            user_query: User's query
            tool_descriptions: Descriptions of available tools
            conversation_history: Optional conversation history
            max_tokens: Maximum tokens to generate
            
        Returns:
            List of tool call dictionaries
        """
        # Format conversation history if provided
        formatted_history = ""
        if conversation_history:
            history_lines = []
            for turn in conversation_history:
                role = turn.get("role", "unknown")
                message = turn.get("message", "")
                history_lines.append(f"{role.capitalize()}: {message}")
            formatted_history = "\n".join(history_lines)
            formatted_history = f"Conversation history:\n{formatted_history}\n\n"
            
        prompt = f"""
You are an AI assistant that helps users by understanding their queries and executing the appropriate tool calls.

{formatted_history}Available tools:
{tool_descriptions}

User query: "{user_query}"

Please analyze the user's query and determine which tool(s) should be called to fulfill the request.
For each tool, specify all required parameters. If a parameter is uncertain, use "<UNK>" as the value.

Think through this step by step:
1. What is the user trying to accomplish?
2. Which tool(s) are needed to complete this task?
3. What parameters are needed for each tool?
4. Which parameters can be determined from the query, and which are uncertain?

Return your response as a JSON object with the following structure:
{{
  "reasoning": "Your step-by-step reasoning about what tools to use and why",
  "tool_calls": [
    {{
      "tool_name": "name_of_tool",
      "arguments": {{
        "arg1": "value1",
        "arg2": "<UNK>"
      }}
    }}
  ]
}}
"""
        # Enhance the prompt with JSON instructions
        prompt = self.enhance_json_prompt(prompt, {
            "reasoning": "string",
            "tool_calls": [
                {
                    "tool_name": "string",
                    "arguments": {}
                }
            ]
        })
        
        response = self.generate_json(
            prompt=prompt,
            response_model={
                "reasoning": "string",
                "tool_calls": [
                    {
                        "tool_name": "string",
                        "arguments": {}
                    }
                ]
            },
            max_tokens=max_tokens,
            temperature=0.2
        )
        
        return response.get("tool_calls", [])
        
    def generate_reasoning(
        self,
        user_query: str,
        conversation_history: List[Dict[str, Any]],
        tool_descriptions: str,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate reasoning about what tools might be needed for a user query.
        
        Args:
            user_query: Current user query
            conversation_history: Prior conversation context
            tool_descriptions: Descriptions of available tools
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with reasoning and potential tool calls
        """
        # Format conversation history
        formatted_history = ""
        if conversation_history:
            history_lines = []
            for turn in conversation_history:
                role = turn.get("role", "unknown")
                message = turn.get("message", "")
                history_lines.append(f"{role.capitalize()}: {message}")
            formatted_history = "\n".join(history_lines)
            
        prompt = f"""
You are an AI assistant that helps users by understanding their queries and executing the appropriate tool calls.

Conversation history:
{formatted_history}

Current user query: "{user_query}"

Available tools:
{tool_descriptions}

Please reason step-by-step about what the user is asking for:
1. What is the user trying to accomplish?
2. What information do we already have from the conversation history?
3. What tools would help accomplish this task?
4. What parameters are needed for each tool?
5. Do we have enough information to execute these tools, or do we need to ask clarifying questions?

Think carefully about each step before proceeding to the next one.

After your reasoning, select the appropriate tool(s) to call.

Tool calls should be formatted as:
{{
  "tool_name": "name_of_tool",
  "arguments": {{
    "arg1": "value1",
    "arg2": "<UNK>" if uncertain
  }}
}}

Return your response as a JSON object with the following structure:
{{
  "reasoning": "Your step-by-step reasoning about what tools to use and why",
  "tool_calls": [
    {{
      "tool_name": "name_of_tool",
      "arguments": {{
        "arg1": "value1",
        "arg2": "<UNK>"
      }}
    }}
  ]
}}
"""
        # Enhance the prompt with JSON instructions
        prompt = self.enhance_json_prompt(prompt, {
            "reasoning": "string",
            "tool_calls": [
                {
                    "tool_name": "string",
                    "arguments": {}
                }
            ]
        })
        
        response = self.generate_json(
            prompt=prompt,
            response_model={
                "reasoning": "string",
                "tool_calls": [
                    {
                        "tool_name": "string",
                        "arguments": {}
                    }
                ]
            },
            max_tokens=max_tokens,
            temperature=0.2
        )
        
        return response
    
    def update_tool_calls_from_error(
        self,
        user_query: str,
        tool_calls: List[Dict[str, Any]],
        error: Dict[str, Any],
        tool_descriptions: str,
        max_tokens: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Update tool calls based on an error.
        
        Args:
            user_query: Original user query
            tool_calls: Current tool calls
            error: Error information
            tool_descriptions: Descriptions of available tools
            max_tokens: Maximum tokens to generate
            
        Returns:
            Updated list of tool call dictionaries
        """
        prompt = f"""
You are an AI assistant that helps users by understanding their queries and executing the appropriate tool calls.

Available tools:
{tool_descriptions}

User query: "{user_query}"

Current tool calls:
{json.dumps(tool_calls, indent=2)}

Error:
{json.dumps(error, indent=2)}

Please update the tool calls to fix the error. Consider what went wrong and how to correct it.

Return your response as a JSON object with the following structure:
{{
  "reasoning": "Your reasoning about what went wrong and how to fix it",
  "updated_tool_calls": [
    {{
      "tool_name": "name_of_tool",
      "arguments": {{
        "arg1": "value1",
        "arg2": "value2"
      }}
    }}
  ]
}}
"""
        # Enhance the prompt with JSON instructions
        prompt = self.enhance_json_prompt(prompt, {
            "reasoning": "string",
            "updated_tool_calls": [
                {
                    "tool_name": "string",
                    "arguments": {}
                }
            ]
        })
        
        response = self.generate_json(
            prompt=prompt,
            response_model={
                "reasoning": "string",
                "updated_tool_calls": [
                    {
                        "tool_name": "string",
                        "arguments": {}
                    }
                ]
            },
            max_tokens=max_tokens,
            temperature=0.2
        )
        
        return response.get("updated_tool_calls", tool_calls)