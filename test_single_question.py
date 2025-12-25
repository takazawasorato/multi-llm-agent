#!/usr/bin/env python3
"""
1つの質問で動作確認
"""

import asyncio
from multi_llm_agent.main import MultiLLMAgent

async def main():
    print("="*80)
    print("Multi-LLM Agent 簡易テスト")
    print("="*80)

    agent = MultiLLMAgent()

    # 利用可能なプロバイダーを確認
    available = agent.orchestrator.get_available_providers()
    print(f"\n利用可能なプロバイダー: {', '.join(available)}")

    if not available:
        print("エラー: プロバイダーが設定されていません")
        return

    # テスト質問
    question = "疾患と正常のscRNAから創薬標的を見つけたい。scRNAは疾患と正常の細胞分布が異なるため、どのように同一細胞をそろえて、DEGをとれば良いか？"

    print(f"\n質問: {question}\n")
    print("処理中...\n")

    result = await agent.query(
        question,
        use_search=True,
        synthesize=True
    )

    # 結果表示
    if result.get("synthesized_response"):
        print("\n" + "="*80)
        print("統合回答")
        print("="*80)
        print(result["synthesized_response"])
        print("="*80)

    # 各LLMの回答状況
    if result.get("llm_responses"):
        print("\n各LLMの回答状況:")
        for provider, response in result["llm_responses"].items():
            status = "成功" if "error" not in response.metadata else "エラー"
            print(f"  {provider}: {status}")
            if status == "エラー":
                print(f"    詳細: {response.metadata.get('error', '')[:100]}...")

    # 時間サマリー
    if result.get("time_summary"):
        print(f"\n総処理時間: {result['time_summary']['total_duration']}")

if __name__ == "__main__":
    asyncio.run(main())
