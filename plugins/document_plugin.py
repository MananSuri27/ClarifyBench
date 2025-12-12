import logging
from typing import Dict, List, Any, Optional, Tuple
import copy
from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class DocumentPlugin(BasePlugin):
    """Plugin for document-related operations.
    
    This plugin provides tools for working with PDF documents, including
    viewing, editing, converting, and manipulating PDF files.
    """
    
    def __init__(self):
        """Initialize the document plugin."""
        super().__init__()
        self._tools = self._load_tool_definitions()
        self._current_context = {
            "number_of_pages": 1,  # Default, will be updated from context
            "pdf_name": "document.pdf"  # Default, will be updated from context
        }
        
        # Cache for dynamic domains - invalidated when document state changes
        self._domain_cache = None
        
        # Only operations that can change page count
        self._page_changing_operations = {
            'delete_page', 'delete_page_range', 'add_page_with_text'
        }
    
    @property
    def name(self) -> str:
        return "document"
    
    @property
    def description(self) -> str:
        return "Plugin for document-related operations like viewing, editing, and converting PDFs."
    
    def _invalidate_domain_cache(self):
        """Invalidate the domain cache when document state changes."""
        self._domain_cache = None
    
    def _update_dynamic_domains(self) -> Dict[str, Any]:
        """Update domains based on current document state."""
        if self._domain_cache is not None:
            return self._domain_cache
        
        try:
            updates = {}
            num_pages = self._current_context.get("number_of_pages", 1)
            
            # Only page-related parameters need dynamic updates
            page_operations = [
                ("add_comment", "page_num"),
                ("delete_page", "page_num"), 
                ("add_signature", "page_num"),
                ("add_page_with_text", "page_num"),
                ("redact_page_range", "start"), ("redact_page_range", "end"),
                ("redact_text", "start"), ("redact_text", "end"),
                ("highlight_text", "start"), ("highlight_text", "end"),
                ("underline_text", "start"), ("underline_text", "end"),
                ("extract_pages", "start"), ("extract_pages", "end"),
                ("delete_page_range", "start"), ("delete_page_range", "end")
            ]
            
            for tool, param in page_operations:
                updates[f"{tool}.{param}"] = {
                    "type": "numeric_range",
                    "values": [1, num_pages]
                }
            
            # Cache the result
            self._domain_cache = updates
            return updates
            
        except Exception as e:
            logger.error(f"Error updating dynamic domains: {e}")
            return {}
    
    def initialize_from_config(self, config_data: Dict[str, Any]) -> bool:
        """Initialize the document plugin from configuration data."""
        if "DocumentPlugin" in config_data:
            doc_config = config_data["DocumentPlugin"]
            self._current_context.update({
                k: v for k, v in doc_config.items() 
                if k in ["number_of_pages", "pdf_name"]
            })
            self._invalidate_domain_cache()  # Invalidate cache after loading
            return True
        return False
    
    def _load_tool_definitions(self) -> List[Dict[str, Any]]:
        """Load tool definitions for PDF operations."""
        # Complete list of tools from PDF_TOOLS_CONFIG
        return [
            {
                "name": "duplicate",
                "description": "Create a duplicate of the PDF file",
                "arguments": [
                    {
                        "name": "output_filename",
                        "description": "Name of the output file",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "rename",
                "description": "Rename the PDF file",
                "arguments": [
                    {
                        "name": "output_filename",
                        "description": "New name for the file",
                        "domain": {
                            "type": "string",
                            "importance": 0.8
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "search",
                "description": "Search for content in the PDF",
                "arguments": [
                    {
                        "name": "object_name",
                        "description": "Term or type of object to search for",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "count_pages",
                "description": "Count the number of pages in the PDF",
                "arguments": []
            },
            {
                "name": "compress_file",
                "description": "Compress the PDF file",
                "arguments": [
                    {
                        "name": "output_filename",
                        "description": "Name of the compressed output file",
                        "domain": {
                            "type": "string",
                            "importance": 0.6
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "convert",
                "description": "Convert the PDF to another format",
                "arguments": [
                    {
                        "name": "format",
                        "description": "Target format for conversion",
                        "domain": {
                            "type": "finite",
                            "values": ["pptx", "doc", "png", "jpeg", "tiff"],
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "output_filename",
                        "description": "Name of the output file",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "zip",
                        "description": "Whether to zip the output (for image formats)",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.4
                        },
                        "required": False,
                        "default": False
                    }
                ]
            },
            {
                "name": "add_comment",
                "description": "Add a comment to a page",
                "arguments": [
                    {
                        "name": "page_num",
                        "description": "Page number to add comment to",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "coordinates",
                        "description": "Coordinates for the comment [x, y]",
                        "domain": {
                            "type": "list",
                            "importance": 0.6
                        },
                        "required": True
                    },
                    {
                        "name": "font_size",
                        "description": "Font size for the comment",
                        "domain": {
                            "type": "numeric_range",
                            "values": [8, 72],
                            "importance": 0.5
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "redact_page_range",
                "description": "Redact content from a range of pages",
                "arguments": [
                    {
                        "name": "start",
                        "description": "Start page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "end",
                        "description": "End page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "redact_text",
                "description": "Redact specific text in a range of pages",
                "arguments": [
                    {
                        "name": "start",
                        "description": "Start page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "end",
                        "description": "End page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "object_name",
                        "description": "List of text to redact. PLEASE FORMAT WHATEVER CONTENT YOU GET AS A PYTHON LIST [...].",
                        "domain": {
                            "type": "list",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "highlight_text",
                "description": "Highlight specific text in a range of pages",
                "arguments": [
                    {
                        "name": "start",
                        "description": "Start page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "end",
                        "description": "End page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "object_name",
                        "description": "List of text to highlight. PLEASE FORMAT WHATEVER CONTENT YOU GET AS A PYTHON LIST [...].",
                        "domain": {
                            "type": "list",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "underline_text",
                "description": "Underline specific text in a range of pages",
                "arguments": [
                    {
                        "name": "start",
                        "description": "Start page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "end",
                        "description": "End page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "object_name",
                        "description": "List of text to underline. PLEASE FORMAT WHATEVER CONTENT YOU GET AS A PYTHON LIST [...].",
                        "domain": {
                            "type": "list",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "extract_pages",
                "description": "Extract a range of pages to a new file",
                "arguments": [
                    {
                        "name": "start",
                        "description": "Start page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "end",
                        "description": "End page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "delete_page",
                "description": "Delete a specific page",
                "arguments": [
                    {
                        "name": "page_num",
                        "description": "Page number to delete",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "delete_page_range",
                "description": "Delete a range of pages",
                "arguments": [
                    {
                        "name": "start",
                        "description": "Start page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "end",
                        "description": "End page number (inclusive)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "add_signature",
                "description": "Add a signature to a page",
                "arguments": [
                    {
                        "name": "page_num",
                        "description": "Page number to add signature to",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.9,
                            "data_dependent": True
                        },
                        "required": True
                    },
                    {
                        "name": "position",
                        "description": "Position for the signature",
                        "domain": {
                            "type": "finite",
                            "values": ["top-left", "top-middle", "top-right", "bottom-right", "bottom-left", "bottom-middle"],
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "overwrite",
                        "description": "Whether to overwrite the original file",
                        "domain": {
                            "type": "boolean",
                            "importance": 0.7
                        },
                        "required": True
                    },
                    {
                        "name": "output_pathname",
                        "description": "Name of the output file if not overwriting",
                        "domain": {
                            "type": "string",
                            "importance": 0.7
                        },
                        "required": False,
                        "default": None
                    }
                ]
            },
            {
                "name": "add_page_with_text",
                "description": "Add a new page with text content",
                "arguments": [
                    {
                        "name": "text_content",
                        "description": "Text content for the new page",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "font_size",
                        "description": "Font size for the text",
                        "domain": {
                            "type": "numeric_range",
                            "values": [8, 72],
                            "importance": 0.6
                        },
                        "required": True
                    },
                    {
                        "name": "page_num",
                        "description": "Page number to insert at (1-indexed)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [1, 1],  # Will be updated dynamically
                            "importance": 0.8,
                            "data_dependent": True
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "add_watermark",
                "description": "Add a watermark to all pages",
                "arguments": [
                    {
                        "name": "watermark_text",
                        "description": "Text for the watermark",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    },
                    {
                        "name": "transparency",
                        "description": "Transparency level (0-1)",
                        "domain": {
                            "type": "numeric_range",
                            "values": [0.0, 1.0],
                            "importance": 0.6
                        },
                        "required": True
                    }
                ]
            },
            {
                "name": "add_password",
                "description": "Password-protect the PDF",
                "arguments": [
                    {
                        "name": "password",
                        "description": "Password for protection",
                        "domain": {
                            "type": "string",
                            "importance": 0.9
                        },
                        "required": True
                    }
                ]
            }
        ]
    
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
        
        # Validate the tool call
        is_valid, error = self.validate_tool_call(tool_name, casted_params)
        if not is_valid:
            return {
                "success": False,
                "message": f"Validation failed: {error}",
                "error": "VALIDATION_ERROR"
            }
        
        # Execute the tool
        try:
            result = self._execute_tool_implementation(tool_name, casted_params)
            
            # Invalidate domain cache if this was a page-changing operation
            if tool_name in self._page_changing_operations:
                self._invalidate_domain_cache()
                # Update page count if needed
                if tool_name == "add_page_with_text":
                    self._current_context["number_of_pages"] += 1
                elif tool_name == "delete_page":
                    self._current_context["number_of_pages"] = max(1, self._current_context["number_of_pages"] - 1)
                elif tool_name == "delete_page_range":
                    start = casted_params.get("start", 1)
                    end = casted_params.get("end", 1)
                    pages_deleted = end - start + 1
                    self._current_context["number_of_pages"] = max(1, self._current_context["number_of_pages"] - pages_deleted)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}")
            return {
                "success": False,
                "message": f"Error executing tool: {str(e)}",
                "error": "EXECUTION_ERROR"
            }
    
    def _execute_tool_implementation(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to execute tools with mock implementations."""
        # This would call actual PDF operations in a real implementation
        # For now, return a mock successful result with appropriate messaging
        if tool_name == "duplicate":
            output_filename = parameters.get("output_filename", "")
            return {
                "success": True,
                "message": f"Successfully duplicated {self._current_context['pdf_name']} to {output_filename}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "rename":
            output_filename = parameters.get("output_filename", "")
            return {
                "success": True,
                "message": f"Successfully renamed {self._current_context['pdf_name']} to {output_filename}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "search":
            object_name = parameters.get("object_name", "")
            return {
                "success": True,
                "message": f"Found '{object_name}' in {self._current_context['pdf_name']}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "results": ["page 1", "page 3"]  # Mock results
                }
            }
        
        elif tool_name == "count_pages":
            return {
                "success": True,
                "message": f"{self._current_context['pdf_name']} has {self._current_context['number_of_pages']} pages",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "page_count": self._current_context['number_of_pages']
                }
            }
        
        elif tool_name == "compress_file":
            output_filename = parameters.get("output_filename", f"compressed_{self._current_context['pdf_name']}")
            return {
                "success": True,
                "message": f"Successfully compressed {self._current_context['pdf_name']} to {output_filename}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "convert":
            format_type = parameters.get("format", "")
            output_filename = parameters.get("output_filename", "")
            zip_output = parameters.get("zip", False)
            
            return {
                "success": True,
                "message": f"Successfully converted {self._current_context['pdf_name']} to {format_type} format as {output_filename}{' (zipped)' if zip_output else ''}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "add_comment":
            page_num = parameters.get("page_num", 1)
            coordinates = parameters.get("coordinates", [0, 0])
            font_size = parameters.get("font_size", 12)
            
            return {
                "success": True,
                "message": f"Successfully added comment on page {page_num} at position {coordinates} with font size {font_size}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "redact_page_range":
            start = parameters.get("start", 1)
            end = parameters.get("end", 1)
            
            return {
                "success": True,
                "message": f"Successfully redacted content from pages {start}-{end}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "redact_text":
            start = parameters.get("start", 1)
            end = parameters.get("end", 1)
            object_name = parameters.get("object_name", [])
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "redacted.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully redacted text {object_name} from pages {start}-{end} and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "highlight_text":
            start = parameters.get("start", 1)
            end = parameters.get("end", 1)
            object_name = parameters.get("object_name", [])
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "highlighted.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully highlighted text {object_name} from pages {start}-{end} and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "underline_text":
            start = parameters.get("start", 1)
            end = parameters.get("end", 1)
            object_name = parameters.get("object_name", [])
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "underlined.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully underlined text {object_name} from pages {start}-{end} and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "extract_pages":
            start = parameters.get("start", 1)
            end = parameters.get("end", 1)
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "extracted.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully extracted pages {start}-{end} and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "delete_page":
            page_num = parameters.get("page_num", 1)
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "modified.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully deleted page {page_num} and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "delete_page_range":
            start = parameters.get("start", 1)
            end = parameters.get("end", 1)
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "modified.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully deleted pages {start}-{end} and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "add_signature":
            page_num = parameters.get("page_num", 1)
            position = parameters.get("position", "bottom-right")
            overwrite = parameters.get("overwrite", False)
            output_pathname = parameters.get("output_pathname", "signed.pdf")
            
            output_msg = f"to {output_pathname}" if not overwrite else "in place"
            
            return {
                "success": True,
                "message": f"Successfully added signature to page {page_num} at {position} position and saved {output_msg}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "add_page_with_text":
            text_content = parameters.get("text_content", "")
            font_size = parameters.get("font_size", 12)
            page_num = parameters.get("page_num", 1)
            
            return {
                "success": True,
                "message": f"Successfully added new page with text at position {page_num} with font size {font_size}",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "add_watermark":
            watermark_text = parameters.get("watermark_text", "")
            transparency = parameters.get("transparency", 0.5)
            
            return {
                "success": True,
                "message": f"Successfully added watermark '{watermark_text}' with transparency {transparency} to all pages",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        elif tool_name == "add_password":
            password = parameters.get("password", "")
            
            return {
                "success": True,
                "message": f"Successfully password-protected the PDF with the provided password",
                "output": {
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            }
        
        # Default case for tools not explicitly handled
        return {
            "success": True,
            "message": f"Executed {tool_name} with parameters {parameters}",
            "output": {
                "tool_name": tool_name,
                "parameters": parameters
            }
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
                        
                        # Get dynamic domain values if data_dependent
                        if domain.get("data_dependent"):
                            dynamic_domains = self._update_dynamic_domains()
                            domain_key = f"{tool_name}.{arg_def['name']}"
                            if domain_key in dynamic_domains:
                                start, end = dynamic_domains[domain_key].get("values", [1, 1])
                            else:
                                start, end = domain.get("values", [1, 1])
                        else:
                            start, end = domain.get("values", [1, 1])
                        
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
        # Initialize from config if available
        if "initial_config" in context and hasattr(self, "initialize_from_config"):
            self.initialize_from_config(context["initial_config"])
        
        # Update the current context
        if "number_of_pages" in context:
            old_pages = self._current_context.get("number_of_pages", 1)
            new_pages = context["number_of_pages"]
            self._current_context["number_of_pages"] = new_pages
            
            # Only invalidate cache if page count actually changed
            if old_pages != new_pages:
                self._invalidate_domain_cache()
        
        if "pdf_name" in context:
            self._current_context["pdf_name"] = context["pdf_name"]
        
        # Return dynamic domain updates
        return self._update_dynamic_domains()
    
    def get_uncertainty_context(self) -> Dict[str, Any]:
        """Get document-specific context for uncertainty calculation."""
        return {
            "number_of_pages": self._current_context.get("number_of_pages", 1),
            "pdf_name": self._current_context.get("pdf_name", "document.pdf")
        }
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get document-specific prompt templates."""
        return {
            "tool_selection": """
You are an AI assistant that helps users with document operations.

Conversation history:
{conversation_history}

User query: "{user_query}"

Available tools:
{tool_descriptions}

Please reason step-by-step about what the user is asking for:
1. What is the user trying to accomplish with the document?
2. What information do we already have from the conversation history?
3. What tools would help accomplish this task?
4. What parameters are needed for each tool?
5. Do we have enough information to execute these tools, or do we need to ask clarifying questions?

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
""",
            "question_generation": """
You are an AI assistant that helps users with document operations.

Conversation history:
{conversation_history}

Original user query: "{user_query}"

I've determined that the following tool calls are needed, but some arguments are uncertain:

Tool Calls:
{tool_calls}

Uncertain Arguments:
{uncertain_args}

Your task is to generate clarification questions that would help resolve the uncertainty about specific arguments.

Instructions:
1. Generate questions that are clear, specific, and directly address the uncertain arguments
2. Each question should target one or more specific arguments
3. Questions should be conversational and easy for a user to understand
4. For each question, specify which tool and argument(s) it aims to clarify

Return your response as a JSON object with the following structure:
{{
  "questions": [
    {{
      "question": "A clear question to ask the user",
      "target_args": [["tool_name", "arg_name"], ["tool_name", "other_arg_name"]]
    }}
  ]
}}
"""
        }