"""
AI Service Configuration for Phase 2.2 Learning Management

Supports multiple AI providers:
- Anthropic Claude API (primary)
- OpenAI-compatible API (e.g., Zhipu GLM as fallback)
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


class AIProvider(str, Enum):
    """AI Provider options"""
    ANTHROPIC = "anthropic"
    OPENAI_COMPATIBLE = "openai"  # For Zhipu GLM and other OpenAI-compatible APIs


class AIServiceConfig(BaseModel):
    """AI Service Configuration"""

    provider: AIProvider = AIProvider.OPENAI_COMPATIBLE
    model: str = "glm-4.7"
    max_tokens: int = 1000
    temperature: float = 0.7

    # Anthropic Claude API settings
    anthropic_api_key: Optional[str] = None

    # OpenAI-compatible API settings (e.g., Zhipu GLM)
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AIServiceConfig":
        """Load configuration from environment variables"""
        provider_str = os.getenv("AI_PROVIDER", "openai").lower()

        # Map provider string to enum
        if provider_str == "anthropic":
            provider = AIProvider.ANTHROPIC
        else:
            provider = AIProvider.OPENAI_COMPATIBLE

        return cls(
            provider=provider,
            model=os.getenv("AI_MODEL", "glm-4.7"),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
        )

    def get_client(self):
        """Get AI client based on provider"""
        if self.provider == AIProvider.ANTHROPIC:
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")

            import anthropic

            return anthropic.Anthropic(api_key=self.anthropic_api_key)

        elif self.provider == AIProvider.OPENAI_COMPATIBLE:
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI-compatible provider")

            from openai import OpenAI

            return OpenAI(
                api_key=self.openai_api_key,
                base_url=self.openai_base_url,
            )

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


# Global AI service configuration instance
ai_config = AIServiceConfig.from_env()


def get_ai_service():
    """Get AI service client (convenience function)"""
    return ai_config.get_client()


def test_ai_connection() -> dict:
    """
    Test AI service connection

    Returns:
        dict with keys:
        - success (bool): Whether the connection test was successful
        - provider (str): AI provider used
        - model (str): Model name
        - error (str, optional): Error message if test failed
    """
    config = AIServiceConfig.from_env()

    try:
        client = config.get_client()

        # Simple test message
        if config.provider == AIProvider.ANTHROPIC:
            response = client.messages.create(
                model=config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
            )
            test_response = response.content[0].text

        else:  # OpenAI-compatible
            response = client.chat.completions.create(
                model=config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
            )
            test_response = response.choices[0].message.content

        return {
            "success": True,
            "provider": config.provider.value,
            "model": config.model,
            "test_response": test_response,
        }

    except Exception as e:
        return {
            "success": False,
            "provider": config.provider.value,
            "model": config.model,
            "error": str(e),
        }


if __name__ == "__main__":
    """Test AI connection when run as script"""
    import json

    result = test_ai_connection()
    print(json.dumps(result, indent=2, ensure_ascii=False))
