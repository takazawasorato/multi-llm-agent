"""
網羅的探索エージェント
複数回の探索を実施し、網羅性を向上させる
"""

import asyncio
from typing import List, Dict, Set, Optional
from .config import Config
from .searchers import BaseSearcher, SearchResult, ArxivSearcher, WebSearcher


class ComprehensiveSearchAgent:
    """網羅的探索を実行するエージェント"""

    def __init__(self, config: Config):
        self.config = config
        self.searchers: Dict[str, BaseSearcher] = {}
        self._initialize_searchers()

    def _initialize_searchers(self):
        """検索エンジンを初期化"""
        if self.config.search.enable_arxiv:
            self.searchers["arxiv"] = ArxivSearcher(
                timeout=self.config.search_timeout
            )

        if self.config.search.enable_web_search:
            self.searchers["web"] = WebSearcher(
                timeout=self.config.search_timeout
            )

    async def comprehensive_search(
        self,
        query: str,
        iterations: Optional[int] = None,
        diversify_queries: bool = True
    ) -> Dict[str, List[SearchResult]]:
        """
        網羅的な検索を実行

        Args:
            query: 検索クエリ
            iterations: 探索回数（Noneの場合は設定値を使用）
            diversify_queries: クエリを多様化するかどうか

        Returns:
            Dict[str, List[SearchResult]]: 検索ソースごとの結果
        """
        if iterations is None:
            iterations = self.config.search.max_iterations

        all_results = {name: [] for name in self.searchers.keys()}
        seen_urls: Dict[str, Set[str]] = {name: set() for name in self.searchers.keys()}

        for iteration in range(iterations):
            if self.config.verbose:
                print(f"\n探索イテレーション {iteration + 1}/{iterations}")

            # イテレーションごとにクエリを多様化
            current_query = query
            if diversify_queries and iteration > 0:
                current_query = self._diversify_query(query, iteration)
                if self.config.verbose:
                    print(f"多様化クエリ: {current_query}")

            # 並列検索
            tasks = []
            searcher_names = []

            for name, searcher in self.searchers.items():
                tasks.append(
                    searcher.search(
                        current_query,
                        max_results=self.config.search.results_per_iteration
                    )
                )
                searcher_names.append(name)

            results_list = await asyncio.gather(*tasks, return_exceptions=True)

            # 結果を集約（重複排除）
            for name, results in zip(searcher_names, results_list):
                if isinstance(results, Exception):
                    if self.config.verbose:
                        print(f"{name}検索エラー: {results}")
                    continue

                new_results = []
                for result in results:
                    if result.url not in seen_urls[name]:
                        seen_urls[name].add(result.url)
                        new_results.append(result)

                all_results[name].extend(new_results)

                if self.config.verbose:
                    print(f"{name}: {len(new_results)}件の新規結果（累計: {len(all_results[name])}件）")

        return all_results

    def comprehensive_search_sync(
        self,
        query: str,
        iterations: Optional[int] = None,
        diversify_queries: bool = True
    ) -> Dict[str, List[SearchResult]]:
        """
        同期版の網羅的検索

        Args:
            query: 検索クエリ
            iterations: 探索回数
            diversify_queries: クエリを多様化するかどうか

        Returns:
            Dict[str, List[SearchResult]]: 検索ソースごとの結果
        """
        if iterations is None:
            iterations = self.config.search.max_iterations

        all_results = {name: [] for name in self.searchers.keys()}
        seen_urls: Dict[str, Set[str]] = {name: set() for name in self.searchers.keys()}

        for iteration in range(iterations):
            if self.config.verbose:
                print(f"\n探索イテレーション {iteration + 1}/{iterations}")

            current_query = query
            if diversify_queries and iteration > 0:
                current_query = self._diversify_query(query, iteration)
                if self.config.verbose:
                    print(f"多様化クエリ: {current_query}")

            for name, searcher in self.searchers.items():
                try:
                    results = searcher.search_sync(
                        current_query,
                        max_results=self.config.search.results_per_iteration
                    )

                    new_results = []
                    for result in results:
                        if result.url not in seen_urls[name]:
                            seen_urls[name].add(result.url)
                            new_results.append(result)

                    all_results[name].extend(new_results)

                    if self.config.verbose:
                        print(f"{name}: {len(new_results)}件の新規結果（累計: {len(all_results[name])}件）")

                except Exception as e:
                    if self.config.verbose:
                        print(f"{name}検索エラー: {e}")

        return all_results

    def _diversify_query(self, original_query: str, iteration: int) -> str:
        """
        クエリを多様化する

        Args:
            original_query: 元のクエリ
            iteration: 現在のイテレーション番号

        Returns:
            str: 多様化されたクエリ
        """
        # 簡易的な多様化戦略
        strategies = [
            f"{original_query}",  # オリジナル
            f"{original_query} overview",  # 概要
            f"{original_query} tutorial",  # チュートリアル
            f"{original_query} best practices",  # ベストプラクティス
            f"{original_query} examples",  # 事例
            f"{original_query} comparison",  # 比較
            f"{original_query} latest",  # 最新
            f"{original_query} research",  # 研究
            f"latest {original_query}",  # 最新版
            f"{original_query} implementation",  # 実装
        ]

        # イテレーション番号に応じて戦略を選択
        strategy_index = iteration % len(strategies)
        return strategies[strategy_index]

    def format_results_summary(
        self,
        results: Dict[str, List[SearchResult]]
    ) -> str:
        """
        検索結果のサマリーをフォーマット

        Args:
            results: 検索結果

        Returns:
            str: フォーマットされたサマリー
        """
        summary_lines = []
        summary_lines.append("="*60)
        summary_lines.append("検索結果サマリー")
        summary_lines.append("="*60)

        total_results = 0
        for source, source_results in results.items():
            count = len(source_results)
            total_results += count
            summary_lines.append(f"\n【{source.upper()}】 {count}件")

            for i, result in enumerate(source_results[:5], 1):  # 最初の5件のみ表示
                summary_lines.append(f"{i}. {result.title}")
                summary_lines.append(f"   URL: {result.url}")
                if result.snippet:
                    snippet = result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
                    summary_lines.append(f"   概要: {snippet}")

            if count > 5:
                summary_lines.append(f"   ... 他 {count - 5}件")

        summary_lines.append(f"\n総結果数: {total_results}件")
        summary_lines.append("="*60)

        return "\n".join(summary_lines)
