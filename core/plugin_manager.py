import os
import importlib
import yaml
import logging
from typing import Dict, List, Any, Optional
import sys

# Need to ensure the plugins directory is in the Python path
plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
if plugins_dir not in sys.path:
    sys.path.append(plugins_dir)

from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class PluginManager:
    """Manager for API plugins.
    
    This class handles loading, discovery, and management of API plugins.
    It serves as the central access point for all plugin-related operations.
    """
    
    def __init__(self, plugin_config_dir: str = "config/plugins"):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_config_dir: Directory containing plugin configurations
        """
        self.plugin_config_dir = plugin_config_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.tool_to_plugin_map: Dict[str, str] = {}
        
        # Create the config directory if it doesn't exist
        os.makedirs(plugin_config_dir, exist_ok=True)
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin directly (without loading from config).
        
        Args:
            plugin: Plugin instance to register
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Register the plugin by name
            self.plugins[plugin.name] = plugin
            
            # Update the tool-to-plugin map (including virtual tools)
            self._update_tool_to_plugin_map(plugin)
                    
            logger.info(f"Successfully registered plugin: {plugin.name}")
            return True
        except Exception as e:
            logger.exception(f"Error registering plugin: {e}")
            return False
    
    def _update_tool_to_plugin_map(self, plugin: BasePlugin) -> None:
        """
        Update the tool-to-plugin map for a specific plugin.
        
        Args:
            plugin: Plugin to update mapping for
        """
        # Get all tools (regular + virtual) from the plugin
        all_tools = plugin.get_all_tools() if hasattr(plugin, 'get_all_tools') else plugin.get_tools()
        
        for tool in all_tools:
            tool_name = tool.get("name")
            if tool_name:
                self.tool_to_plugin_map[tool_name] = plugin.name
                logger.debug(f"Mapped tool '{tool_name}' to plugin '{plugin.name}'")
    
    def refresh_tool_mapping(self) -> None:
        """
        Refresh the tool-to-plugin mapping for all plugins.
        
        This should be called after virtual tools are added to plugins.
        """
        logger.info("Refreshing tool-to-plugin mapping")
        self.tool_to_plugin_map.clear()
        
        for plugin in self.plugins.values():
            self._update_tool_to_plugin_map(plugin)
        
        logger.info(f"Refreshed mapping for {len(self.tool_to_plugin_map)} tools")
    
    def add_virtual_tool_to_plugin(self, plugin_name: str, tool_definition: Dict[str, Any]) -> bool:
        """
        Add a virtual tool to a specific plugin and update mappings.
        
        Args:
            plugin_name: Name of the plugin to add the tool to
            tool_definition: Tool definition dictionary
            
        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin '{plugin_name}' not found")
            return False
        
        # Add the virtual tool to the plugin
        if hasattr(plugin, '_add_virtual_tool'):
            plugin._add_virtual_tool(tool_definition)
            
            # Update the tool mapping for this plugin
            self._update_tool_to_plugin_map(plugin)
            
            logger.info(f"Added virtual tool '{tool_definition.get('name')}' to plugin '{plugin_name}'")
            return True
        else:
            logger.error(f"Plugin '{plugin_name}' does not support virtual tools")
            return False
    
    def add_virtual_tool_to_any_plugin(self, tool_definition: Dict[str, Any]) -> bool:
        """
        Add a virtual tool to the first available plugin that supports virtual tools.
        
        Args:
            tool_definition: Tool definition dictionary
            
        Returns:
            True if successful, False otherwise
        """
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, '_add_virtual_tool'):
                return self.add_virtual_tool_to_plugin(plugin_name, tool_definition)
        
        logger.error("No plugins support virtual tools")
        return False
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin by name from configuration.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            True if successful, False otherwise
        """
        # Try to load plugin configuration
        config_path = os.path.join(self.plugin_config_dir, f"{plugin_name}.yaml")
        if not os.path.exists(config_path):
            logger.error(f"Plugin configuration not found: {config_path}")
            return False
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            module_path = config.get("module_path")
            class_name = config.get("class_name")
            
            if not module_path or not class_name:
                logger.error(f"Invalid plugin configuration: {config_path}")
                return False
                
            # Import the plugin module
            module = importlib.import_module(module_path)
            
            # Get the plugin class
            plugin_class = getattr(module, class_name)
            
            # Create an instance of the plugin
            plugin = plugin_class()
            
            # Register the plugin
            return self.register_plugin(plugin)
            
        except Exception as e:
            logger.exception(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> None:
        """Load all plugins from the configuration directory."""
        if not os.path.exists(self.plugin_config_dir):
            logger.warning(f"Plugin configuration directory not found: {self.plugin_config_dir}")
            return
            
        for filename in os.listdir(self.plugin_config_dir):
            if filename.endswith(".yaml"):
                plugin_name = os.path.splitext(filename)[0]
                self.load_plugin(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def get_plugin_for_tool(self, tool_name: str) -> Optional[BasePlugin]:
        """
        Get the plugin that provides a specific tool (including virtual tools).
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Plugin instance or None if no plugin provides this tool
        """
        plugin_name = self.tool_to_plugin_map.get(tool_name)
        if plugin_name:
            return self.plugins.get(plugin_name)
        
        # If not found in map, try to find it by checking all plugins
        # This handles cases where virtual tools were added after initial mapping
        for plugin in self.plugins.values():
            if hasattr(plugin, 'get_all_tools'):
                all_tools = plugin.get_all_tools()
            else:
                all_tools = plugin.get_tools()
            
            tool_names = {tool.get("name") for tool in all_tools}
            if tool_name in tool_names:
                # Update the mapping for future use
                self.tool_to_plugin_map[tool_name] = plugin.name
                return plugin
        
        return None
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools from all loaded plugins (including virtual tools).
        
        Returns:
            List of all tool definitions from all plugins
        """
        all_tools = []
        for plugin in self.plugins.values():
            # Use get_all_tools if available (includes virtual tools), otherwise fall back
            if hasattr(plugin, 'get_all_tools'):
                all_tools.extend(plugin.get_all_tools())
            else:
                all_tools.extend(plugin.get_tools())
        return all_tools
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool through its plugin (with virtual tool support).
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Result of the tool execution
        """
        plugin = self.get_plugin_for_tool(tool_name)
        if not plugin:
            return {
                "success": False,
                "message": f"No plugin found for tool: {tool_name}",
                "error": "PLUGIN_NOT_FOUND"
            }
        
        # Use virtual tool support if available
        if hasattr(plugin, 'execute_tool_with_virtual_support'):
            return plugin.execute_tool_with_virtual_support(tool_name, parameters)
        else:
            # Fallback to regular execution
            return plugin.execute_tool(tool_name, parameters)
    
    def get_all_prompt_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get all prompt templates from all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to their prompt templates
        """
        all_templates = {}
        for plugin_name, plugin in self.plugins.items():
            all_templates[plugin_name] = plugin.get_prompt_templates()
        return all_templates
    
    def format_template(
        self, 
        plugin_name: str, 
        template_name: str, 
        **kwargs
    ) -> Optional[str]:
        """
        Format a prompt template from a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            template_name: Name of the template
            **kwargs: Format arguments
            
        Returns:
            Formatted template or None if not found
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return None
            
        templates = plugin.get_prompt_templates()
        if template_name not in templates:
            return None
            
        # Get the template
        template = templates[template_name]
        
        # Check if the template has a placeholder for conversation history
        if "{conversation_history}" in template and "conversation_history" not in kwargs:
            # Add empty conversation history if not provided
            kwargs["conversation_history"] = ""
            
        # Format the template
        try:
            return template.format(**kwargs)
        except Exception as e:
            logger.error(f"Error formatting template {template_name} from plugin {plugin_name}: {e}")
            return None
    
    def get_virtual_tools_summary(self) -> Dict[str, List[str]]:
        """
        Get a summary of virtual tools by plugin.
        
        Returns:
            Dictionary mapping plugin names to lists of their virtual tool names
        """
        summary = {}
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, '_virtual_tools'):
                virtual_tool_names = [tool["name"] for tool in plugin._virtual_tools]
                if virtual_tool_names:
                    summary[plugin_name] = virtual_tool_names
        return summary