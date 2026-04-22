---
marp: true
theme: default
paginate: true
size: 16:9
header: '課題解決実習 / 3回目：ASR + LLM で音声認識精度を上げる'
footer: '湘南工科大学'
style: |
  section { font-size: 26px; }
  h1 { color: #1e3a8a; }
  h2 { color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 4px; }
  code { background: #f3f4f6; padding: 1px 4px; border-radius: 3px; }
  table { font-size: 22px; }
---

# ASR + LLM で音声認識精度を上げる

## 3回目 — 知覚情報処理の実践入門

- Whisper / WhisperX を動かす
- LLM に補正させる「危険さ」を理解する
- 検証ループで精度を上げる

---

## 今日のゴール

| フェーズ | 到達点 |
|---|---|
| 90分（今日） | WhisperX を動かし、ASR+LLM の **基本の型** が書ける |
| セルフ1 | 検証ループで hallucination を **自分で検出** できる |
| セルフ2 | WER を基準に **数字で精度を上げる** ことができる |

題材：`data/sample.mp4`（約7分22秒の講義動画）

---

## 前半45分のアジェンダ

1. ASR とは何か（10分）
2. Whisper / WhisperX の構造（10分）
3. LLM の幻覚（hallucination）（10分）
4. ASR + LLM 協調設計とループパターン（15分）

---

# 1. ASR とは何か

---

## ASR = Automatic Speech Recognition

音声を **テキストに変換する** 技術。

```
音声波形 → 特徴量抽出 → 音響モデル → 言語モデル → テキスト
        (MFCC/mel)   (AM)         (LM)
```

- 古典：HMM + GMM → DNN-HMM
- 現代：End-to-End（CTC / Attention / Transducer）
- 2022〜：大規模事前学習モデル（Whisper 等）

---

## ASR の代表的な誤り

| 種類 | 例 |
|---|---|
| 置換 | 「抗体」→「交代」 |
| 欠落 | 短い助詞の脱落 |
| 挿入 | 無音から単語を**幻覚** |
| 境界ずれ | 単語の切れ目を間違える |

評価指標：**WER（Word Error Rate）**

$$
\mathrm{WER} = \frac{S + D + I}{N}
$$

S=置換, D=削除, I=挿入, N=正解語数

---

# 2. Whisper / WhisperX

---

## Whisper（OpenAI, 2022）

- Encoder–Decoder **Transformer**
- 680,000 時間の多言語データで学習
- 強み：多言語・頑健性・句読点付き
- 弱み：**無音から単語を生成する**（hallucination）

```
音声 → log-Mel スペクトログラム
     → Encoder → Decoder（自己回帰） → テキスト
```

---

## WhisperX（2023〜）

Whisper に **word-level alignment** を後付け。

| 機能 | 提供 |
|---|---|
| 文字起こし | Whisper |
| 単語単位タイムスタンプ | wav2vec2 forced alignment |
| 話者分離 | pyannote |

→ **「この単語が、いつ、どこに対応するか」が正確に分かる**

---

## WhisperX の強みと限界

**強み**
- 単語単位の時刻が取れる
- 話者切り替えが追える
- バッチ処理が速い

**限界**
- 「音声的にあり得ない単語」のスコアを返さない
- Whisper 由来の hallucination は止められない
  - → 別の検証器（例：CTC-ASR）が必要

---

# 3. LLM の幻覚（hallucination）

---

## LLM は何を最大化しているか

真実ではなく **尤度**。

> 「入力が正しいと仮定して、もっとも自然に続きそうなトークン列」を出す。

ASR 誤りが混ざった入力を渡すと：

- それらしく **補完** してしまう
- 音声にない単語を **追加** してしまう
- 正しい部分まで **書き換える**

---

## なぜ ASR + LLM は危険なのか

```
音声（曖昧）→ ASR（誤り）→ LLM（補完）→ 出力（一見きれい）
```

**2段階の不確実性が累積**：

1. ASR の誤り（雑音・分布外音声・句切り）
2. LLM の幻覚（確信を持った嘘）

→ WER は小さくても、意味が反転することがある。

---

## 典型的な失敗例

```
音声：   "the patient denies chest pain"
ASR：    "the patient denies chest pain"
LLM補正："the patient denies severe chest pain"
```

- 「severe」は音声に **存在しない**
- でも文としては自然 → 検出しにくい
- 医療文脈なら **事故** になる

---

# 4. ASR + LLM 協調設計とループ

---

## 設計思想：LLM は「提案器」、ASR/音響は「裁判官」

| パターン | 仕組み |
|---|---|
| N-best + LLM | ASR の候補集合から LLM が選ぶ |
| Confidence-aware | ASR 信頼度に応じて LLM 介入を制御 |
| Joint | ASR と LLM を内部表現で統合 |
| **Verification loop** | **LLM 出力を音響で再検証** ← 今日の主軸 |

---

## Verification Loop の基本形

```
     Audio
       ↓
  [ ASR / WhisperX ]
       ↓
  [ Error Detection ]   ← 低 confidence 箇所
       ↓
  [ LLM （局所修正のみ）]
       ↓
  [ WhisperX 再 alignment ]
       ↓
   ok → finalize
  ng → reject / retry
```

---

## LLM に必ず課すルール

```
❌ 新しい単語の追加は禁止
✅ 既存単語の置換・削除のみ
✅ 変更した単語と理由を出力
✅ 確信がなければ変更しない
```

**プロンプトだけでは不十分** → 検証器で強制する。

---

## 今日の実践で作るもの

| ファイル | 内容 | フェーズ |
|---|---|---|
| `01_asr_basic.py` | WhisperX で生ログ取得 | 講義中 |
| `02_asr_llm.py` | LLM 補正 + 比較 | 講義中 |
| `03_validation.py` | alignment で幻覚検出 | セルフ1 |
| `04_accuracy.py` | WER 最適化ループ | セルフ2 |

---

# 後半45分：実践

---

## ハンズオン手順（ローカル）

```bash
cd 3回目
uv sync
cp .env.example .env   # LLM_URL / LLM_MODEL / LLM_API_KEY を設定

# [実践①] 生ログ取得
uv run python src/01_asr_basic.py

# [実践②] LLM で補正
uv run python src/02_asr_llm.py
```

Colab 版：`notebooks/colab.ipynb` を GPU ランタイムで開く。

---

## 実践で観察すべき点

1. **WhisperX の word-level タイムスタンプ** の中身を見る
2. **生ログと LLM 補正後** の diff を取る
3. LLM が **何を足したか** を確認する
4. その追加は **音声に存在していたか** を自分の耳で確認する

→ これで「LLM は嘘をつく」ことを **体感** する。

## セルフ1（90分）— `03_validation.py` で Level 2

**狙い**：LLM が出した補正テキストを WhisperX alignment で再検証し、幻覚を検出する。

1. `02_asr_llm_corrected.txt` を入力に `03_validation.py` 実行
2. `03_validation_report.json` を読む
   - `naive_added` / `llm_added` / `alignment_of_added` を比較
   - **score 低い語 = 幻覚候補** と判定
3. 元音声を聞いて疑わしい語が実在するか **耳で検証**
4. レポート：どの語が幻覚／どの語が真の補正か、理由付きで分類

→ 「LLM 出力を盲信しない検証ループ」の体得。

---

## セルフ2（90分）— `04_accuracy.py` で Level 3

**狙い**：CER/WER で **数字** に基づき prompt を改善する。

1. `01_asr_raw.txt` を手修正 → `results/04_reference.txt`（正解作りも学び）
2. variant ループ：`--variant strict / with_glossary / fewshot / reflect`、または `--all`
3. `04_wer_log.csv` の **CER / WER / len_ratio** を比較し、効いた prompt を定量判断
4. 自分で **新 variant** 追加（用語・few-shot 例・制約変更）→ 再測定
5. レポート：**仮説 → 実験 → 結果** の流れで改善理由を記述

**共通の学び所**：主観でなく CER/score で意思決定。prompt は仮説実験の単位＝変えたら必ず測る。


---

## まとめ

- ASR 単体は誤る
- LLM 単体は幻覚する
- **組み合わせ方を間違えると、誤りが増幅する**
- 正しい組み合わせ方＝ **LLM 提案 × ASR/音響 検証**

セルフスタディで：
- 検証ループを自分で実装
- WER を基準に改善を回す

---

## 参考資料

- WhisperX：https://github.com/m-bain/whisperX
- Whisper 論文：https://cdn.openai.com/papers/whisper.pdf
- `docs/` 内の 9 本の設計ノート
- Agentic Design Patterns（日本語）: https://github.com/sit-xinli/AgentDesignPatterns

---

## 本日のキーセンテンス

> LLM は **書き手** ではなく **校正者** として使う。
> 決定権は常に **音声** 側に置く。
