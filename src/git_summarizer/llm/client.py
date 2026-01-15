"""LLM client for interacting with Gemini and OpenRouter APIs."""

import httpx
from google import genai
from typing import Optional

from ..config import get_config, LLMProvider
from .prompts import Prompts


class LLMClient:
    """Client for LLM interactions supporting multiple providers."""
    
    def __init__(self, api_key: Optional[str] = None, provider: Optional[LLMProvider] = None):
        self.config = get_config()
        
        # Determine provider
        if provider:
            self.provider = provider
        else:
            self.provider = self.config.get_active_provider()
        
        # Set up the appropriate client
        if self.provider == LLMProvider.GEMINI:
            self._setup_gemini(api_key)
        elif self.provider == LLMProvider.OPENROUTER:
            self._setup_openrouter(api_key)
    
    def _setup_gemini(self, api_key: Optional[str] = None) -> None:
        """Set up Gemini client."""
        self.api_key = api_key or self.config.gemini_api_key
        self.model_name = self.config.gemini_model
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided.")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def _setup_openrouter(self, api_key: Optional[str] = None) -> None:
        """Set up OpenRouter client."""
        self.api_key = api_key or self.config.openrouter_api_key
        self.model_name = self.config.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided.")
    
    def _generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        if self.provider == LLMProvider.GEMINI:
            return self._generate_gemini(prompt)
        elif self.provider == LLMProvider.OPENROUTER:
            return self._generate_openrouter(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _generate_gemini(self, prompt: str) -> str:
        """Generate using Gemini API."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    def _generate_openrouter(self, prompt: str) -> str:
        """Generate using OpenRouter API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/git-summarizer",
                "X-Title": "Git-Summarizer"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {e}")
    
    def get_provider_name(self) -> str:
        """Get the name of the active provider."""
        return self.provider.value.title()
    
    def summarize_changes(
        self,
        diff: str,
        stats: str,
        files: list[str]
    ) -> str:
        """Generate a human-readable summary of changes."""
        prompt = Prompts.status_summary(diff, stats, files)
        return self._generate(prompt)
    
    def suggest_commit_message(self, diff: str, stats: str) -> str:
        """Generate a conventional commit message."""
        prompt = Prompts.commit_message(diff, stats)
        response = self._generate(prompt)
        # Clean up the response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
        return response.strip()
    
    def generate_report(
        self,
        commits_summary: str,
        total_commits: int,
        days: int
    ) -> str:
        """Generate a progress report."""
        prompt = Prompts.progress_report(commits_summary, total_commits, days)
        return self._generate(prompt)
