"""
メインエントリーポイント
全コンポーネントを統合し、エンドツーエンドの処理を実行
"""

import asyncio
from typing import Optional
from .config import Config
from .orchestrator import MultiLLMOrchestrator
from .search_agent import ComprehensiveSearchAgent
from .aggregator import ResponseAggregator
from .time_tracker import TimeTracker
from .llm_providers import OpenAIProvider


class MultiLLMAgent:
    """複数LLM統合エージェントのメインクラス"""

    def __init__(self, config: Optional[Config] = None):
        """
        初期化

        Args:
            config: 設定オブジェクト（Noneの場合はデフォルト設定を使用）
        """
        self.config = config if config else Config.from_env()
        self.time_tracker = TimeTracker()

        # コンポーネントの初期化
        self.orchestrator = MultiLLMOrchestrator(self.config)
        self.search_agent = ComprehensiveSearchAgent(self.config)

        # 統合用のLLMプロバイダーを作成
        aggregation_provider = self._create_aggregation_provider()
        self.aggregator = ResponseAggregator(self.config, aggregation_provider)

    def _create_aggregation_provider(self) -> Optional[OpenAIProvider]:
        """統合用のLLMプロバイダーを作成"""
        # 利用可能な最初のプロバイダーを使用
        for provider_config in self.config.llm_providers:
            if provider_config.enabled and provider_config.api_key:
                if provider_config.name == "openai":
                    return OpenAIProvider(
                        api_key=provider_config.api_key,
                        model=self.config.aggregation_model,
                        timeout=self.config.llm_timeout
                    )
        return None

    async def query(
        self,
        question: str,
        use_search: bool = True,
        synthesize: bool = True
    ) -> dict:
        """
        質問に対して、包括的な回答を生成

        Args:
            question: 質問
            use_search: 検索を使用するか
            synthesize: 回答を統合するか

        Returns:
            dict: 結果を含む辞書
        """
        self.time_tracker.start_total()
        result = {
            "question": question,
            "search_results": None,
            "llm_responses": None,
            "synthesized_response": None,
            "comparison": None,
            "time_summary": None
        }

        try:
            # 1. 検索の実行（オプション）
            search_context = None
            if use_search:
                with self.time_tracker.measure("網羅的検索"):
                    if self.config.verbose:
                        print("\n" + "="*60)
                        print("ステップ1: 網羅的検索を実施中...")
                        print("="*60)

                    search_results = await self.search_agent.comprehensive_search(question)
                    result["search_results"] = search_results

                    if self.config.verbose:
                        summary = self.search_agent.format_results_summary(search_results)
                        print(summary)

                    # 検索結果をコンテキストとして整形
                    search_context = self._format_search_context(search_results)

            # 2. 複数LLMへのクエリ
            with self.time_tracker.measure("複数LLMクエリ"):
                if self.config.verbose:
                    print("\n" + "="*60)
                    print("ステップ2: 複数のLLMに質問を送信中...")
                    print("="*60)

                # 検索結果を含めた質問を構築
                enhanced_question = question
                if search_context:
                    enhanced_question = f"{question}\n\n参考情報:\n{search_context}"

                llm_responses = await self.orchestrator.query_all(enhanced_question)
                result["llm_responses"] = llm_responses

                if self.config.verbose:
                    formatted = self.aggregator.format_responses(llm_responses)
                    print(formatted)

            # 3. 回答の比較・分析
            with self.time_tracker.measure("回答分析"):
                if self.config.verbose:
                    print("\n" + "="*60)
                    print("ステップ3: 回答を分析中...")
                    print("="*60)

                comparison = self.aggregator.analyze_differences(llm_responses)
                comparison_table = self.aggregator.create_comparison_table(llm_responses)
                result["comparison"] = comparison + "\n" + comparison_table

                if self.config.verbose:
                    print(comparison)
                    print(comparison_table)

            # 4. 回答の統合（オプション）
            if synthesize:
                with self.time_tracker.measure("回答統合"):
                    if self.config.verbose:
                        print("\n" + "="*60)
                        print("ステップ4: 回答を統合中...")
                        print("="*60)

                    synthesized = await self.aggregator.synthesize_responses(
                        llm_responses,
                        question,
                        search_context
                    )
                    result["synthesized_response"] = synthesized

                    if self.config.verbose:
                        print("\n" + "="*60)
                        print("統合回答")
                        print("="*60)
                        print(synthesized)
                        print("="*60)

            # 5. 時間サマリー
            total_time = self.time_tracker.end_total()
            result["time_summary"] = self.time_tracker.get_summary()

            if self.config.verbose:
                self.time_tracker.print_summary()

            return result

        except Exception as e:
            if self.config.verbose:
                print(f"エラーが発生しました: {e}")
            result["error"] = str(e)
            return result

    def query_sync(
        self,
        question: str,
        use_search: bool = True,
        synthesize: bool = True
    ) -> dict:
        """
        同期版のクエリ

        Args:
            question: 質問
            use_search: 検索を使用するか
            synthesize: 回答を統合するか

        Returns:
            dict: 結果を含む辞書
        """
        return asyncio.run(self.query(question, use_search, synthesize))

    def _format_search_context(self, search_results: dict) -> str:
        """検索結果をコンテキスト文字列にフォーマット"""
        lines = []

        for source, results in search_results.items():
            if results:
                lines.append(f"\n【{source.upper()}からの情報】")
                for i, result in enumerate(results[:5], 1):  # 最初の5件のみ
                    lines.append(f"{i}. {result.title}")
                    if result.snippet:
                        lines.append(f"   {result.snippet[:200]}")
                    lines.append(f"   URL: {result.url}")

        return "\n".join(lines)


def main():
    """CLIエントリーポイント"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python -m multi_llm_agent.main '質問'")
        print("例: python -m multi_llm_agent.main 'Transformerアーキテクチャについて教えて'")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    # エージェントを作成して実行
    agent = MultiLLMAgent()
    result = agent.query_sync(question)

    # 結果の表示
    if result.get("synthesized_response"):
        print("\n" + "="*80)
        print("最終回答")
        print("="*80)
        print(result["synthesized_response"])
        print("="*80)


if __name__ == "__main__":
    main()
