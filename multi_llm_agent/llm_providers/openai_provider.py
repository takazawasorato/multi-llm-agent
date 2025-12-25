"""
OpenAI GPTプロバイダー
"""

import time
from typing import Optional
from openai import OpenAI, AsyncOpenAI
from .base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI/GPTプロバイダー"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ):
        super().__init__(api_key, model, temperature, max_tokens, timeout)
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.async_client = AsyncOpenAI(api_key=api_key, timeout=timeout)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """非同期でレスポンスを生成"""
        start_time = time.time()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # 新しいAPIではmax_completion_tokensを使用
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_completion_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.choices[0].message.content or "",
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": response.usage.completion_tokens if response.usage else None,
                }
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

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # 新しいAPIではmax_completion_tokensを使用
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_completion_tokens=kwargs.get("max_tokens", self.max_tokens),
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.choices[0].message.content or "",
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": response.usage.completion_tokens if response.usage else None,
                }
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
