from typing import Dict, List, Any, Optional
import json
import os
import logging
import glob

logger = logging.getLogger(__name__)

class SimulationDataLoader:
    """Class for loading simulation data from JSON files."""
    
    def __init__(self, data_dir: str = "simulation_data"):
        """
        Initialize a simulation data loader.
        
        Args:
            data_dir: Directory containing simulation data files
        """
        self.data_dir = data_dir
        
        # Ensure the data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def load_simulation_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load simulation data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded simulation data
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Validate the data structure
            self._validate_simulation_data(data)
            
            return data
            
        except Exception as e:
            logger.exception(f"Error loading simulation data from {file_path}")
            # Return an empty data structure with minimal required fields
            return {
                "user_query": "",
                "user_intent": "",
                "ground_truth_tool_calls": [],
                "number_of_pages": 1,
                "pdf_name": "unknown.pdf",
                "potential_follow_ups": []
            }

    def _validate_simulation_data(self, data: Dict[str, Any]) -> None:
        """
        Validate simulation data structure.
        
        Args:
            data: Data to validate
            
        Raises:
            ValueError: If the data is invalid
        """
        # Allow either user_query or initial_query as the main query field
        if "user_query" not in data and "initial_query" not in data:
            raise ValueError(f"Missing required field: user_query or initial_query")
        
        # If initial_query is used, normalize to user_query for backward compatibility
        if "initial_query" in data and "user_query" not in data:
            data["user_query"] = data["initial_query"]
        
        # Validate ground truth tool calls
        tool_calls = data.get("ground_truth_tool_calls", [])
        if not isinstance(tool_calls, list):
            raise ValueError("ground_truth_tool_calls must be a list")
            
        for tc in tool_calls:
            if "tool_name" not in tc:
                raise ValueError("Each tool call must have a tool_name")
            if "parameters" not in tc:
                raise ValueError("Each tool call must have parameters")
            
            # If turn information is not present, add it (for backward compatibility)
            if "turn" not in tc:
                tc["turn"] = 1  # Default to turn 1 if not specified
        
        # Validate potential follow-ups if present
        if "potential_follow_ups" in data and not isinstance(data["potential_follow_ups"], list):
            raise ValueError("potential_follow_ups must be a list")
    
    def list_simulation_files(self) -> List[str]:
        """
        List all simulation data files in the data directory.
        
        Returns:
            List of file paths
        """
        pattern = os.path.join(self.data_dir, "*.json")
        return glob.glob(pattern)
    
    def save_simulation_result(
        self,
        simulation_id: str,
        result: Dict[str, Any]
    ) -> str:
        """
        Save simulation result to a JSON file.
        
        Args:
            simulation_id: Unique identifier for the simulation
            result: Simulation result to save
            
        Returns:
            Path to the saved file
        """
        # Create a file path
        file_path = os.path.join(self.data_dir, f"result_{simulation_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Saved simulation result to {file_path}")
            return file_path
            
        except Exception as e:
            logger.exception(f"Error saving simulation result to {file_path}")
            return ""