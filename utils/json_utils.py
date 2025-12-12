import json
import logging
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)

def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON as a dictionary
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return {}

def save_json(data: Dict[str, Any], file_path: str, pretty: bool = True) -> bool:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        file_path: Path to the output file
        pretty: Whether to format the JSON for readability
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(file_path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False

def merge_json_objects(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two JSON objects.
    
    Args:
        obj1: First object
        obj2: Second object
        
    Returns:
        Merged object
    """
    result = obj1.copy()
    
    for key, value in obj2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json_objects(result[key], value)
        else:
            result[key] = value
    
    return result

def extract_fields(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """
    Extract specific fields from a JSON object.
    
    Args:
        data: Source data
        fields: List of field names to extract
        
    Returns:
        Dictionary with extracted fields
    """
    result = {}
    
    for field in fields:
        if field in data:
            result[field] = data[field]
    
    return result

def pretty_print_json(data: Dict[str, Any]) -> str:
    """
    Convert data to a pretty-printed JSON string.
    
    Args:
        data: Data to format
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2)