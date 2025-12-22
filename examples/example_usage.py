"""
Multi-LLM Agentの使用例
"""

import asyncio
from multi_llm_agent.main import MultiLLMAgent
from multi_llm_agent.config import Config


async def basic_example():
    """基本的な使用例"""
    print("="*80)
    print("例1: 基本的な使用方法")
    print("="*80)

    # エージェントを作成
    agent = MultiLLMAgent()

    # 質問を実行
    question = "Transformerアーキテクチャの主要な特徴について教えてください"
    result = await agent.query(question, use_search=True, synthesize=True)

    print("\n最終的な統合回答:")
    print(result["synthesized_response"])


async def search_only_example():
    """検索のみの例"""
    print("\n" + "="*80)
    print("例2: 検索のみ（LLMクエリなし）")
    print("="*80)

    agent = MultiLLMAgent()

    # 検索のみを実行
    search_results = await agent.search_agent.comprehensive_search(
        "機械学習 最新手法",
        iterations=2
    )

    # 結果のサマリーを表示
    summary = agent.search_agent.format_results_summary(search_results)
    print(summary)


async def llm_only_example():
    """LLMクエリのみの例（検索なし）"""
    print("\n" + "="*80)
    print("例3: 複数LLMクエリのみ（検索なし）")
    print("="*80)

    agent = MultiLLMAgent()

    question = "量子コンピュータの仕組みを簡単に説明してください"
    result = await agent.query(question, use_search=False, synthesize=True)

    # 各LLMの回答を比較
    print(result["comparison"])


async def custom_config_example():
    """カスタム設定の例"""
    print("\n" + "="*80)
    print("例4: カスタム設定を使用")
    print("="*80)

    # カスタム設定を作成
    custom_config = Config.from_env()
    custom_config.search.max_iterations = 5  # 探索回数を増やす
    custom_config.search.results_per_iteration = 15  # 取得件数を増やす
    custom_config.verbose = True  # 詳細ログを有効化

    agent = MultiLLMAgent(config=custom_config)

    question = "深層学習における過学習の対策方法"
    result = await agent.query(question, use_search=True, synthesize=True)

    print(f"\n検索で取得した総件数:")
    for source, results in result["search_results"].items():
        print(f"  {source}: {len(results)}件")


async def comparison_example():
    """回答比較の例"""
    print("\n" + "="*80)
    print("例5: 複数LLMの回答を詳細に比較")
    print("="*80)

    agent = MultiLLMAgent()

    question = "ブロックチェーンの利点と欠点を教えてください"
    result = await agent.query(question, use_search=False, synthesize=False)

    # 各LLMの回答を表示
    formatted = agent.aggregator.format_responses(result["llm_responses"])
    print(formatted)

    # 比較表を表示
    print(result["comparison"])


def sync_example():
    """同期版の使用例"""
    print("\n" + "="*80)
    print("例6: 同期版API（asyncioなし）")
    print("="*80)

    agent = MultiLLMAgent()

    question = "強化学習とは何ですか？"

    # 同期版を使用
    result = agent.query_sync(question, use_search=True, synthesize=True)

    print("\n統合回答:")
    print(result["synthesized_response"])

    print("\n処理時間:")
    print(result["time_summary"]["total_duration"])


async def direct_component_usage():
    """コンポーネントを直接使用する例"""
    print("\n" + "="*80)
    print("例7: コンポーネントを個別に使用")
    print("="*80)

    from multi_llm_agent.orchestrator import MultiLLMOrchestrator
    from multi_llm_agent.config import Config

    config = Config.from_env()
    orchestrator = MultiLLMOrchestrator(config)

    # 特定のLLMのみを使用
    question = "ニューラルネットワークとは？"
    available_providers = orchestrator.get_available_providers()
    print(f"利用可能なプロバイダー: {available_providers}")

    if available_providers:
        # 最初のプロバイダーのみを使用
        responses = await orchestrator.query_specific(
            [available_providers[0]],
            question
        )

        for provider, response in responses.items():
            print(f"\n【{provider}】")
            print(response.content)


async def main():
    """全ての例を実行"""

    # 基本例
    await basic_example()

    # 他の例（コメントアウトを外して実行）
    # await search_only_example()
    # await llm_only_example()
    # await custom_config_example()
    # await comparison_example()
    # sync_example()
    # await direct_component_usage()


if __name__ == "__main__":
    asyncio.run(main())
