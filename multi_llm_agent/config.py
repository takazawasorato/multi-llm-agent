"""
設定管理モジュール
環境変数とデフォルト設定を管理
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMProviderConfig:
    """LLMプロバイダーの設定"""
    name: str
    enabled: bool = True
    api_key: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class SearchConfig:
    """検索設定"""
    max_iterations: int = 3  # 探索の繰り返し回数
    results_per_iteration: int = 10  # 1回あたりの取得件数
    enable_arxiv: bool = True
    enable_google_scholar: bool = True
    enable_web_search: bool = True


@dataclass
class Config:
    """全体設定"""

    # LLMプロバイダー設定
    llm_providers: List[LLMProviderConfig] = field(default_factory=list)

    # 検索設定
    search: SearchConfig = field(default_factory=SearchConfig)

    # 統合設定
    enable_parallel_processing: bool = True
    aggregation_model: str = "gpt-4"  # 統合に使用するモデル

    # タイムアウト設定
    llm_timeout: int = 60  # 秒
    search_timeout: int = 30  # 秒

    # デバッグ
    debug: bool = False
    verbose: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        """環境変数から設定を読み込む"""

        llm_providers = []

        # OpenAI/GPT設定
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            llm_providers.append(LLMProviderConfig(
                name="openai",
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
            ))

        # Google Gemini設定
        gemini_key = os.getenv("GOOGLE_API_KEY", "")
        if gemini_key:
            llm_providers.append(LLMProviderConfig(
                name="gemini",
                api_key=gemini_key,
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "2000"))
            ))

        # Anthropic Claude設定
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            llm_providers.append(LLMProviderConfig(
                name="anthropic",
                api_key=anthropic_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "2000"))
            ))

        # 検索設定
        search = SearchConfig(
            max_iterations=int(os.getenv("SEARCH_MAX_ITERATIONS", "3")),
            results_per_iteration=int(os.getenv("SEARCH_RESULTS_PER_ITERATION", "10")),
            enable_arxiv=os.getenv("ENABLE_ARXIV", "true").lower() == "true",
            enable_google_scholar=os.getenv("ENABLE_GOOGLE_SCHOLAR", "true").lower() == "true",
            enable_web_search=os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
        )

        return cls(
            llm_providers=llm_providers,
            search=search,
            enable_parallel_processing=os.getenv("ENABLE_PARALLEL", "true").lower() == "true",
            aggregation_model=os.getenv("AGGREGATION_MODEL", "gpt-4"),
            llm_timeout=int(os.getenv("LLM_TIMEOUT", "60")),
            search_timeout=int(os.getenv("SEARCH_TIMEOUT", "30")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            verbose=os.getenv("VERBOSE", "true").lower() == "true"
        )


# デフォルト設定インスタンス
default_config = Config.from_env()
