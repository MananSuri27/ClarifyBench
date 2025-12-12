from typing import Dict, List, Any, Tuple, Optional
import logging
from core.tool_registry import ToolRegistry
from core.types import ToolCall
from core.plugin_manager import PluginManager

logger = logging.getLogger(__name__)

class ToolExecutionResult:
    """Class representing the result of a tool execution."""
    
    def __init__(
        self,
        tool_name: str,
        success: bool,
        message: str,
        error: Optional[str] = None,
        output: Optional[Dict] = None
    ):
        """
        Initialize a tool execution result.
        
        Args:
            tool_name: Name of the executed tool
            success: Whether the execution succeeded
            message: Human-readable message about the execution
            error: Error message if execution failed
            output: Output of the tool if execution succeeded
        """
        self.tool_name = tool_name
        self.success = success
        self.message = message
        self.error = error
        self.output = output or {}
    
    def to_dict(self) -> Dict:
        """Convert the execution result to a dictionary."""
        result = {
            "tool_name": self.tool_name,
            "success": self.success,
            "message": self.message
        }
        
        if self.error:
            result["error"] = self.error
            
        if self.output:
            result["output"] = self.output
            
        return result


class ToolExecutor:
    """Class for executing tool calls with virtual tool support."""
    
    def __init__(
        self,
        tool_registry: ToolRegistry,
        plugin_manager: PluginManager
    ):
        """
        Initialize a tool executor.
        
        Args:
            tool_registry: Registry of available tools
            plugin_manager: Manager for API plugins
        """
        self.tool_registry = tool_registry
        self.plugin_manager = plugin_manager
    
    def validate_tool_call(self, tool_call: ToolCall) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call before execution.
        This checks if the tool call is executable (has all required parameters),
        NOT if the parameters are correct against ground truth.
        
        Args:
            tool_call: Tool call to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get the plugin for this tool
        plugin = self.plugin_manager.get_plugin_for_tool(tool_call.tool_name)
        if plugin:
            # Use plugin-specific validation with virtual tool support
            return plugin.validate_tool_call_with_virtual_support(
                tool_call.tool_name, 
                tool_call.arguments
            )
        
        # Fallback to tool registry validation for tools without plugins
        tool = self.tool_registry.get_tool(tool_call.tool_name)
        if not tool:
            return False, f"Unknown tool: {tool_call.tool_name}"
            
        # Check required arguments using tool registry
        for arg in tool.arguments:
            if arg.required and (arg.name not in tool_call.arguments or tool_call.arguments[arg.name] == "<UNK>"):
                return False, f"Missing required argument: {arg.name}"
            
            # If the argument is provided, validate its domain
            if arg.name in tool_call.arguments and tool_call.arguments[arg.name] != "<UNK>":
                value = tool_call.arguments[arg.name]
                
                # Validate based on domain type
                if not self._validate_argument_by_domain(arg, value):
                    return False, f"Invalid value for argument {arg.name}: {value}"
        
        return True, None
    
    def _validate_argument_by_domain(self, arg, value) -> bool:
        """
        Validate an argument value based on its domain type.
        
        Args:
            arg: The argument definition
            value: The value to validate
            
        Returns:
            True if valid, False otherwise
        """
        domain = arg.domain
        
        # Handle different domain types
        if domain.domain_type.value == "finite":
            # For finite domains, value must be in the allowed set
            return value in domain.values
        
        elif domain.domain_type.value == "numeric_range":
            # For numeric ranges, value must be within range
            try:
                val = float(value)
                start, end = domain.values
                return start <= val <= end
            except (ValueError, TypeError):
                return False
        
        elif domain.domain_type.value == "boolean":
            # For booleans, must be bool type or convertible
            return isinstance(value, bool) or value in ['true', 'false', 'True', 'False', True, False]
        
        elif domain.domain_type.value == "string":
            # For strings, any non-empty string is valid
            return isinstance(value, str) and value != ""
        
        elif domain.domain_type.value == "list":
            # For lists, must be a list and each element must be valid
            if not isinstance(value, list):
                return False
            # If there's an element domain defined, validate each element
            if hasattr(domain, 'element_domain'):
                element_domain = domain.element_domain
                return all(self._validate_argument_by_domain(
                    type('dummy_arg', (), {'domain': element_domain}), 
                    elem
                ) for elem in value)
            return True
        
        # Default case for unknown domain types
        return True
    
    def execute_tool_call(self, tool_call: ToolCall) -> ToolExecutionResult:
        """
        Execute a single tool call with virtual tool support.
        
        Args:
            tool_call: Tool call to execute
            
        Returns:
            Execution result
        """
        # Validate the tool call for executability
        is_valid, error = self.validate_tool_call(tool_call)
        if not is_valid:
            return ToolExecutionResult(
                tool_name=tool_call.tool_name,
                success=False,
                message=f"Validation failed: {error}",
                error=error
            )
        
        # Get the plugin for this tool
        plugin = self.plugin_manager.get_plugin_for_tool(tool_call.tool_name)
        if not plugin:
            # Special case: check if this is a virtual tool in any plugin
            for plugin_name, p in self.plugin_manager.plugins.items():
                if hasattr(p, '_is_virtual_tool') and p._is_virtual_tool(tool_call.tool_name):
                    plugin = p
                    break
            
            if not plugin:
                return ToolExecutionResult(
                    tool_name=tool_call.tool_name,
                    success=False,
                    message=f"No plugin found for tool: {tool_call.tool_name}",
                    error="PLUGIN_NOT_FOUND"
                )
        
        # Prepare parameters for execution (filter out <UNK> values)
        parameters = {
            k: v for k, v in tool_call.arguments.items() 
            if v != "<UNK>"
        }
        
        try:
            # Execute the tool call via the plugin with virtual tool support
            result = plugin.execute_tool_with_virtual_support(
                tool_name=tool_call.tool_name,
                parameters=parameters
            )
            
            # Check if execution succeeded
            if result.get("success", False):
                return ToolExecutionResult(
                    tool_name=tool_call.tool_name,
                    success=True,
                    message=result.get("message", "Tool executed successfully"),
                    output=result.get("output", {})
                )
            else:
                return ToolExecutionResult(
                    tool_name=tool_call.tool_name,
                    success=False,
                    message=result.get("message", "Tool execution failed"),
                    error=result.get("error", "Unknown error")
                )
                
        except Exception as e:
            logger.exception(f"Error executing tool {tool_call.tool_name}")
            return ToolExecutionResult(
                tool_name=tool_call.tool_name,
                success=False,
                message=f"Error executing tool: {str(e)}",
                error=str(e)
            )
    
    def execute_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolExecutionResult]:
        """
        Execute a sequence of tool calls.
        
        Args:
            tool_calls: List of tool calls to execute
            
        Returns:
            List of execution results
        """
        results = []
        
        for tool_call in tool_calls:
            result = self.execute_tool_call(tool_call)
            results.append(result)
            
            # If execution failed, stop processing further tool calls
            if not result.success:
                break
        
        return results
    
    def is_final_answer_tool(self, tool_call: ToolCall) -> bool:
        """
        Check if a tool call is the final_answer tool.
        
        Args:
            tool_call: Tool call to check
            
        Returns:
            True if this is the final_answer tool
        """
        return tool_call.tool_name == "final_answer"
    
    def generate_error_clarification(
        self, 
        error_result: ToolExecutionResult, 
        tool_calls: List[ToolCall],
        user_query: str,
        llm_provider
    ) -> Tuple[Optional[str], List[ToolCall]]:
        """
        Generate a clarification question based on an error.
        
        Args:
            error_result: The error execution result
            tool_calls: The current tool calls
            user_query: Original user query
            llm_provider: LLM provider for generating clarification
            
        Returns:
            Tuple of (clarification question or None, updated tool calls)
        """
        # Prepare the prompt for error clarification
        tool_descriptions = self.tool_registry.get_tool_descriptions()
        
        prompt = f"""
You are an AI assistant that helps users by understanding their queries and executing tool calls.

Original user query:
"{user_query}"

The following tool call resulted in an error:
Tool: {error_result.tool_name}
Error: {error_result.error}
Error message: {error_result.message}

Current tool calls:
{[tc.to_dict() for tc in tool_calls]}

Available tools:
{tool_descriptions}

Based on the error, I need two things:
1. A clear, conversational clarification question to ask the user to help resolve the error
2. An updated version of the tool calls that might resolve the error if the user doesn't provide more information

Return your response as a JSON object with the following structure:
{{
  "clarification_question": "The question to ask the user",
  "updated_tool_calls": [
    {{
      "tool_name": "tool_name",
      "arguments": {{
        "arg1": "value1",
        "arg2": "value2"
      }}
    }}
  ]
}}
"""
        
        # Call LLM to generate clarification
        response = llm_provider.generate_json(
            prompt=prompt,
            response_model={
                "clarification_question": "string",
                "updated_tool_calls": [
                    {
                        "tool_name": "string",
                        "arguments": {}
                    }
                ]
            },
            max_tokens=2000
        )
        
        # Extract the clarification question
        clarification_question = response.get("clarification_question")
        
        # Extract the updated tool calls
        updated_tool_calls_data = response.get("updated_tool_calls", [])
        updated_tool_calls = []
        
        for tc_data in updated_tool_calls_data:
            tool_name = tc_data.get("tool_name", "")
            arguments = tc_data.get("arguments", {})
            
            if tool_name:
                updated_tool_calls.append(ToolCall(tool_name, arguments))
        
        # If no updated tool calls were provided, keep the original ones
        if not updated_tool_calls:
            updated_tool_calls = tool_calls
        
        return clarification_question, updated_tool_calls