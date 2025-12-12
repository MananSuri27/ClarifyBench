from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """Abstract base class for API plugins.
    
    This interface defines the contract that all API plugins must fulfill to work
    with the disambiguation system. It provides methods for tool discovery, execution,
    validation, and API-specific behaviors like domain updates and uncertainty context.
    """
    
    def __init__(self):
        """Initialize the base plugin."""
        # Track virtual tools that are added dynamically
        self._virtual_tools = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the plugin."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the description of the plugin."""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of tools provided by this plugin.
        
        Returns:
            List of tool definitions in dictionary format.
        """
        pass
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools including virtual tools.
        
        Returns:
            List of all tool definitions (regular + virtual).
        """
        regular_tools = self.get_tools()
        return regular_tools + self._virtual_tools
    
    def _add_virtual_tool(self, tool_definition: Dict[str, Any]) -> None:
        """
        Add a virtual tool to this plugin.
        
        Virtual tools are tools that don't correspond to actual API methods
        but are useful for the agent system (like final_answer).
        
        Args:
            tool_definition: Tool definition dictionary
        """
        # Validate tool definition
        required_fields = ["name", "description", "arguments"]
        for field in required_fields:
            if field not in tool_definition:
                logger.warning(f"Virtual tool missing required field '{field}', skipping")
                return
        
        # Check if tool already exists
        tool_name = tool_definition["name"]
        existing_names = {tool["name"] for tool in self.get_all_tools()}
        if tool_name in existing_names:
            logger.warning(f"Tool '{tool_name}' already exists, skipping virtual tool")
            return
        
        self._virtual_tools.append(tool_definition)
        logger.info(f"Added virtual tool: {tool_name}")
    
    def _is_virtual_tool(self, tool_name: str) -> bool:
        """Check if a tool is a virtual tool."""
        virtual_names = {tool["name"] for tool in self._virtual_tools}
        return tool_name in virtual_names
    
    def _execute_virtual_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a virtual tool.

        Args:
            tool_name: Name of the virtual tool
            parameters: Parameters for the tool

        Returns:
            Execution result
        """
        # Handle final_answer specially
        if tool_name == "final_answer":
            answer = parameters.get("answer", "Task completed")
            return {
                "success": True,
                "message": answer,
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "final_answer": answer
                }
            }

        # Handle ask_user specially
        elif tool_name == "ask_user":
            question = parameters.get("question", "Could you provide more details?")
            return {
                "success": True,
                "message": question,
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "question": question
                }
            }

        # For other virtual tools, return a generic success
        return {
            "success": True,
            "message": f"Virtual tool '{tool_name}' executed",
            "output": {
                "tool_name": tool_name,
                "parameters": parameters
            }
        }
    
    @abstractmethod
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Result of the tool execution with at least the following keys:
            - success: Whether execution was successful
            - message: User-friendly message about the result
            - output: (optional) Output data from the tool
            - error: (optional) Error details if execution failed
        """
        pass
    
    def execute_tool_with_virtual_support(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with support for virtual tools.
        
        This method should be called instead of execute_tool directly
        to handle both regular and virtual tools.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Result of the tool execution
        """
        # Check if it's a virtual tool
        if self._is_virtual_tool(tool_name):
            return self._execute_virtual_tool(tool_name, parameters)
        
        # Otherwise, execute as regular tool
        return self.execute_tool(tool_name, parameters)
    
    @abstractmethod
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call before execution.
        
        Args:
            tool_name: Name of the tool to validate
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message), where error_message is None if valid
        """
        pass
    
    def validate_tool_call_with_virtual_support(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call with support for virtual tools.
        
        Args:
            tool_name: Name of the tool to validate
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's a virtual tool
        if self._is_virtual_tool(tool_name):
            # Find the virtual tool definition
            virtual_tool = None
            for tool in self._virtual_tools:
                if tool["name"] == tool_name:
                    virtual_tool = tool
                    break
            
            if not virtual_tool:
                return False, f"Virtual tool '{tool_name}' not found"
            
            # Validate virtual tool arguments
            for arg_def in virtual_tool.get("arguments", []):
                if arg_def.get("required", True) and arg_def["name"] not in parameters:
                    return False, f"Missing required argument: {arg_def['name']}"
            
            return True, None
        
        # Otherwise, validate as regular tool
        return self.validate_tool_call(tool_name, parameters)
    
    def get_domain_updates_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get updates to tool domains based on context.
        For example, page numbers might depend on the number of pages in a document.
        
        Args:
            context: Context data that may affect domain definitions
            
        Returns:
            Dictionary mapping "tool_name.arg_name" to updated domain information
        """
        return {}
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """
        Get API-specific context for uncertainty calculation.
        This allows each API to provide custom data for uncertainty calculations.
        
        Returns:
            Dictionary of context data for uncertainty calculations
        """
        return {}
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """
        Get API-specific prompt templates.
        
        Returns:
            Dictionary mapping template names to template strings
        """
        return {}
    
    def _cast_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Cast parameters to their expected types based on tool definitions.
        
        Args:
            tool_name: Name of the tool
            parameters: Raw parameters to cast
            
        Returns:
            Tuple of (casted_parameters, error_message)
            error_message is None if casting succeeded
        """
        # Find the tool definition (including virtual tools)
        tool_def = None
        for tool in self.get_all_tools():
            if tool["name"] == tool_name:
                tool_def = tool
                break
        
        if not tool_def:
            return parameters, f"Unknown tool: {tool_name}"
        
        casted_params = {}
        
        # Process each argument definition
        for arg_def in tool_def.get("arguments", []):
            arg_name = arg_def["name"]
            
            # Use default value if parameter not provided
            if arg_name not in parameters:
                if "default" in arg_def:
                    casted_params[arg_name] = arg_def["default"]
                continue
            
            raw_value = parameters[arg_name]
            
            # Skip casting for special values like "<UNK>"
            if raw_value == "<UNK>":
                casted_params[arg_name] = raw_value
                continue
            
            # Determine expected type from domain
            domain = arg_def.get("domain", {})
            domain_type = domain.get("type", "string")
            
            try:
                casted_value = self._cast_single_value(raw_value, domain_type, domain)
                casted_params[arg_name] = casted_value
            except (ValueError, TypeError) as e:
                return parameters, f"Failed to cast parameter '{arg_name}': {str(e)}"
        
        # Include any parameters not in the tool definition (pass through)
        for param_name, param_value in parameters.items():
            if param_name not in casted_params:
                casted_params[param_name] = param_value
        
        return casted_params, None
    
    def _cast_single_value(self, value: Any, domain_type: str, domain: Dict[str, Any]) -> Any:
        """
        Cast a single value to the expected type.
        
        Args:
            value: Raw value to cast
            domain_type: Expected type from domain
            domain: Full domain specification
            
        Returns:
            Casted value
            
        Raises:
            ValueError: If casting fails
            TypeError: If value type is incompatible
        """
        # If value is already the right type, return as-is for some cases
        if domain_type == "boolean":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ("true", "yes", "1", "on"):
                    return True
                elif value.lower() in ("false", "no", "0", "off"):
                    return False
                else:
                    raise ValueError(f"Cannot convert '{value}' to boolean")
            if isinstance(value, (int, float)):
                return bool(value)
            raise TypeError(f"Cannot convert {type(value)} to boolean")
        
        elif domain_type == "numeric_range":
            if isinstance(value, (int, float)):
                return value
            if isinstance(value, str):
                try:
                    # Try int first, then float
                    if '.' not in value:
                        return int(value)
                    else:
                        return float(value)
                except ValueError:
                    raise ValueError(f"Cannot convert '{value}' to number")
            raise TypeError(f"Cannot convert {type(value)} to number")
        
        elif domain_type == "finite":
            # For finite domains, we typically want to preserve the type
            # but ensure it's in the acceptable values
            return value
        
        elif domain_type == "list":
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                # Try to parse as comma-separated values
                return [item.strip() for item in value.split(',') if item.strip()]
            raise TypeError(f"Cannot convert {type(value)} to list")
        
        elif domain_type == "string":
            if isinstance(value, str):
                return value
            # Convert other types to string
            return str(value)
        
        else:
            # Unknown domain type, return as-is
            return value