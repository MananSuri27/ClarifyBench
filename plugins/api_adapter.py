from typing import Dict, List, Any, Optional, Tuple
import logging
import yaml
import os
from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class APIAdapter(BasePlugin):
    """
    Generic adapter for existing API classes.
    
    This adapter wraps existing API classes to make them compatible with the
    plugin system without requiring modification of the original API code.
    """
    
    def __init__(self, api_instance, config: Dict[str, Any] = None):
        """
        Initialize an API adapter.
        
        Args:
            api_instance: Instance of the API class to wrap
            config: Configuration for the adapter (method mappings, etc.)
        """
        self.api = api_instance
        self.config = config or {}
        self._name = self.config.get("name", getattr(api_instance, "__class__.__name__", "unknown"))
        self._description = self.config.get("description", getattr(api_instance, "_api_description", ""))
        self._tools = self._generate_tools_from_config()
        self._method_map = self.config.get("method_map", {})
        self._param_transforms = self.config.get("param_transforms", {})
        self._result_transforms = self.config.get("result_transforms", {})
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def _generate_tools_from_config(self) -> List[Dict[str, Any]]:
        """Generate tool definitions from the configuration."""
        return self.config.get("tools", [])
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools provided by this plugin."""
        return self._tools
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        # Cast parameters first using the base class method
        casted_params, cast_error = self._cast_parameters(tool_name, parameters)
        if cast_error:
            return {
                "success": False,
                "message": f"Parameter casting error: {cast_error}",
                "error": "TYPE_CASTING_ERROR"
            }
        
        # Find the corresponding API method for this tool
        method_name = self._method_map.get(tool_name)
        if not method_name or not hasattr(self.api, method_name):
            return {
                "success": False,
                "message": f"No method found for tool: {tool_name}",
                "error": "METHOD_NOT_FOUND"
            }
        
        # Apply parameter transformations if needed
        transformed_params = self._transform_parameters(tool_name, casted_params)
        
        # Call the API method
        try:
            method = getattr(self.api, method_name)
            result = method(**transformed_params)
            
            # Apply result transformations if needed
            transformed_result = self._transform_result(tool_name, result)
            
            # Format the result
            return transformed_result
        
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}")
            return {
                "success": False,
                "message": f"Error executing tool: {str(e)}",
                "error": str(e)
            }
    
    def _transform_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply transformations to parameters before calling the API method.
        
        Args:
            tool_name: Name of the tool being executed
            parameters: Original parameters
            
        Returns:
            Transformed parameters
        """
        # Get transforms for this tool
        transforms = self._param_transforms.get(tool_name, {})
        
        if not transforms:
            # No transformations defined, return parameters as is
            return parameters
        
        transformed = {}
        
        # Apply rename transformations
        rename_map = transforms.get("rename", {})
        for param_name, value in parameters.items():
            # If param should be renamed, use the new name, otherwise keep original
            new_name = rename_map.get(param_name, param_name)
            transformed[new_name] = value
        
        # Apply value transformations
        value_transforms = transforms.get("value", {})
        for param_name, transform_info in value_transforms.items():
            if param_name in transformed:
                transform_type = transform_info.get("type")
                
                if transform_type == "boolean_to_string":
                    if isinstance(transformed[param_name], bool):
                        transformed[param_name] = str(transformed[param_name]).lower()
                
                elif transform_type == "string_to_boolean":
                    if isinstance(transformed[param_name], str):
                        transformed[param_name] = transformed[param_name].lower() in ("true", "yes", "1")
                
                # Add other transformation types as needed
        
        return transformed
    
    def _transform_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """
        Transform API result into the standard format expected by the system.
        
        Args:
            tool_name: Name of the tool that was executed
            result: Original result from the API
            
        Returns:
            Standardized result dictionary
        """
        # Get transforms for this tool
        transforms = self._result_transforms.get(tool_name, {})
        
        # If result is already a dictionary, use it as a base
        if isinstance(result, dict):
            transformed = result.copy()
            
            # Ensure required fields are present
            if "success" not in transformed:
                transformed["success"] = "error" not in transformed
            
            if "message" not in transformed:
                if "error" in transformed:
                    transformed["message"] = transformed["error"]
                else:
                    transformed["message"] = f"Tool {tool_name} executed successfully"
            
            # Ensure output field exists
            if "output" not in transformed:
                # Move everything except success and message to output
                output = {k: v for k, v in transformed.items() if k not in ["success", "message", "error"]}
                transformed["output"] = output
            
            return transformed
        
        else:
            # For non-dictionary results, wrap in standard format
            return {
                "success": True,
                "message": f"Tool {tool_name} executed successfully",
                "output": result
            }
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a tool call before execution."""
        # Find the tool definition
        tool_def = None
        for tool in self._tools:
            if tool["name"] == tool_name:
                tool_def = tool
                break
        
        if not tool_def:
            return False, f"Unknown tool: {tool_name}"
        
        # Check required arguments
        for arg_def in tool_def.get("arguments", []):
            if arg_def.get("required", True) and arg_def["name"] not in parameters:
                return False, f"Missing required argument: {arg_def['name']}"
            
            # If the argument is provided, validate its value
            if arg_def["name"] in parameters and parameters[arg_def["name"]] != "<UNK>":
                value = parameters[arg_def["name"]]
                
                # Validate based on domain type
                domain = arg_def.get("domain", {})
                domain_type = domain.get("type", "string")
                
                if domain_type == "numeric_range":
                    try:
                        val = float(value)
                        start, end = domain.get("values", [float('-inf'), float('inf')])
                        if not (start <= val <= end):
                            return False, f"Value {value} for {arg_def['name']} is out of range [{start}, {end}]"
                    except (ValueError, TypeError):
                        return False, f"Invalid numeric value for {arg_def['name']}: {value}"
                
                elif domain_type == "finite":
                    if value not in domain.get("values", []):
                        values_str = ", ".join(str(v) for v in domain.get("values", []))
                        return False, f"Invalid value for {arg_def['name']}: {value}. Expected one of: {values_str}"
                
                elif domain_type == "boolean":
                    if not isinstance(value, bool) and value not in [True, False, "true", "false", "True", "False"]:
                        return False, f"Invalid boolean value for {arg_def['name']}: {value}"
                
                elif domain_type == "list":
                    if not isinstance(value, list):
                        return False, f"Invalid list value for {arg_def['name']}: {value}"
        
        return True, None
    
    def get_domain_updates_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update tool domains based on context."""
        # By default, no domain updates
        return {}
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """Get API-specific context for uncertainty calculation."""
        # Default implementation returns empty context
        return {}
    
    @classmethod
    def from_yaml(cls, api_instance, yaml_path: str) -> 'APIAdapter':
        """
        Create an adapter from a YAML configuration file.
        
        Args:
            api_instance: Instance of the API class to wrap
            yaml_path: Path to the YAML configuration file
            
        Returns:
            Configured API adapter
        """
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            
            return cls(api_instance, config)
        
        except Exception as e:
            logger.exception(f"Error loading API adapter configuration: {e}")
            # Return a minimal adapter
            return cls(api_instance)