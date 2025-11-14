from __future__ import annotations

import json
from typing import Dict, Optional

import requests

from .config import get_setting


class LLMClient:
    """
    LLM client that supports Ollama (primary) and OpenAI (fallback).
    Shares Ollama instance with AI-EWG.
    """
    
    def __init__(self):
        self.provider = get_setting("LLM_PROVIDER", "ollama")
        self.ollama_base_url = get_setting("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = get_setting("MODEL_NAME", "llama3.1")
        self.openai_api_key = get_setting("OPENAI_API_KEY")
        self.openai_model = get_setting("OPENAI_MODEL", "gpt-4o-mini")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generate text using configured LLM provider.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Max tokens to generate
            temperature: Sampling temperature (0-1)
        
        Returns:
            Generated text
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt, max_tokens, temperature)
        elif self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Generate using Ollama API."""
        url = f"{self.ollama_base_url}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def _generate_openai(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Generate using OpenAI API (fallback)."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.openai_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")


# Singleton instance
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create singleton LLM client."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
