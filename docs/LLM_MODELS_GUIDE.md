# LLM APIモデル選択ガイド（2025年版）

各LLM APIで利用可能なモデルの一覧と推奨設定をまとめました。

## 目次
- [OpenAI](#openai)
- [Google Gemini](#google-gemini)
- [Anthropic Claude](#anthropic-claude)
- [推奨設定](#推奨設定)

---

## OpenAI

### 現行モデル（2025年12月時点）

#### GPT-5シリーズ（最新）
| モデル名 | 特徴 | 推奨用途 |
|---------|------|---------|
| `gpt-5.2` | 2025年12月リリースの最新モデル | 最高性能が必要なタスク |
| `gpt-5.1` | 2025年11月リリース（すぐに5.2に更新） | - |
| `gpt-5` | - | - |

#### GPT-4.1シリーズ
| モデル名 | 特徴 | 推奨用途 |
|---------|------|---------|
| `gpt-4.1` | GPT-4oの後継、より強力で安価 | 一般的なタスク |
| `gpt-4.1-mini` | 小型高速版、GPT-4o miniの後継 | 高速処理が必要なタスク |

#### GPT-4oシリーズ（レガシー）
| モデル名 | 特徴 | 推奨用途 | 状態 |
|---------|------|---------|------|
| `gpt-4o` | 音声入出力サポート | 音声処理が必要な場合のみ | レガシー |
| `gpt-4o-mini` | 小型版 | - | GPT-4.1 miniに置き換え推奨 |
| `gpt-4o-audio` | 音声入出力特化版 | 音声処理 | 現在も利用可能 |

#### GPT-4 Turboシリーズ（レガシー）
| モデル名 | 状態 |
|---------|------|
| `gpt-4-turbo` | レガシー |
| `gpt-4-turbo-preview` | レガシー |

#### GPT-3.5シリーズ（非推奨）
| モデル名 | 状態 | 注意 |
|---------|------|------|
| `gpt-3.5-turbo` | 非推奨 | 2024年6月17日以降、既存ユーザーのみ |
| `gpt-3.5-turbo-0613` | 廃止予定 | - |
| `gpt-3.5-turbo-16k-0613` | 廃止予定 | - |

### 推奨モデル（2025年12月）
```bash
# .envファイル設定例
OPENAI_MODEL=gpt-4o              # 一般用途
OPENAI_MODEL=gpt-4.1             # コストと性能のバランス
OPENAI_MODEL=gpt-4.1-mini        # 高速処理
OPENAI_MODEL=gpt-4o-audio        # 音声処理
```

---

## Google Gemini

### 現行モデル（2025年12月時点）

#### Gemini 3シリーズ（最新）
| モデル名 | 特徴 | 入力トークン | 推奨用途 |
|---------|------|------------|---------|
| `gemini-3-flash` | 最高速度、低コスト | 1,048,576 | 高頻度ワークフロー |
| `gemini-3-pro` | 最新の推論特化モデル | 1,048,576 | 複雑なエージェントタスク、コーディング |

**対応入力**: テキスト、画像、動画、音声、PDF
**機能**: 検索グラウンディング、関数呼び出し、コード実行

#### Gemini 2.5シリーズ
| モデル名 | 特徴 | 入力トークン | 推奨用途 |
|---------|------|------------|---------|
| `gemini-2.5-pro` | 最強モデル、適応的思考機能 | 1,048,576 | 複雑な推論、長文解析 |
| `gemini-2.5-flash` | 安定版、価格性能バランス | 1,048,576 | 一般用途 |
| `gemini-2.5-flash-lite` | 軽量高速版 | - | 単純な高頻度タスク |

**対応入力**: 音声、画像、動画、テキスト、PDF
**機能**: Google Maps統合、検索グラウンディング

#### Gemini 2.0シリーズ
| モデル名 | 特徴 | コンテキスト | 推奨用途 |
|---------|------|------------|---------|
| `gemini-2.0-flash` | 次世代機能、ネイティブツール利用 | 1M トークン | 一般用途 |
| `gemini-2.0-flash-lite` | 超効率的 | - | 速度優先タスク |

#### 廃止されたモデル
| モデル名 | 状態 | 備考 |
|---------|------|------|
| `gemini-pro` (1.5) | 完全廃止 | 2025年4月29日に廃止 |
| `gemini-1.5-pro` | 完全廃止 | 2025年4月29日に廃止 |
| `gemini-1.5-flash` | 完全廃止 | 2025年4月29日に廃止 |

### 推奨モデル（2025年12月）
```bash
# .envファイル設定例
GEMINI_MODEL=gemini-3-flash      # 高速処理
GEMINI_MODEL=gemini-3-pro        # 複雑なタスク
GEMINI_MODEL=gemini-2.5-pro      # 最高性能
GEMINI_MODEL=gemini-2.5-flash    # バランス型
```

---

## Anthropic Claude

### 現行モデル（2025年12月時点）

#### Claude 4.5シリーズ（最新）
| モデル名 | リリース日 | 特徴 | 価格（API） | 推奨用途 |
|---------|----------|------|------------|---------|
| `claude-opus-4.5-20251101` | 2025年11月24日 | 最も強力 | $5/M入力, $25/M出力 | 最高性能が必要なタスク |
| `claude-sonnet-4.5-20250929` | 2025年9月29日 | コーディング、エージェント特化 | $3/M入力, $15/M出力 | コーディング、コンピュータ操作 |

#### Claude 4.1シリーズ
| モデル名 | リリース日 | 特徴 | 推奨用途 |
|---------|----------|------|---------|
| `claude-opus-4.1-20250805` | 2025年8月5日 | エージェントタスク、推論強化 | エージェントワークフロー |

#### Claude 4シリーズ
| モデル名 | リリース日 | 特徴 | 推奨用途 |
|---------|----------|------|---------|
| `claude-opus-4-20250522` | 2025年5月22日 | Claude 3からの進化版 | 一般用途 |
| `claude-sonnet-4-20250522` | 2025年5月22日 | バランス型 | 一般用途 |

#### モデルティア
Anthropicは3つのティアでモデルを分類：
- **Haiku**: 最速・最小（低コスト）
- **Sonnet**: バランス型（中コスト）
- **Opus**: 最高性能（高コスト）

#### 廃止されたモデル
| モデル名 | 廃止日 | 備考 |
|---------|-------|------|
| `claude-3-opus-20240229` | 2025年6月30日廃止 | 2026年1月5日完全削除 |
| `claude-3-sonnet-20240229` | 2025年7月21日完全削除 | - |
| `claude-2.1` | 2025年7月21日完全削除 | - |

### 対応機能
- テキスト入力・出力
- 画像入力
- 多言語対応
- ビジョン機能

### 推奨モデル（2025年12月）
```bash
# .envファイル設定例
ANTHROPIC_MODEL=claude-opus-4.5-20251101      # 最高性能
ANTHROPIC_MODEL=claude-sonnet-4.5-20250929    # コーディング特化
ANTHROPIC_MODEL=claude-opus-4.1-20250805      # エージェント用途
ANTHROPIC_MODEL=claude-opus-4-20250522        # 一般用途
```

---

## 推奨設定

### Multi-LLM Agentでの推奨設定（2025年12月）

#### バランス重視（推奨）
```bash
# .env
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.5-flash
ANTHROPIC_MODEL=claude-sonnet-4.5-20250929
AGGREGATION_MODEL=gpt-4o
```

#### 最高性能重視
```bash
# .env
OPENAI_MODEL=gpt-5.2
GEMINI_MODEL=gemini-3-pro
ANTHROPIC_MODEL=claude-opus-4.5-20251101
AGGREGATION_MODEL=gpt-5.2
```

#### コスト重視
```bash
# .env
OPENAI_MODEL=gpt-4.1-mini
GEMINI_MODEL=gemini-3-flash
ANTHROPIC_MODEL=claude-sonnet-4-20250522
AGGREGATION_MODEL=gpt-4.1-mini
```

#### コーディング特化
```bash
# .env
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-3-pro
ANTHROPIC_MODEL=claude-sonnet-4.5-20250929
AGGREGATION_MODEL=claude-sonnet-4.5-20250929
```

---

## 重要な注意事項

### 1. APIパラメータの変更
**OpenAI API（2024年後半〜）**:
- `max_tokens` → `max_completion_tokens` に変更
- 古いパラメータは一部モデルで非対応

### 2. モデル名の正確性
- モデル名は大文字小文字を区別します
- 日付サフィックス（例: `20251101`）が必要なモデルもあります
- 公式ドキュメントで最新のモデル名を確認してください

### 3. 廃止予定の確認
各APIで定期的にモデルが廃止されます：
- OpenAI: https://platform.openai.com/docs/deprecations
- Gemini: https://ai.google.dev/gemini-api/docs/changelog
- Claude: https://platform.claude.com/docs/en/about-claude/model-deprecations

### 4. レート制限
無料/有料プランによってレート制限が異なります。
特にGeminiの無料tierは制限が厳しいので注意してください。

---

## 参考リンク

- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
- [Google Gemini Models](https://ai.google.dev/gemini-api/docs/models)
- [Anthropic Claude Models](https://platform.claude.com/docs/en/about-claude/models/overview)

---

**更新日**: 2025年12月23日
**次回更新推奨**: 2026年1月（四半期ごとに確認推奨）
