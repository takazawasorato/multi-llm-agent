"""
Google Geminiプロバイダー（新APIパッケージ対応）
"""

import time
from typing import Optional
from google import genai
from google.genai.types import GenerateContentConfig
from .base import BaseLLMProvider, LLMResponse


class GeminiProvider(BaseLLMProvider):
    """Google Geminiプロバイダー（google-genai使用）"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ):
        super().__init__(api_key, model, temperature, max_tokens, timeout)
        self.client = genai.Client(api_key=api_key)

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

        try:
            # 設定を作成
            config = GenerateContentConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                system_instruction=system_prompt if system_prompt else None
            )

            # 非同期で生成
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.text if response.text else "No content",
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

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """同期版のレスポンス生成"""
        start_time = time.time()

        try:
            # 設定を作成
            config = GenerateContentConfig(
                temperature=kwargs.get("temperature", self.temperature),
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                system_instruction=system_prompt if system_prompt else None
            )

            # 同期で生成
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.text if response.text else "No content",
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
