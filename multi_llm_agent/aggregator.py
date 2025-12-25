"""
回答統合・合成エンジン
複数のLLM回答を分析・統合する
"""

from typing import Dict, Optional
from .llm_providers import LLMResponse, BaseLLMProvider
from .config import Config


class ResponseAggregator:
    """複数のLLM回答を統合するクラス"""

    def __init__(self, config: Config, aggregation_provider: Optional[BaseLLMProvider] = None):
        self.config = config
        self.aggregation_provider = aggregation_provider

    def format_responses(self, responses: Dict[str, LLMResponse]) -> str:
        """
        複数の回答を読みやすい形式にフォーマット

        Args:
            responses: プロバイダー名をキーとした応答の辞書

        Returns:
            str: フォーマットされた回答
        """
        lines = []
        lines.append("="*80)
        lines.append("複数LLMからの回答")
        lines.append("="*80)

        for i, (provider, response) in enumerate(responses.items(), 1):
            lines.append(f"\n【回答 {i}: {provider.upper()} ({response.model})】")
            lines.append("-"*80)
            lines.append(response.content)

            if response.response_time:
                lines.append(f"\n処理時間: {response.response_time:.2f}秒")
            if response.tokens_used:
                lines.append(f"トークン使用量: {response.tokens_used}")

            if "error" in response.metadata:
                lines.append(f"⚠ エラー: {response.metadata['error']}")

            lines.append("-"*80)

        return "\n".join(lines)

    def analyze_differences(self, responses: Dict[str, LLMResponse]) -> str:
        """
        回答の違いを分析

        Args:
            responses: プロバイダー名をキーとした応答の辞書

        Returns:
            str: 分析結果
        """
        lines = []
        lines.append("\n" + "="*80)
        lines.append("回答の比較分析")
        lines.append("="*80)

        # 回答長の比較
        lines.append("\n【回答の長さ】")
        for provider, response in responses.items():
            length = len(response.content)
            lines.append(f"  {provider}: {length}文字")

        # 処理時間の比較
        lines.append("\n【処理時間】")
        for provider, response in responses.items():
            if response.response_time:
                lines.append(f"  {provider}: {response.response_time:.2f}秒")

        # トークン使用量の比較
        lines.append("\n【トークン使用量】")
        for provider, response in responses.items():
            if response.tokens_used:
                lines.append(f"  {provider}: {response.tokens_used}トークン")

        # エラーチェック
        errors = [
            provider for provider, response in responses.items()
            if "error" in response.metadata
        ]
        if errors:
            lines.append("\n【エラーが発生したプロバイダー】")
            for provider in errors:
                lines.append(f"  ⚠ {provider}")

        return "\n".join(lines)

    async def synthesize_responses(
        self,
        responses: Dict[str, LLMResponse],
        original_question: str,
        context: Optional[str] = None
    ) -> str:
        """
        複数の回答を統合して、総合的な回答を生成

        Args:
            responses: プロバイダー名をキーとした応答の辞書
            original_question: 元の質問
            context: 追加コンテキスト（検索結果など）

        Returns:
            str: 統合された回答
        """
        if not self.aggregation_provider:
            # 統合用プロバイダーがない場合は、シンプルな連結を返す
            return self._simple_synthesis(responses)

        # LLMを使って回答を統合
        synthesis_prompt = self._create_synthesis_prompt(
            responses, original_question, context
        )

        try:
            result = await self.aggregation_provider.generate(
                synthesis_prompt,
                system_prompt="あなたは複数の情報源からの回答を統合し、"
                             "包括的で正確な回答を生成する専門家です。"
            )

            # デバッグ: 空のレスポンスの場合は詳細を記録
            if not result.content:
                # 空の場合はフォールバック
                return self._simple_synthesis(responses)

            # max_tokensに達して途中で切れた場合の警告
            if result.finish_reason == "length" and self.config.verbose:
                print(f"警告: 統合回答がmax_tokens上限に達しました（{result.metadata.get('completion_tokens', 'N/A')}トークン）")

            return result.content

        except Exception as e:
            if self.config.verbose:
                print(f"統合処理エラー: {e}")
            return self._simple_synthesis(responses)

    def synthesize_responses_sync(
        self,
        responses: Dict[str, LLMResponse],
        original_question: str,
        context: Optional[str] = None
    ) -> str:
        """
        同期版の回答統合

        Args:
            responses: プロバイダー名をキーとした応答の辞書
            original_question: 元の質問
            context: 追加コンテキスト

        Returns:
            str: 統合された回答
        """
        if not self.aggregation_provider:
            return self._simple_synthesis(responses)

        synthesis_prompt = self._create_synthesis_prompt(
            responses, original_question, context
        )

        try:
            result = self.aggregation_provider.generate_sync(
                synthesis_prompt,
                system_prompt="あなたは複数の情報源からの回答を統合し、"
                             "包括的で正確な回答を生成する専門家です。"
            )

            # デバッグ: 空のレスポンスの場合は詳細を記録
            if not result.content:
                # 空の場合はフォールバック
                return self._simple_synthesis(responses)

            # max_tokensに達して途中で切れた場合の警告
            if result.finish_reason == "length" and self.config.verbose:
                print(f"警告: 統合回答がmax_tokens上限に達しました（{result.metadata.get('completion_tokens', 'N/A')}トークン）")

            return result.content

        except Exception as e:
            if self.config.verbose:
                print(f"統合処理エラー: {e}")
            return self._simple_synthesis(responses)

    def _create_synthesis_prompt(
        self,
        responses: Dict[str, LLMResponse],
        original_question: str,
        context: Optional[str] = None
    ) -> str:
        """統合用のプロンプトを作成"""
        prompt_parts = []

        prompt_parts.append(f"元の質問: {original_question}\n")

        if context:
            prompt_parts.append(f"追加コンテキスト:\n{context}\n")

        prompt_parts.append("以下は、複数のAIモデルからの回答です:\n")

        for i, (provider, response) in enumerate(responses.items(), 1):
            prompt_parts.append(f"\n【回答{i} - {provider}】")
            prompt_parts.append(response.content)

        prompt_parts.append("\n" + "="*60)
        prompt_parts.append("\nタスク:")
        prompt_parts.append("上記の複数の回答を分析し、以下の点に注意して統合された回答を作成してください:")
        prompt_parts.append("1. 各回答の共通点と相違点を特定する")
        prompt_parts.append("2. 矛盾する情報がある場合は明記する")
        prompt_parts.append("3. 最も信頼できる情報を優先する")
        prompt_parts.append("4. 包括的で正確な統合回答を生成する")
        prompt_parts.append("5. 必要に応じて追加の注意事項や補足を含める")

        return "\n".join(prompt_parts)

    def _simple_synthesis(self, responses: Dict[str, LLMResponse]) -> str:
        """シンプルな統合（連結）"""
        lines = []
        lines.append("="*80)
        lines.append("統合回答（各モデルからの回答）")
        lines.append("="*80)

        for provider, response in responses.items():
            if "error" not in response.metadata:
                lines.append(f"\n【{provider.upper()}からの回答】")
                lines.append(response.content)
                lines.append("")

        lines.append("="*80)
        lines.append("注: 上記は複数のAIモデルからの個別回答です。")
        lines.append("矛盾する情報がある場合は、複数の情報源で確認することをお勧めします。")
        lines.append("="*80)

        return "\n".join(lines)

    def create_comparison_table(self, responses: Dict[str, LLMResponse]) -> str:
        """
        回答の比較表を作成

        Args:
            responses: プロバイダー名をキーとした応答の辞書

        Returns:
            str: 比較表
        """
        lines = []
        lines.append("\n" + "="*100)
        lines.append("回答比較表")
        lines.append("="*100)

        # ヘッダー
        header = f"{'モデル':<15} | {'文字数':<10} | {'処理時間(秒)':<15} | {'トークン':<10} | {'ステータス':<10}"
        lines.append(header)
        lines.append("-"*100)

        # 各行
        for provider, response in responses.items():
            model_name = f"{provider}/{response.model}"[:15]
            char_count = len(response.content)
            time_str = f"{response.response_time:.2f}" if response.response_time else "N/A"
            tokens_str = str(response.tokens_used) if response.tokens_used else "N/A"
            status = "エラー" if "error" in response.metadata else "成功"

            row = f"{model_name:<15} | {char_count:<10} | {time_str:<15} | {tokens_str:<10} | {status:<10}"
            lines.append(row)

        lines.append("="*100)

        return "\n".join(lines)
