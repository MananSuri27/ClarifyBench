# ClarifyBench Evaluation Harness

A clean, minimal evaluation harness for testing LLM-based agents on the ClarifyBench benchmark. Evaluate different models or reasoning approaches on tool-calling tasks that require disambiguation and clarification.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MananSuri27/ClarifyBench.git
cd ClarifyBench

# Install dependencies
pip install -r requirements.txt
```

### Running Evaluation

```bash
# Configure your LLM (choose one):
export OPENAI_API_KEY="sk-..."           # For OpenAI
export VLLM_PORT=8000                    # For local vLLM server


# Run on full benchmark suite
python main.py --agent baseline --data ClarifyBench/ClarifyBench_A/ --output results/

# Calculate metrics
python evaluate.py --results_dir results/ --gt_dir ClarifyBench/ClarifyBench_A/
```

## Supported LLM Backends

The harness supports any OpenAI-compatible API through a unified provider. You can use OpenAI, vLLM, Ollama, or any compatible server.

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
python main.py [...]
```

To configure in `config.py`:
```python
LLM_CONFIG = {
    "model": "gpt-4o-2024-08-06",
    "api_key": "sk-...",  # or set OPENAI_API_KEY env var
    "max_tokens": 2000,
    "temperature": 0.7
}
```

### vLLM

```bash
# Start vLLM server
vllm serve Qwen/Qwen2.5-14B-Instruct --port 8000

# Run harness
export VLLM_PORT=8000
python main.py --agent baseline --data ClarifyBench/ClarifyBench_A/
```

To configure in `config.py`:
```python
LLM_CONFIG = {
    "base_url": "http://localhost:8000/v1",
    "api_key": "EMPTY",
    "max_tokens": 2000,
    "temperature": 0.7
}
```

Similarly, you can configure any OpenAI compatible endpoint.

## Evaluation Guide

This harness is designed for evaluating different approaches to agentic tool use on the ClarifyBench dataset. There are two main evaluation scenarios:

### 1. Evaluating New Reasoning Scaffolds

If you want to test different reasoning approaches, modify the baseline agent implementation. (You should duplicate it, and specify paths correctly in config.py).

**File to modify:** `core/baseline_agent.py`

**Key methods to customize:**

```python
class ReactAgent:
    def _reason(self, request: str, observations: List[str]) -> Tuple[str, str, Any]:
        """
        Main reasoning loop - customize this for different reasoning strategies.

        Current implementation: Simple ReAct (Reason + Act)

        Alternative approaches you could implement:
        - Chain-of-Thought: Add explicit reasoning steps before tool selection
        - Tree-of-Thoughts: Explore multiple reasoning branches
        - Reflexion: Add self-reflection and error correction
        - Plan-and-Execute: Generate full plan before execution

        Returns:
            (reasoning_text, action_type, tool_call_or_question)
        """
        # Your custom reasoning logic here
        pass

    def _handle_error(self, error_result, request, context):
        """Customize error handling and recovery strategies."""
        pass

    # Example helper method to add
    def _should_ask_clarification(self, tool_call, request):
        """Customize when to ask for clarification."""
        pass
```

**Example: Implementing Chain-of-Thought Reasoning**

```python
def _reason(self, request: str, observations: List[str]) -> Tuple[str, str, Any]:
    """Chain-of-Thought: Explicit multi-step reasoning before action."""

    prompt = f"""Break down this request into clear reasoning steps:

REQUEST: {request}
OBSERVATIONS: {observations}

Think step-by-step:
1. What is the user trying to accomplish?
2. What information do I have?
3. What information is missing?
4. What tool should I use next?

Then choose the appropriate tool.

Respond in JSON:
{{
    "step1_goal": "...",
    "step2_have": "...",
    "step3_missing": "...",
    "step4_next_tool": "...",
    "tool_call": {{"tool_name": "...", "arguments": {{}}}}
}}
"""

    response = self._call_llm_with_tracking(prompt, "reasoning")
    # Extract and process response
    # Return (reasoning, action_type, tool_call)
```


### 2. Evaluating New Models

If you want to test different LLMs while keeping the reasoning scaffold the same, you only need to change the model configuration.

**Quick Start - OpenAI Models:**

```bash
# Test with GPT-4
export OPENAI_API_KEY="sk-..."
python main.py --agent baseline --data ClarifyBench/sample/

# Test with GPT-3.5 (to compare performance)
# Edit config.py and change model to "gpt-3.5-turbo"
python main.py --agent baseline --data ClarifyBench/sample/
```

**Quick Start - Local Models via vLLM:/ OpenAI endpoint compatible models**

```bash
# Start your model with vLLM
vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000

# Run evaluation
export VLLM_PORT=8000
python main.py --agent baseline --data ClarifyBench/ClarifyBench_A/
```

**Creating a Custom Model Provider:**

If your model doesn't support OpenAI-compatible API, create a custom provider:

```python
# llm/my_custom_provider.py
from llm.provider import LLMProvider
from typing import Dict, Any

class MyCustomProvider(LLMProvider):
    """Provider for your custom model API."""

    def __init__(self, model_name: str, api_endpoint: str, **kwargs):
        self.model_name = model_name
        self.api_endpoint = api_endpoint
        # Initialize your model client here

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text from your model.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text response
        """
        # Call your model API
        # response = your_api_call(prompt, max_tokens, temperature)
        # return response.text
        pass

    def generate_json(
        self,
        prompt: str,
        response_model: Dict[str, Any],
        max_tokens: int = 2000,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate structured JSON from your model.

        The baseline agent expects JSON responses for tool calling.

        Args:
            prompt: The input prompt
            response_model: Expected JSON schema
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Parsed JSON dictionary
        """
        # Add JSON formatting instructions to prompt
        enhanced_prompt = self.enhance_json_prompt(prompt, response_model)

        # Call your model
        # response_text = your_api_call(enhanced_prompt)

        # Parse and validate JSON
        # return self.safe_parse_json(response_text, default={})
        pass
```

**Register your provider in `config.py`:**

```python
# config.py
from llm.my_custom_provider import MyCustomProvider

def get_llm_provider():
    return MyCustomProvider(
        model_name="my-model-v1",
        api_endpoint="http://localhost:5000/api/generate",
        max_tokens=2000,
        temperature=0.7
    )
```


## Dataset Format

Each ClarifyBench instance is a JSON file with:

```json
{
  "user_query": "Book a flight to Paris next week",
  "user_intent": "Book roundtrip flight from SFO to CDG",
  "ground_truth_tool_calls": [
    {
      "tool_name": "search_flights",
      "parameters": {
        "origin": "SFO",
        "destination": "CDG",
        "date": "2024-01-15"
      }
    }
  ]
}
```

The agent must:
1. Understand the user query
2. Select the correct tools
3. Fill in the correct parameters
4. Ask for clarification if needed


# Cite us

```
@article{suri2025structured,
  title={Structured Uncertainty guided Clarification for LLM Agents},
  author={Suri, Manan and Mathur, Puneet and Lipka, Nedim and Dernoncourt, Franck and Rossi, Ryan A and Manocha, Dinesh},
  journal={arXiv preprint arXiv:2511.08798},
  year={2025}
}
```