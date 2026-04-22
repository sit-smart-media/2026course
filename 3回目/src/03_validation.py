"""[セルフスタディ1] WhisperX 検証ループで LLM の幻覚を検出。

考え方：
  LLM が勝手に追加した単語は、WhisperX の word-level alignment を通らない。
  修正後テキストを再度 WhisperX で alignment し、
  - 追加された単語に対応する音声区間があるか
  - 時刻が既存語と自然につながるか
  を照合する。

実装はシンプル版：
  1. 修正前テキストから単語集合 W_raw を作る
  2. 修正後テキストから単語集合 W_fix を作る
  3. W_fix - W_raw = 追加候補 → 追加はすべて疑う
  4. 追加候補を re-alignment して、信頼できる区間があるか確認

実行：
  uv run python src/03_validation.py
"""
from __future__ import annotations

import argparse
import re

import torch
import whisperx

from utils import LLMConfig, RESULTS, SAMPLE_AUDIO, load_json, save_json, save_text

VERIFY_PROMPT = """あなたは ASR 後処理の監査者です。
以下の「修正前テキスト」「修正後テキスト」を比較し、
修正後にだけ出現する単語のうち、音声由来でない可能性が高いものをリストアップしてください。

制約：
- 修正前に無かった内容語（名詞・動詞・形容詞・数値）を **すべて** 挙げる
- 助詞・読点・句読点の違いは無視
- 出力形式は JSON：{"added_words": ["word1", "word2", ...]}
"""


def tokenize(text: str) -> list[str]:
    # 日本語・英語両対応の素朴なトークナイズ
    return re.findall(r"[A-Za-z]+|[一-龥ぁ-んァ-ヶ]+|\d+", text)


def added_words(before: str, after: str) -> list[str]:
    b = set(tokenize(before))
    a = tokenize(after)
    return [w for w in a if w not in b]


def check_with_llm(before: str, after: str, cfg: LLMConfig) -> dict:
    client = cfg.client()
    resp = client.chat.completions.create(
        model=cfg.model,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": VERIFY_PROMPT},
            {
                "role": "user",
                "content": f"[修正前]\n{before}\n\n[修正後]\n{after}",
            },
        ],
    )
    import json as _json

    return _json.loads(resp.choices[0].message.content)


def realign(audio_path: str, text: str, language: str) -> list[dict]:
    """LLM修正後テキストを音声に forced-align し、単語タイムスタンプを返す。"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    audio = whisperx.load_audio(audio_path)
    align_model, metadata = whisperx.load_align_model(
        language_code=language, device=device
    )
    # segments は 1 つにまとめて渡す
    fake_segments = [{"start": 0.0, "end": len(audio) / 16000, "text": text}]
    out = whisperx.align(
        fake_segments, align_model, metadata, audio, device=device,
        return_char_alignments=False,
    )
    words = []
    for seg in out["segments"]:
        words.extend(seg.get("words", []) or [])
    return words


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default=str(RESULTS / "01_asr_raw.txt"))
    parser.add_argument("--fixed", default=str(RESULTS / "02_asr_llm_corrected.txt"))
    parser.add_argument(
        "--meta", default=str(RESULTS / "01_asr_raw.json"),
        help="言語判定を取得する 01 の出力 JSON",
    )
    parser.add_argument("--audio", default=str(SAMPLE_AUDIO))
    args = parser.parse_args()

    from pathlib import Path

    raw = Path(args.raw).read_text(encoding="utf-8")
    fixed = Path(args.fixed).read_text(encoding="utf-8")
    meta = load_json(Path(args.meta))
    language = meta.get("language", "ja")

    # 1. 素朴な集合差分
    naive_added = added_words(raw, fixed)
    print(f"[check] naive added-word count: {len(naive_added)}")

    # 2. LLM に精緻な差分抽出を依頼
    cfg = LLMConfig.from_env()
    llm_added = check_with_llm(raw, fixed, cfg)
    print(f"[check] llm-detected added-words: {llm_added.get('added_words', [])}")

    # 3. 修正後テキストを forced-align し、追加候補語の位置を確認
    print("[check] re-aligning corrected text...")
    words = realign(args.audio, fixed, language)

    suspicious = []
    added_set = set(llm_added.get("added_words", [])) | set(naive_added)
    for w in words:
        token = w.get("word", "").strip()
        score = w.get("score")
        if token in added_set:
            suspicious.append(
                {"word": token, "start": w.get("start"), "end": w.get("end"), "score": score}
            )

    report = {
        "language": language,
        "naive_added": naive_added,
        "llm_added": llm_added.get("added_words", []),
        "alignment_of_added": suspicious,
    }
    save_json(RESULTS / "03_validation_report.json", report)

    lines = ["# Validation Report", "", f"Language: {language}", ""]
    lines.append(f"Added words (naive): {naive_added}")
    lines.append(f"Added words (LLM):   {llm_added.get('added_words', [])}")
    lines.append("")
    lines.append("## Alignment check (lower score = lower confidence)")
    for s in suspicious:
        lines.append(
            f"- {s['word']} @ {s['start']:.2f}-{s['end']:.2f} score={s['score']}"
        )
    save_text(RESULTS / "03_validation_report.md", "\n".join(lines))
    print("[check] saved: results/03_validation_report.{json,md}")


if __name__ == "__main__":
    main()
