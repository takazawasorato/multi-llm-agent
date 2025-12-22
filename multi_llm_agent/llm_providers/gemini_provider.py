"""
Google Geminiプロバイダー
"""

import time
from typing import Optional
import google.generativeai as genai
from .base import BaseLLMProvider, LLMResponse


class GeminiProvider(BaseLLMProvider):
    """Google Geminiプロバイダー"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ):
        super().__init__(api_key, model, temperature, max_tokens, timeout)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """非同期でレスポンスを生成"""
        start_time = time.time()

        # Geminiではsystem promptとuser promptを結合
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            response = await self.client.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.text,
                tokens_used=None,  # Geminiはトークン数を返さない場合がある
                finish_reason=None,
                response_time=response_time,
                metadata={}
            )

        except Exception as e:
            response_time = time.time() - start_time
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=f"Error: {str(e)}",
                response_time=response_time,
                metadata={"error": str(e)}
            )

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """同期版のレスポンス生成"""
        start_time = time.time()

        # Geminiではsystem promptとuser promptを結合
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.text,
                tokens_used=None,
                finish_reason=None,
                response_time=response_time,
                metadata={}
            )

        except Exception as e:
            response_time = time.time() - start_time
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=f"Error: {str(e)}",
                response_time=response_time,
                metadata={"error": str(e)}
            )
