from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import os
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

class LLMBackend(ABC):
    """Abstract base class for LLM backends"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def generate_with_tools(self, prompt: str, tools: List[Any], **kwargs) -> Dict[str, Any]:
        """Generate text with tool calling"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass

class OpenAIBackend(LLMBackend):
    """OpenAI LLM backend"""
    
    def __init__(self, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.api_key ="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"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=self.api_key
        )
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI"""
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def generate_with_tools(self, prompt: str, tools: List[Any], **kwargs) -> Dict[str, Any]:
        """Generate text with tool calling using OpenAI"""
        try:
            # For now, return a simple response
            # In a full implementation, this would handle tool calling
            response = await self.llm.ainvoke(prompt)
            return {
                "content": response.content,
                "tools_used": [],
                "model": self.model
            }
        except Exception as e:
            logger.error(f"OpenAI tool generation failed: {e}")
            raise
    
    async def ainvoke(self, prompt: str) -> Any:
        """Async invoke method for compatibility"""
        return await self.llm.ainvoke(prompt)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": 4096
        }

class GeminiBackend(LLMBackend):
    """Google Gemini LLM backend"""
    
    def __init__(self, model: str = "gemini-pro", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Note: Would need langchain_google_genai for full implementation
        self.llm = None  # Placeholder
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini"""
        try:
            # Placeholder implementation
            return f"Gemini response to: {prompt[:100]}..."
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    async def generate_with_tools(self, prompt: str, tools: List[Any], **kwargs) -> Dict[str, Any]:
        """Generate text with tool calling using Gemini"""
        try:
            # Placeholder implementation
            return {
                "content": f"Gemini tool response to: {prompt[:100]}...",
                "tools_used": [],
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Gemini tool generation failed: {e}")
            raise
    
    async def ainvoke(self, prompt: str) -> Any:
        """Async invoke method for compatibility"""
        return type('obj', (object,), {'content': await self.generate(prompt)})()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information"""
        return {
            "provider": "Google",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": 8192
        }

def get_llm_backend(provider: str = "openai", **kwargs) -> LLMBackend:
    """Factory function to get LLM backend"""
    if provider.lower() == "openai":
        return OpenAIBackend(**kwargs)
    elif provider.lower() == "gemini":
        return GeminiBackend(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 