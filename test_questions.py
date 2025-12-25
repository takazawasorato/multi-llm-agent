#!/usr/bin/env python3
"""
3つの質問でMulti-LLM Agentをテスト
"""

import asyncio
import sys
from multi_llm_agent.main import MultiLLMAgent
from multi_llm_agent.time_tracker import TimeTracker

# 3つの質問
QUESTIONS = [
    """疾患と正常のscRNAから創薬標的を見つけたい。scRNAは疾患と正常の細胞分布が異なるため、どのように同一細胞をそろえて、DEGをとれば良いか？""",

    """遺伝子発現データセットのL1000は、KD、OE、薬剤摂動のデータセットであるが、900程度のシグネチャー遺伝子の発現データしかなく使いにくい。KD,OE,薬剤摂動の全遺伝子の発現データで利用可能なデータセットはあるか？網羅的に調査してくれ。特に、アクセス、入手方法も教えてくれ""",

    """低分子創薬のインシリコ手法の学習セットにできるデータベースを網羅的に調査してください。アクセス方法も付与してください。"""
]


async def test_question(agent, question_num, question):
    """1つの質問をテスト"""
    print("\n" + "="*100)
    print(f"質問 {question_num}/3")
    print("="*100)
    print(f"質問: {question}")
    print("="*100)

    try:
        result = await agent.query(
            question,
            use_search=True,      # 網羅的検索を使用
            synthesize=True       # 回答を統合
        )

        # 統合回答を表示
        if result.get("synthesized_response"):
            print("\n" + "="*100)
            print("統合回答")
            print("="*100)
            print(result["synthesized_response"])
            print("="*100)

        # 時間サマリーを表示
        if result.get("time_summary"):
            print("\n処理時間サマリー:")
            summary = result["time_summary"]
            print(f"  総処理時間: {summary['total_duration']}")
            print(f"  タスク数: {summary['total_tasks']}")
            for task in summary['tasks']:
                print(f"    - {task['name']}: {task['duration']}")

        # 検索結果のサマリー
        if result.get("search_results"):
            print("\n検索結果サマリー:")
            for source, results in result["search_results"].items():
                print(f"  {source}: {len(results)}件")

        # 比較表
        if result.get("comparison"):
            print("\n" + result["comparison"])

        return result

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """メイン処理"""
    print("="*100)
    print("Multi-LLM Agent 動作確認テスト")
    print("="*100)

    # エージェントを作成
    print("\nエージェントを初期化中...")
    agent = MultiLLMAgent()

    # 利用可能なLLMプロバイダーを表示
    available_providers = agent.orchestrator.get_available_providers()
    print(f"利用可能なLLMプロバイダー: {', '.join(available_providers)}")

    if not available_providers:
        print("\nエラー: 利用可能なLLMプロバイダーがありません。")
        print(".envファイルでAPIキーを設定してください。")
        sys.exit(1)

    # 全体の時間計測開始
    total_tracker = TimeTracker()
    total_tracker.start_total()

    # 各質問を実行
    results = []
    for i, question in enumerate(QUESTIONS, 1):
        result = await test_question(agent, i, question)
        results.append(result)

        # 質問間に少し待機
        if i < len(QUESTIONS):
            print("\n次の質問まで3秒待機...")
            await asyncio.sleep(3)

    # 全体の時間を表示
    total_time = total_tracker.end_total()

    print("\n" + "="*100)
    print("全テスト完了")
    print("="*100)
    print(f"全体の処理時間: {total_time/60:.2f}分 ({total_time:.2f}秒)")

    # 成功/失敗のサマリー
    success_count = sum(1 for r in results if r is not None)
    print(f"\n成功: {success_count}/{len(QUESTIONS)}")


if __name__ == "__main__":
    asyncio.run(main())
