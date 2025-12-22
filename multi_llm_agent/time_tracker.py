"""
時間計測モジュール
各処理の所要時間を記録・管理する
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager


class TimeTracker:
    """処理時間を追跡・記録するクラス"""

    def __init__(self):
        self.records: List[Dict] = []
        self.current_task: Optional[str] = None
        self.task_start_time: Optional[float] = None
        self.total_start_time: Optional[float] = None

    def start_total(self):
        """全体の計測を開始"""
        self.total_start_time = time.time()

    def end_total(self) -> float:
        """全体の計測を終了"""
        if self.total_start_time is None:
            return 0.0
        elapsed = time.time() - self.total_start_time
        return elapsed

    def start_task(self, task_name: str):
        """タスクの計測を開始"""
        if self.current_task is not None:
            # 前のタスクを自動終了
            self.end_task()

        self.current_task = task_name
        self.task_start_time = time.time()

    def end_task(self) -> Optional[float]:
        """タスクの計測を終了"""
        if self.current_task is None or self.task_start_time is None:
            return None

        elapsed = time.time() - self.task_start_time

        record = {
            "task": self.current_task,
            "duration_seconds": elapsed,
            "duration_formatted": self._format_duration(elapsed),
            "timestamp": datetime.now().isoformat()
        }

        self.records.append(record)

        self.current_task = None
        self.task_start_time = None

        return elapsed

    @contextmanager
    def measure(self, task_name: str):
        """コンテキストマネージャーでタスク計測"""
        self.start_task(task_name)
        try:
            yield
        finally:
            self.end_task()

    def get_summary(self) -> Dict:
        """計測結果のサマリーを取得"""
        if not self.records:
            return {
                "total_tasks": 0,
                "total_duration": "0秒",
                "tasks": []
            }

        total_duration = sum(r["duration_seconds"] for r in self.records)

        return {
            "total_tasks": len(self.records),
            "total_duration": self._format_duration(total_duration),
            "total_duration_seconds": total_duration,
            "tasks": [
                {
                    "name": r["task"],
                    "duration": r["duration_formatted"],
                    "duration_seconds": r["duration_seconds"]
                }
                for r in self.records
            ]
        }

    def print_summary(self):
        """計測結果を見やすく表示"""
        summary = self.get_summary()

        print("\n" + "="*60)
        print("処理時間サマリー")
        print("="*60)

        if summary["total_tasks"] == 0:
            print("計測データがありません")
            return

        for i, task in enumerate(summary["tasks"], 1):
            print(f"{i}. {task['name']}: {task['duration']}")

        print("-"*60)
        print(f"合計タスク数: {summary['total_tasks']}")
        print(f"総処理時間: {summary['total_duration']}")
        print("="*60 + "\n")

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """秒数を読みやすい形式にフォーマット"""
        if seconds < 60:
            return f"{seconds:.2f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.2f}分"
        else:
            hours = seconds / 3600
            return f"{hours:.2f}時間"
