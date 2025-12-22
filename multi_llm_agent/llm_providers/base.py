"""
LLMプロバイダーの基底クラス
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LLMResponse:
    """LLMからの応答を表すデータクラス"""
    provider: str
    model: str
    content: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None
    timestamp: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """LLMプロバイダーの抽象基底クラス"""

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        プロンプトからレスポンスを生成

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            **kwargs: 追加パラメータ

        Returns:
            LLMResponse: LLMからの応答
        """
        pass

    @abstractmethod
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        同期版のgenerate

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            **kwargs: 追加パラメータ

        Returns:
            LLMResponse: LLMからの応答
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """プロバイダー名を返す"""
        pass
