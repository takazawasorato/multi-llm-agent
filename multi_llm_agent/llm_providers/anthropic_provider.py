"""
Anthropic Claudeプロバイダー
"""

import time
from typing import Optional
from anthropic import Anthropic, AsyncAnthropic
from .base import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claudeプロバイダー"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ):
        super().__init__(api_key, model, temperature, max_tokens, timeout)
        self.client = Anthropic(api_key=api_key, timeout=timeout)
        self.async_client = AsyncAnthropic(api_key=api_key, timeout=timeout)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """非同期でレスポンスを生成"""
        start_time = time.time()

        try:
            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system_prompt if system_prompt else "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                response_time=response_time,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
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

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                system=system_prompt if system_prompt else "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_time = time.time() - start_time

            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                response_time=response_time,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
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
