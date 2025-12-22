# Multi-LLM Agent System

複数のLLM（Large Language Model）を統合し、網羅的な調査と回答統合を行うエージェントシステムです。

## 特徴

### 1. 複数LLMの統合
- OpenAI GPT-4
- Google Gemini
- Anthropic Claude

これらのLLMに並列でクエリを送信し、複数の視点からの回答を取得します。

### 2. 網羅的な探索機能
- **複数回の探索イテレーション**: 初期調査の網羅性を高めるため、複数回の探索を自動実行
- **クエリの多様化**: イテレーションごとに検索クエリを変化させ、より広範な情報を収集
- **複数の検索ソース**:
  - arXiv（学術論文）
  - Web検索（DuckDuckGo）
  - （拡張可能）

### 3. 回答の統合・分析
- 複数のLLM回答を自動比較
- 矛盾点の検出
- 総合的な回答を生成
- 処理時間とトークン使用量の分析

### 4. 時間計測機能
- 各処理ステップの時間を自動記録
- 開発・最適化のための詳細なタイムトラッキング

## システムアーキテクチャ

```
ユーザー質問
    ↓
ComprehensiveSearchAgent (網羅的探索)
    ├→ arXiv検索 (複数回)
    ├→ Web検索 (複数回)
    └→ 検索結果の重複排除・統合
    ↓
収集された情報
    ↓
MultiLLMOrchestrator (並列LLMクエリ)
    ├→ OpenAI GPT
    ├→ Google Gemini
    └→ Anthropic Claude
    ↓
各LLMの回答
    ↓
ResponseAggregator (回答統合)
    ├→ 回答の比較・分析
    ├→ 矛盾点の検出
    └→ 統合回答の生成
    ↓
最終回答 + 時間サマリー
```

## インストール

### 1. リポジトリのクローン

```bash
cd /path/to/agent
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、APIキーを設定します：

```bash
cp .env.example .env
```

`.env`を編集：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 使い方

### 基本的な使用方法

```python
from multi_llm_agent.main import MultiLLMAgent

# エージェントを作成
agent = MultiLLMAgent()

# 質問を実行（同期版）
result = agent.query_sync(
    "Transformerアーキテクチャについて教えてください",
    use_search=True,      # 検索を使用
    synthesize=True       # 回答を統合
)

# 統合回答を表示
print(result["synthesized_response"])

# 時間サマリーを表示
print(result["time_summary"])
```

### 非同期版

```python
import asyncio
from multi_llm_agent.main import MultiLLMAgent

async def main():
    agent = MultiLLMAgent()

    result = await agent.query(
        "深層学習の最新動向について",
        use_search=True,
        synthesize=True
    )

    print(result["synthesized_response"])

asyncio.run(main())
```

### CLIから使用

```bash
python -m multi_llm_agent.main "量子コンピュータについて教えて"
```

### カスタム設定

```python
from multi_llm_agent.main import MultiLLMAgent
from multi_llm_agent.config import Config

# カスタム設定を作成
config = Config.from_env()
config.search.max_iterations = 5           # 探索回数を増やす
config.search.results_per_iteration = 15   # 取得件数を増やす
config.verbose = True                       # 詳細ログを有効化

agent = MultiLLMAgent(config=config)
result = agent.query_sync("機械学習について")
```

## 設定項目

### 検索設定

- `SEARCH_MAX_ITERATIONS`: 探索の繰り返し回数（デフォルト: 3）
- `SEARCH_RESULTS_PER_ITERATION`: 1回あたりの取得件数（デフォルト: 10）
- `ENABLE_ARXIV`: arXiv検索を有効化（デフォルト: true）
- `ENABLE_WEB_SEARCH`: Web検索を有効化（デフォルト: true）

### LLM設定

各LLMごとに以下を設定可能：
- `MODEL`: 使用するモデル
- `TEMPERATURE`: 温度パラメータ（0.0-1.0）
- `MAX_TOKENS`: 最大トークン数

### その他

- `ENABLE_PARALLEL`: 並列処理を有効化（デフォルト: true）
- `AGGREGATION_MODEL`: 回答統合に使用するモデル
- `LLM_TIMEOUT`: LLMタイムアウト（秒）
- `SEARCH_TIMEOUT`: 検索タイムアウト（秒）

## プロジェクト構造

```
multi_llm_agent/
├── __init__.py              # パッケージ初期化
├── config.py                # 設定管理
├── time_tracker.py          # 時間計測
├── orchestrator.py          # 複数LLM統合マネージャー
├── search_agent.py          # 網羅的探索エージェント
├── aggregator.py            # 回答統合エンジン
├── main.py                  # メインエントリーポイント
├── llm_providers/           # LLMプロバイダー
│   ├── __init__.py
│   ├── base.py              # 基底クラス
│   ├── openai_provider.py   # OpenAI実装
│   ├── gemini_provider.py   # Gemini実装
│   └── anthropic_provider.py # Claude実装
└── searchers/               # 検索エンジン
    ├── __init__.py
    ├── base.py              # 基底クラス
    ├── arxiv_searcher.py    # arXiv検索
    └── web_searcher.py      # Web検索

examples/
└── example_usage.py         # 使用例

requirements.txt             # 依存関係
.env.example                 # 環境変数サンプル
README.md                    # このファイル
```

## 主要機能の詳細

### 1. 網羅的探索

`ComprehensiveSearchAgent`は以下の戦略で網羅性を向上：

1. **複数回のイテレーション**: デフォルトで3回の探索を実行
2. **クエリの多様化**: イテレーションごとに検索キーワードを変更
   - オリジナルクエリ
   - "クエリ + overview"
   - "クエリ + tutorial"
   - "クエリ + best practices"
   - など
3. **重複排除**: URLベースで重複結果を自動除外
4. **複数ソース**: 論文、Web、データベースなど多様な情報源

### 2. 複数LLM統合

`MultiLLMOrchestrator`の特徴：

- **並列実行**: 複数のLLMに同時にクエリを送信（高速化）
- **エラーハンドリング**: 一部のLLMが失敗しても処理を継続
- **統一インターフェース**: 異なるLLM APIを統一的に扱う

### 3. 回答統合

`ResponseAggregator`の機能：

- **回答比較**: 各LLMの回答長、処理時間、トークン数を比較
- **矛盾検出**: 異なる回答間の矛盾を特定
- **統合生成**: LLMを使って複数回答から総合的な回答を生成
- **比較表作成**: 見やすい比較表を自動生成

### 4. 時間計測

`TimeTracker`で以下を記録：

- 各処理ステップの所要時間
- 総処理時間
- 詳細なタイムサマリー

## 使用例

詳細な使用例は`examples/example_usage.py`を参照してください：

```bash
python examples/example_usage.py
```

## 開発時間の記録

このシステムの開発には、各コンポーネントの実装時間が`TimeTracker`によって記録されます。
実際の使用時にも、各処理の所要時間が自動的に計測・表示されます。

## 拡張性

### 新しいLLMプロバイダーの追加

1. `llm_providers/`に新しいプロバイダーを実装
2. `BaseLLMProvider`を継承
3. `orchestrator.py`に登録

### 新しい検索ソースの追加

1. `searchers/`に新しい検索エンジンを実装
2. `BaseSearcher`を継承
3. `search_agent.py`に登録

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

質問や問題がある場合は、GitHubのIssuesで報告してください。
