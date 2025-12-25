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
from .output_manager import OutputManager
from .llm_providers import OpenAIProvider


class MultiLLMAgent:
    """複数LLM統合エージェントのメインクラス"""

    def __init__(self, config: Optional[Config] = None, enable_output: bool = True):
        """
        初期化

        Args:
            config: 設定オブジェクト（Noneの場合はデフォルト設定を使用）
            enable_output: 出力管理を有効にするか
        """
        self.config = config if config else Config.from_env()
        self.time_tracker = TimeTracker()

        # 出力管理の初期化
        self.output_manager = OutputManager() if enable_output else None

        # コンポーネントの初期化
        self.orchestrator = MultiLLMOrchestrator(self.config)
        self.search_agent = ComprehensiveSearchAgent(self.config)

        # 統合用のLLMプロバイダーを作成
        aggregation_provider = self._create_aggregation_provider()
        self.aggregator = ResponseAggregator(self.config, aggregation_provider)

        # 初期化完了をログ記録
        if self.output_manager:
            self.output_manager.log("Multi-LLM Agent を初期化しました")

    def _create_aggregation_provider(self) -> Optional[OpenAIProvider]:
        """統合用のLLMプロバイダーを作成"""
        # 利用可能な最初のプロバイダーを使用
        for provider_config in self.config.llm_providers:
            if provider_config.enabled and provider_config.api_key:
                if provider_config.name == "openai":
                    return OpenAIProvider(
                        api_key=provider_config.api_key,
                        model=self.config.aggregation_model,
                        max_tokens=self.config.aggregation_max_tokens,
                        temperature=self.config.aggregation_temperature,
                        timeout=self.config.aggregation_timeout
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
        # ログ記録
        if self.output_manager:
            self.output_manager.log(f"質問を受け付けました: {question}")

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
                if self.output_manager:
                    self.output_manager.log("網羅的検索を開始します")

                with self.time_tracker.measure("網羅的検索"):
                    if self.config.verbose:
                        print("検索中...")

                    search_results = await self.search_agent.comprehensive_search(question)
                    result["search_results"] = search_results

                    # 検索結果の詳細をログに記録
                    if self.output_manager:
                        total_results = sum(len(results) for results in search_results.values())
                        self.output_manager.log(f"検索完了: {total_results}件の結果を取得しました")

                        # 各検索ソースの詳細をログに記録
                        for source, results in search_results.items():
                            self.output_manager.log(f"  - {source.upper()}: {len(results)}件")
                            for i, r in enumerate(results[:3], 1):
                                self.output_manager.log(f"    {i}. {r.title[:80]}", level="debug")

                    if self.config.verbose:
                        total_results = sum(len(results) for results in search_results.values())
                        print(f"検索完了: {total_results}件")

                    # 検索結果をコンテキストとして整形
                    search_context = self._format_search_context(search_results)

            # 2. 複数LLMへのクエリ
            if self.output_manager:
                self.output_manager.log("複数のLLMへクエリを送信します")

            with self.time_tracker.measure("複数LLMクエリ"):
                if self.config.verbose:
                    print("LLMクエリ中...")

                # 検索結果を含めた質問を構築
                enhanced_question = question
                if search_context:
                    enhanced_question = f"{question}\n\n参考情報:\n{search_context}"

                llm_responses = await self.orchestrator.query_all(enhanced_question)
                result["llm_responses"] = llm_responses

                # LLM応答の詳細をログに記録
                if self.output_manager:
                    success_count = sum(1 for r in llm_responses.values() if "error" not in r.metadata)
                    self.output_manager.log(f"LLM応答取得完了: {success_count}/{len(llm_responses)}件成功")

                    for provider, response in llm_responses.items():
                        if "error" not in response.metadata:
                            self.output_manager.log(f"  - {provider.upper()} ({response.model}): "
                                                   f"{len(response.content)}文字, "
                                                   f"{response.response_time:.2f}秒")
                        else:
                            self.output_manager.log(f"  - {provider.upper()}: エラー - {response.metadata['error']}",
                                                   level="error")

                if self.config.verbose:
                    success_count = sum(1 for r in llm_responses.values() if "error" not in r.metadata)
                    print(f"LLM応答取得: {success_count}/{len(llm_responses)}件成功")

            # 3. 回答の比較・分析
            with self.time_tracker.measure("回答分析"):
                if self.output_manager:
                    self.output_manager.log("回答の比較・分析を開始します")

                comparison = self.aggregator.analyze_differences(llm_responses)
                comparison_table = self.aggregator.create_comparison_table(llm_responses)
                result["comparison"] = comparison + "\n" + comparison_table

                if self.output_manager:
                    self.output_manager.log("回答分析完了")

            # 4. 回答の統合（オプション）
            if synthesize:
                if self.output_manager:
                    self.output_manager.log("回答の統合を開始します")

                with self.time_tracker.measure("回答統合"):
                    if self.config.verbose:
                        print("統合中...")

                    synthesized = await self.aggregator.synthesize_responses(
                        llm_responses,
                        question,
                        search_context
                    )
                    result["synthesized_response"] = synthesized

                    if self.output_manager:
                        self.output_manager.log(f"回答統合完了: {len(synthesized)}文字の統合回答を生成")

                    if self.config.verbose:
                        print(f"統合完了: {len(synthesized)}文字")

            # 5. 時間サマリー
            self.time_tracker.end_total()
            result["time_summary"] = self.time_tracker.get_summary()

            # 処理時間の詳細をログに記録
            if self.output_manager:
                time_summary = result["time_summary"]
                self.output_manager.log(f"総処理時間: {time_summary['total_duration']}")
                for task in time_summary['tasks']:
                    self.output_manager.log(f"  - {task['name']}: {task['duration']}")

            if self.config.verbose:
                time_summary = result["time_summary"]
                print(f"\n総処理時間: {time_summary['total_duration']}")

            # 6. 結果を保存
            if self.output_manager:
                self.output_manager.log("処理が正常に完了しました")
                self.output_manager.save_result(result, question)
                self.output_manager.save_result_markdown(result, question)

                # 統合回答が存在する場合は別ファイルとしても保存
                if result.get("synthesized_response"):
                    self.output_manager.save_synthesis_markdown(
                        result["synthesized_response"],
                        question
                    )

                # 出力先を表示
                self.output_manager.print_summary()

            return result

        except Exception as e:
            # エラーログを記録
            if self.output_manager:
                self.output_manager.log(f"エラーが発生しました: {e}", level="error")
                import traceback
                self.output_manager.log(f"スタックトレース:\n{traceback.format_exc()}", level="error")

            if self.config.verbose:
                print(f"エラーが発生しました: {e}")

            result["error"] = str(e)

            # エラー時も結果を保存
            if self.output_manager:
                self.output_manager.save_result(result, question)
                self.output_manager.save_result_markdown(result, question)

                # 統合回答が存在する場合は別ファイルとしても保存
                if result.get("synthesized_response"):
                    self.output_manager.save_synthesis_markdown(
                        result["synthesized_response"],
                        question
                    )

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

    # 結果の保存先を表示
    if result.get("synthesized_response"):
        print(f"\n処理完了。結果は output/ に保存されました。")


if __name__ == "__main__":
    main()
