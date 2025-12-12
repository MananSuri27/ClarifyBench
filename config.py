"""
Configuration for the agentic disambiguation system.
"""

from typing import Dict, Any, List

# LLM Configuration
# Example configurations for different backends:

# For OpenAI:
# LLM_CONFIG = {
#     "model": "gpt-4o-2024-08-06",
#     "api_key": "sk-...",  # or set OPENAI_API_KEY env var
#     "max_tokens": 2000,
#     "temperature": 0.7
# }

# For vLLM:
# LLM_CONFIG = {
#     "base_url": "http://localhost:8000/v1",
#     "api_key": "EMPTY",
#     "max_tokens": 2000,
#     "temperature": 0.7
# }
# Or set VLLM_PORT=8000 environment variable



# Default configuration (uses environment variables)
LLM_CONFIG = {
    "model": "gpt-4o-2024-08-06",
    "max_tokens": 2000,
    "temperature": 0.7
}

# Simulation Configuration
SIMULATION_CONFIG = {
    "data_dir": "ClarifyBench/sample",  # Directory for simulation data
    "results_dir": "results",  # Directory for simulation results
    "log_dir": "logs",  # Directory for logs
    "max_turns": 10,  # Maximum number of conversation turns
    "max_clarifications_per_request": 5  # Maximum clarifications per request
}

# Experiment Configuration
EXPERIMENT_CONFIG = {
    "base_data_dir": "ClarifyBench",  # Relative to project root
    "experiments_dir": "experiments",  # Directory for experiments
    "datasets": {
        "I": "ClarifyBench_I",
        "A": "ClarifyBench_A",
        "E": "ClarifyBench_E",
    },
    "agents": {
        "baseline": "core.baseline_agent"
    }
}

