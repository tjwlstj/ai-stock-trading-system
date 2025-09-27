"""
OpenAI Client with Resilience
Async OpenAI client with retry logic, timeout handling, and error recovery
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import tiktoken

from .settings import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Resilient OpenAI API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self.model = settings.OPENAI_MODEL
        self.timeout = settings.OPENAI_TIMEOUT
        
        # Initialize tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Using default encoding for model {self.model}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
    
    @retry(
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to OpenAI API with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        timeout = httpx.Timeout(self.timeout, connect=5.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=payload
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Rate limit hit, retrying...")
                raise httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=response.request,
                    response=response
                )
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            return response.json()
    
    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create chat completion with error handling"""
        
        # Validate input length
        total_tokens = sum(self.count_tokens(msg.get("content", "")) for msg in messages)
        if total_tokens > 4000:  # Conservative limit
            raise ValueError(f"Input too long: {total_tokens} tokens")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = await self._make_request("/chat/completions", payload)
            
            return {
                "content": response["choices"][0]["message"]["content"],
                "model": response["model"],
                "usage": response["usage"],
                "finish_reason": response["choices"][0]["finish_reason"]
            }
            
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = "Unknown error"
            
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", str(e))
            except:
                error_detail = str(e)
            
            logger.error(f"OpenAI API error {status_code}: {error_detail}")
            
            if status_code == 401:
                raise ValueError("Invalid OpenAI API key")
            elif status_code == 429:
                raise ValueError("Rate limit exceeded")
            elif status_code >= 500:
                raise ValueError("OpenAI service unavailable")
            else:
                raise ValueError(f"OpenAI API error: {error_detail}")
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI request: {e}")
            raise ValueError(f"OpenAI request failed: {str(e)}")
    
    async def analyze_stock(self, prompt: str) -> Dict[str, Any]:
        """Analyze stock with structured prompt"""
        
        system_prompt = """You are a professional stock analyst. Analyze the provided information and respond with a JSON object containing:
{
  "recommendation": "BUY" | "HOLD" | "SELL",
  "confidence": 0.0-1.0,
  "target_price": number,
  "key_factors": ["factor1", "factor2", ...],
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "time_horizon": "SHORT" | "MEDIUM" | "LONG"
}

Be objective and base your analysis on the provided data."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1000
            )
            
            # Try to parse JSON response
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using fallback")
                return {
                    "recommendation": "HOLD",
                    "confidence": 0.5,
                    "target_price": 0,
                    "key_factors": ["Analysis parsing failed"],
                    "risk_level": "MEDIUM",
                    "time_horizon": "MEDIUM",
                    "raw_response": content
                }
        
        except Exception as e:
            logger.error(f"Stock analysis failed: {e}")
            return {
                "recommendation": "HOLD",
                "confidence": 0.0,
                "target_price": 0,
                "key_factors": [f"Analysis failed: {str(e)}"],
                "risk_level": "HIGH",
                "time_horizon": "UNKNOWN"
            }
