"""
Unified OpenAI-compatible provider for multiple backends.
Supports: OpenAI, vLLM, Ollama (with OpenAI compatibility), and any OpenAI-compatible server.
"""

from typing import Dict, List, Any, Optional
import logging
import os
from openai import OpenAI
from .provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    """Unified provider for OpenAI-compatible APIs (OpenAI, vLLM, Ollama, etc.)."""

    def __init__(
        self,
        model_name: str = None,
        base_url: str = None,
        api_key: str = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        Initialize OpenAI-compatible provider.

        Args:
            model_name: Model name (if None, auto-detect from server)
            base_url: Base URL for API (None = OpenAI default, or set for vLLM/Ollama)
            api_key: API key (required for OpenAI, use "EMPTY" for local servers)
            max_tokens: Default max tokens
            temperature: Default temperature
        """
        # Check environment variables
        base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        api_key = api_key or os.environ.get("OPENAI_API_KEY", "EMPTY")

        # Check for VLLM_PORT environment variable (backward compatibility)
        vllm_port = os.environ.get("VLLM_PORT")
        if vllm_port and not base_url:
            base_url = f"http://localhost:{vllm_port}/v1"
            logger.info(f"Using VLLM_PORT from environment: {vllm_port}")

        # Initialize OpenAI client
        if base_url:
            self.client = OpenAI(base_url=base_url, api_key=api_key)
            logger.info(f"Initialized OpenAI-compatible provider at {base_url}")
        else:
            self.client = OpenAI(api_key=api_key)
            logger.info("Initialized OpenAI provider")

        # Auto-detect model name if not provided
        if model_name is None:
            try:
                models = self.client.models.list()
                model_name = models.data[0].id if models.data else "gpt-4"
                logger.info(f"Auto-detected model: {model_name}")
            except Exception as e:
                logger.warning(f"Could not auto-detect model: {e}. Using default.")
                model_name = "gpt-4"

        self.model_name = model_name
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """Generate text from the LLM."""
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ""

    def generate_json(
        self,
        prompt: str,
        response_model: Dict[str, Any],
        max_tokens: int = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """Generate structured JSON from the LLM."""
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature if temperature is not None else 0.2

        # Enhance prompt with JSON instructions
        enhanced_prompt = self.enhance_json_prompt(prompt, response_model)

        # Add system prompt for JSON
        system_prompt = """You are a helpful assistant that always responds with valid JSON.
Your responses must be properly formatted JSON objects only, with no additional text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_text = response.choices[0].message.content
            return self.safe_parse_json(response_text, default={})

        except Exception as e:
            logger.error(f"Error generating JSON: {e}")
            return {}


def create_openai_compatible_provider(config: Dict[str, Any]) -> OpenAICompatibleProvider:
    """
    Factory function to create provider from config.

    Args:
        config: Configuration dictionary with keys:
            - model: Model name (optional, auto-detected if not provided)
            - base_url: API base URL (optional, defaults to OpenAI)
            - api_key: API key (optional, uses OPENAI_API_KEY env var)
            - max_tokens: Maximum tokens (default: 2000)
            - temperature: Sampling temperature (default: 0.7)

    Returns:
        OpenAICompatibleProvider instance
    """
    return OpenAICompatibleProvider(
        model_name=config.get("model"),
        base_url=config.get("base_url"),
        api_key=config.get("api_key"),
        max_tokens=config.get("max_tokens", 2000),
        temperature=config.get("temperature", 0.7)
    )
