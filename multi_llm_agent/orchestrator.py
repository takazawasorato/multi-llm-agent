"""
複数LLM統合オーケストレーター
"""

import asyncio
from typing import List, Dict, Optional
from .config import Config, LLMProviderConfig
from .llm_providers import (
    BaseLLMProvider,
    LLMResponse,
    OpenAIProvider,
    GeminiProvider,
    AnthropicProvider
)


class MultiLLMOrchestrator:
    """複数のLLMを統合管理し、並列実行するオーケストレーター"""

    def __init__(self, config: Config):
        self.config = config
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """設定に基づいてプロバイダーを初期化"""
        for provider_config in self.config.llm_providers:
            if not provider_config.enabled:
                continue

            provider = self._create_provider(provider_config)
            if provider:
                self.providers[provider_config.name] = provider

    def _create_provider(self, config: LLMProviderConfig) -> Optional[BaseLLMProvider]:
        """プロバイダー設定からプロバイダーインスタンスを作成"""
        if not config.api_key:
            if self.config.verbose:
                print(f"Warning: {config.name}のAPIキーが設定されていません")
            return None

        try:
            if config.name == "openai":
                return OpenAIProvider(
                    api_key=config.api_key,
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=self.config.llm_timeout
                )
            elif config.name == "gemini":
                return GeminiProvider(
                    api_key=config.api_key,
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=self.config.llm_timeout
                )
            elif config.name == "anthropic":
                return AnthropicProvider(
                    api_key=config.api_key,
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=self.config.llm_timeout
                )
            else:
                if self.config.verbose:
                    print(f"Warning: 不明なプロバイダー: {config.name}")
                return None
        except Exception as e:
            if self.config.verbose:
                print(f"Error: {config.name}の初期化に失敗: {e}")
            return None

    async def query_all(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, LLMResponse]:
        """
        全てのLLMに並列でクエリを送信

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, LLMResponse]: プロバイダー名をキーとした応答の辞書
        """
        if not self.providers:
            raise ValueError("有効なLLMプロバイダーが設定されていません")

        if self.config.enable_parallel_processing:
            # 並列実行
            tasks = []
            provider_names = []

            for name, provider in self.providers.items():
                tasks.append(provider.generate(prompt, system_prompt, **kwargs))
                provider_names.append(name)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            responses = {}
            for name, result in zip(provider_names, results):
                if isinstance(result, Exception):
                    # エラー時のレスポンスを作成
                    responses[name] = LLMResponse(
                        provider=name,
                        model="unknown",
                        content=f"Error: {str(result)}",
                        metadata={"error": str(result)}
                    )
                else:
                    responses[name] = result

            return responses
        else:
            # 逐次実行
            responses = {}
            for name, provider in self.providers.items():
                try:
                    response = await provider.generate(prompt, system_prompt, **kwargs)
                    responses[name] = response
                except Exception as e:
                    responses[name] = LLMResponse(
                        provider=name,
                        model="unknown",
                        content=f"Error: {str(e)}",
                        metadata={"error": str(e)}
                    )

            return responses

    def query_all_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, LLMResponse]:
        """
        全てのLLMに同期的にクエリを送信（逐次実行）

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, LLMResponse]: プロバイダー名をキーとした応答の辞書
        """
        if not self.providers:
            raise ValueError("有効なLLMプロバイダーが設定されていません")

        responses = {}
        for name, provider in self.providers.items():
            try:
                response = provider.generate_sync(prompt, system_prompt, **kwargs)
                responses[name] = response
            except Exception as e:
                responses[name] = LLMResponse(
                    provider=name,
                    model="unknown",
                    content=f"Error: {str(e)}",
                    metadata={"error": str(e)}
                )

        return responses

    async def query_specific(
        self,
        provider_names: List[str],
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, LLMResponse]:
        """
        特定のLLMのみにクエリを送信

        Args:
            provider_names: クエリするプロバイダー名のリスト
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト
            **kwargs: 追加パラメータ

        Returns:
            Dict[str, LLMResponse]: プロバイダー名をキーとした応答の辞書
        """
        selected_providers = {
            name: provider
            for name, provider in self.providers.items()
            if name in provider_names
        }

        if not selected_providers:
            raise ValueError(f"指定されたプロバイダーが見つかりません: {provider_names}")

        tasks = []
        names = []

        for name, provider in selected_providers.items():
            tasks.append(provider.generate(prompt, system_prompt, **kwargs))
            names.append(name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        responses = {}
        for name, result in zip(names, results):
            if isinstance(result, Exception):
                responses[name] = LLMResponse(
                    provider=name,
                    model="unknown",
                    content=f"Error: {str(result)}",
                    metadata={"error": str(result)}
                )
            else:
                responses[name] = result

        return responses

    def get_available_providers(self) -> List[str]:
        """利用可能なプロバイダー名のリストを返す"""
        return list(self.providers.keys())
