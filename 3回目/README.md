# 3回目：ASR + LLM で音声認識精度を上げる

**テーマ**：WhisperX（ASR）と OpenAI互換LLMを協調させ、講義音声の文字起こし精度を実用レベルまで引き上げる。

- 対象：大学 2〜3年生（Python 基本文法、uv・git 使用経験あり）
- 題材：`data/sample.mp4`（約7分22秒の講義動画）
- 時間：**90分（講義+基本実践） + セルフスタディ 90分 × 2回**

---

## 学習目標

| 到達レベル | 内容 |
|---|---|
| Level 1（90分で到達） | WhisperX で文字起こしを実行し、ASR の仕組みと誤りパターンを説明できる |
| Level 2（セルフ1で到達） | LLM で ASR 結果を補正し、WhisperX alignment で hallucination を検出できる |
| Level 3（セルフ2で到達） | ルール設計・プロンプト制約・検証ループで認識精度を定量的に改善できる |

---

## リポジトリ構成

```
3回目/
├── README.md               # このファイル
├── slides/
│   └── slides.md           # Marp スライド（前半45分講義）
├── src/
│   ├── utils.py            # 共通ユーティリティ
│   ├── 01_asr_basic.py     # [基本] WhisperX 文字起こし
│   ├── 02_asr_llm.py       # [基本] ASR + LLM 補正
│   ├── 03_validation.py    # [セルフ1] WhisperX 検証ループ
│   └── 04_accuracy.py      # [セルフ2] 精度向上ループ
├── notebooks/
│   └── colab.ipynb         # Colab 用統合ノートブック
├── data/
│   └── sample.mp4          # 題材音声
├── docs/                   # 参考資料（9本の設計ノート）
├── results/                # 実行結果の保存先
├── pyproject.toml          # uv 用
├── requirements.txt        # pip / Colab 用
├── .env.example            # API キー設定例
└── .gitignore
```

---

## 90分メインの流れ

| 時間 | 内容 | 成果 |
|---|---|---|
| 00–15 | 講義①：ASR の基礎と Whisper / WhisperX | 仕組み理解 |
| 15–30 | 講義②：LLM の hallucination と ASR+LLM 協調設計 | リスク理解 |
| 30–45 | 講義③：Loop Pattern と検証アーキテクチャ | 設計力 |
| 45–70 | 実践①：`src/01_asr_basic.py` を動かす | 生ログ取得 |
| 70–90 | 実践②：`src/02_asr_llm.py` を動かして比較 | 効果体感 |

---

## セルフスタディ（各90分）

### セルフ1：検証ループを実装する
- 課題：LLM が勝手に単語を追加していないか、WhisperX の word-level alignment で検証する
- スクリプト：`src/03_validation.py`
- 出力：修正前テキスト / 修正後テキスト / alignment 照合結果

### セルフ2：精度を定量的に上げる
- 課題：WER（Word Error Rate）を基準に、プロンプト設計・制約ルールを回して精度を改善する
- スクリプト：`src/04_accuracy.py`
- 出力：WER 推移、改善理由のレポート

---

## 環境構築

### A. ローカル（uv）

```bash
cd 3回目
uv sync
cp .env.example .env
# .env を自分の LiteLLM プロキシ情報で書き換える
```

WhisperX は GPU 推奨（CUDA 11.8+ / 12.x）。CPU でも動くが `large-v3` は重い。CPU のみの PC では `--model small` から試す。

### B. Google Colab（GPU 無料枠）

`notebooks/colab.ipynb` を Colab で開いて最上部セルから実行。GPU ランタイムに切り替えること（ランタイム → ランタイムのタイプを変更 → T4 GPU）。

### 必要な環境変数（`.env`）

```
LLM_URL=https://<your-litellm-proxy>/
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...
```

---

## 実行例（基本）

```bash
# [実践①] WhisperX で文字起こし
uv run python src/01_asr_basic.py

# [実践②] LLM で補正
uv run python src/02_asr_llm.py
```

結果は `results/` に JSON + TXT で保存される。

---

## 参考資料（docs/）

| ファイル | 内容 |
|---|---|
| 1.ASR+LLM.md | 協調設計の概念整理 |
| 2.LoopPattern.md | 4種類のループパターン |
| 3.Whisperx.md | WhisperX の本質と検証利用 |
| 4.Whisperx+CTC-ASR.md | 二段検証アーキテクチャ |
| 5.Medical.md | 医用向け hallucination-safe loop |
| 6.Dictionary.md | 専門用語辞書の安全な使い方 |
| 7.RAG.md | RAG を検証器として使う設計 |
| 8.multimodel.md | マルチモーダル生成AI併用 |
| 9.file2prompt.md | プロンプトをファイル化する運用 |

---

## 評価・提出物

セルフスタディ2の終了時に以下を提出（GitHub リポジトリ化を推奨）：

1. `results/` の実行結果（JSON / TXT）
2. 改善プロンプトの版管理履歴（`src/04_accuracy.py` と対応）
3. 1〜2分程度の気づきレポート（`REPORT.md`）

---

## トラブルシュート

- `torch` がインストールできない → CUDA 版と Python 版の整合を `uv sync --index-strategy unsafe-best-match` で調整
- WhisperX の pyannote モデルが落とせない → Hugging Face アクセストークンを `HF_TOKEN` で渡す
- LiteLLM から `401` → `.env` の `LLM_API_KEY` を確認
