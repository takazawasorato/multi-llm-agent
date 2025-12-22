"""
arXiv論文検索
"""

import arxiv
from typing import List
from .base import BaseSearcher, SearchResult


class ArxivSearcher(BaseSearcher):
    """arXiv論文検索クラス"""

    @property
    def source_name(self) -> str:
        return "arxiv"

    async def search(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """非同期検索（同期版を呼び出す）"""
        return self.search_sync(query, max_results, **kwargs)

    def search_sync(
        self,
        query: str,
        max_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """arXivから論文を検索"""
        try:
            # arXivクライアントで検索
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            results = []
            for paper in search.results():
                result = SearchResult(
                    title=paper.title,
                    url=paper.entry_id,
                    snippet=paper.summary[:500] if paper.summary else "",
                    source=self.source_name,
                    published_date=paper.published.isoformat() if paper.published else None,
                    authors=[author.name for author in paper.authors] if paper.authors else None,
                    metadata={
                        "pdf_url": paper.pdf_url,
                        "categories": paper.categories,
                        "primary_category": paper.primary_category,
                    }
                )
                results.append(result)

            return results

        except Exception as e:
            # エラー時は空のリストを返す
            print(f"arXiv検索エラー: {e}")
            return []
