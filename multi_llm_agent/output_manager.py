"""
出力管理モジュール
日付ごとのディレクトリにログと結果を保存
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class OutputManager:
    """出力管理クラス"""

    def __init__(self, base_dir: str = "output"):
        """
        初期化

        Args:
            base_dir: 基底ディレクトリパス
        """
        self.base_dir = Path(base_dir)
        self.session_time = datetime.now()
        self.date_str = self.session_time.strftime("%Y-%m-%d")
        self.time_str = self.session_time.strftime("%Y%m%d_%H%M%S")

        # ジョブごとのディレクトリ（日付_時間）
        self.output_dir = self.base_dir / self.time_str

        # ディレクトリを作成
        self._create_directories()

        # ログファイルパス（ディレクトリ名に時間が入っているのでシンプルに）
        self.log_file = self.output_dir / "log.txt"
        self.result_json = self.output_dir / "result.json"
        self.result_md = self.output_dir / "result.md"
        self.synthesis_md = self.output_dir / "synthesis.md"

        # ロガーを設定
        self._setup_logger()

    def _create_directories(self):
        """必要なディレクトリを作成"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self):
        """ロガーを設定"""
        self.logger = logging.getLogger(f"MultiLLMAgent_{self.time_str}")
        self.logger.setLevel(logging.INFO)

        # ファイルハンドラー
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # コンソールハンドラー（エラーのみ表示）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # ハンドラーを追加
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, message: str, level: str = "info"):
        """
        ログメッセージを記録

        Args:
            message: ログメッセージ
            level: ログレベル (info, warning, error, debug)
        """
        level_map = {
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "debug": self.logger.debug
        }
        log_func = level_map.get(level.lower(), self.logger.info)
        log_func(message)

    def save_result(
        self,
        result: Dict[str, Any],
        question: Optional[str] = None
    ):
        """
        結果をJSON形式で保存

        Args:
            result: 結果データ
            question: 質問（オプション）
        """
        # データをJSON serializable な形式に変換
        serializable_result = self._make_serializable(result)

        output_data = {
            "timestamp": self.session_time.isoformat(),
            "question": question,
            "result": serializable_result
        }

        # JSON形式で保存
        with open(self.result_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        self.log(f"結果をJSON形式で保存しました")

    def _make_serializable(self, obj: Any) -> Any:
        """
        オブジェクトをJSON serializable な形式に変換

        Args:
            obj: 変換対象のオブジェクト

        Returns:
            JSON serializable なオブジェクト
        """
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # dataclassやカスタムオブジェクトを辞書に変換
            return self._make_serializable(vars(obj))
        else:
            return obj

    def save_result_markdown(
        self,
        result: Dict[str, Any],
        question: Optional[str] = None
    ):
        """
        結果をMarkdown形式で保存

        Args:
            result: 結果データ
            question: 質問（オプション）
        """
        lines = []

        # ヘッダー
        lines.append("# Multi-LLM Agent 実行結果")
        lines.append("")
        lines.append(f"**実行日時**: {self.session_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("")

        # 質問
        if question:
            lines.append("## 質問")
            lines.append("")
            lines.append(f"> {question}")
            lines.append("")

        # 検索結果
        if result.get("search_results"):
            lines.append("## 検索結果サマリー")
            lines.append("")
            for source, results in result["search_results"].items():
                lines.append(f"### {source.upper()} ({len(results)}件)")
                lines.append("")
                for i, r in enumerate(results[:5], 1):
                    lines.append(f"{i}. **{r.title}**")
                    lines.append(f"   - URL: {r.url}")
                    if r.snippet:
                        snippet = r.snippet[:150] + "..." if len(r.snippet) > 150 else r.snippet
                        lines.append(f"   - 概要: {snippet}")
                    lines.append("")
                if len(results) > 5:
                    lines.append(f"*... 他 {len(results) - 5}件*")
                    lines.append("")

        # 各LLMの回答
        if result.get("llm_responses"):
            lines.append("## 各LLMからの回答")
            lines.append("")
            for provider, response in result["llm_responses"].items():
                lines.append(f"### {provider.upper()} ({response.model})")
                lines.append("")

                if "error" not in response.metadata:
                    lines.append(response.content)
                    lines.append("")

                    if response.response_time:
                        lines.append(f"*処理時間: {response.response_time:.2f}秒*")
                    if response.tokens_used:
                        lines.append(f"*トークン使用量: {response.tokens_used}*")
                else:
                    lines.append(f"⚠️ **エラー**: {response.metadata['error']}")

                lines.append("")
                lines.append("---")
                lines.append("")

        # 統合回答
        if result.get("synthesized_response"):
            lines.append("## 統合回答")
            lines.append("")
            lines.append(result["synthesized_response"])
            lines.append("")

        # 比較分析
        if result.get("comparison"):
            lines.append("## 回答比較分析")
            lines.append("")
            lines.append("```")
            lines.append(result["comparison"])
            lines.append("```")
            lines.append("")

        # 時間サマリー
        if result.get("time_summary"):
            summary = result["time_summary"]
            lines.append("## 処理時間サマリー")
            lines.append("")
            lines.append(f"- **総処理時間**: {summary['total_duration']}")
            lines.append(f"- **タスク数**: {summary['total_tasks']}")
            lines.append("")
            lines.append("### タスク別処理時間")
            lines.append("")
            for task in summary['tasks']:
                lines.append(f"- {task['name']}: {task['duration']}")
            lines.append("")

        # ファイルに保存
        with open(self.result_md, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        self.log(f"結果をMarkdown形式で保存しました")

    def save_synthesis_markdown(
        self,
        synthesized_response: str,
        question: Optional[str] = None
    ):
        """
        統合回答のみをMarkdown形式で保存

        Args:
            synthesized_response: 統合回答
            question: 質問（オプション）
        """
        lines = []

        # ヘッダー
        lines.append("# 統合回答")
        lines.append("")
        lines.append(f"**実行日時**: {self.session_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("")

        # 質問
        if question:
            lines.append("## 質問")
            lines.append("")
            lines.append(f"> {question}")
            lines.append("")

        # 統合回答
        lines.append("## 回答")
        lines.append("")
        lines.append(synthesized_response)
        lines.append("")

        # ファイルに保存
        with open(self.synthesis_md, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        self.log(f"統合回答をMarkdown形式で保存しました")

    def get_output_paths(self) -> Dict[str, Path]:
        """
        出力ファイルのパスを取得

        Returns:
            Dict[str, Path]: ファイル名をキーとしたパスの辞書
        """
        return {
            "log": self.log_file,
            "result_json": self.result_json,
            "result_md": self.result_md,
            "synthesis_md": self.synthesis_md,
            "output_dir": self.output_dir
        }

    def print_summary(self):
        """出力ファイルのサマリーを表示"""
        print(f"\n出力ディレクトリ: {self.output_dir}")
        print(f"  - log.txt")
        print(f"  - result.json")
        print(f"  - result.md")
        print(f"  - synthesis.md\n")
