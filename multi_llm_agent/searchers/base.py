"""
検索の基底クラス
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    """検索結果を表すデータクラス"""
    title: str
    url: str
    snippet: str
    source: str  # 検索ソース（arxiv, google, etc）
    published_date: Optional[str] = None
    authors: Optional[List[str]] = None
    metadata: Dict[str, Any] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class BaseSearcher(ABC):
    """検索の抽象基底クラス"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """
        検索を実行

        Args:
            query: 検索クエリ
            max_results: 最大取得件数
            **kwargs: 追加パラメータ

        Returns:
            List[SearchResult]: 検索結果のリスト
        """
        pass

    @abstractmethod
    def search_sync(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """
        同期版の検索

        Args:
            query: 検索クエリ
            max_results: 最大取得件数
            **kwargs: 追加パラメータ

        Returns:
            List[SearchResult]: 検索結果のリスト
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """検索ソース名を返す"""
        pass
