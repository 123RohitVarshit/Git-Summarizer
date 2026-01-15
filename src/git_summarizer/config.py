"""Configuration management for Git-Summarizer."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class LLMProvider(Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


@dataclass
class Config:
    """Configuration settings for Git-Summarizer."""
    
    # API Keys
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    openrouter_api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    
    # Defaults
    default_days: int = field(default_factory=lambda: int(os.getenv("GIT_SUMMARIZER_DAYS", "7")))
    max_diff_chars: int = field(default_factory=lambda: int(os.getenv("GIT_SUMMARIZER_MAX_DIFF", "8000")))
    
    # Model settings
    gemini_model: str = field(default_factory=lambda: os.getenv("GIT_SUMMARIZER_GEMINI_MODEL", "gemini-flash-latest"))
    openrouter_model: str = field(default_factory=lambda: os.getenv("GIT_SUMMARIZER_OPENROUTER_MODEL", "xiaomi/mimo-v2-flash:free"))
    
    # Provider preference
    preferred_provider: str = field(default_factory=lambda: os.getenv("GIT_SUMMARIZER_PROVIDER", "auto"))
    
    # Slack integration
    slack_webhook_url: str = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL", ""))
    
    def get_active_provider(self) -> LLMProvider:
        """Determine which LLM provider to use based on config and available keys."""
        if self.preferred_provider == "gemini" and self.gemini_api_key:
            return LLMProvider.GEMINI
        elif self.preferred_provider == "openrouter" and self.openrouter_api_key:
            return LLMProvider.OPENROUTER
        elif self.preferred_provider == "auto":
            # Auto-select: prioritize OpenRouter (free tier available)
            if self.openrouter_api_key:
                return LLMProvider.OPENROUTER
            elif self.gemini_api_key:
                return LLMProvider.GEMINI
        
        # No valid provider found
        raise ValueError(
            "No LLM API key configured. Please set one of:\n"
            "  • OPENROUTER_API_KEY (get free at https://openrouter.ai/keys) [RECOMMENDED]\n"
            "  • GEMINI_API_KEY (get at https://aistudio.google.com/apikey)"
        )
    
    def validate(self) -> None:
        """Validate that at least one API key is configured."""
        self.get_active_provider()  # This will raise if no provider is available
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment."""
        return cls()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config
