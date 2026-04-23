"""[基本実践①-1] openai-whisper で sample.mp3 を文字起こし。

目的：
  - whisperx なしで標準 whisper を使う
  - セグメント単位タイムスタンプを観察する
  - 結果を results/ に保存する

実行：
  uv run python src/01_1_asr_basic.py
"""
from __future__ import annotations

import argparse
import time

import torch
import whisper

from utils import RESULTS, SAMPLE_AUDIO, ASRResult, save_json, save_text


def transcribe(
    audio_path: str,
    model_size: str = "small",
    language: str | None = None,
) -> ASRResult:
    device = "cpu"
    print(f"[asr] device={device} model={model_size}")

    t0 = time.time()
    model = whisper.load_model(model_size)
    options = {"language": language} if language else {}
    result = model.transcribe(str(audio_path), **options)

    detected_lang = result.get("language", "unknown")
    print(f"[asr] language={detected_lang} segments={len(result['segments'])}")
    print(f"[asr] done in {time.time() - t0:.1f}s")

    full_text = " ".join(seg["text"].strip() for seg in result["segments"])
    return ASRResult(text=full_text, segments=result["segments"], language=detected_lang)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", default=str(SAMPLE_AUDIO))
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="ja", help="ja / en / None(auto)")
    args = parser.parse_args()

    result = transcribe(args.audio, model_size=args.model, language=args.language)

    save_text(RESULTS / "01_1_asr_raw.txt", result.text)
    save_json(
        RESULTS / "01_1_asr_raw.json",
        {"language": result.language, "segments": result.segments},
    )
    print(f"[asr] saved: results/01_1_asr_raw.txt / .json")
    print(f"[asr] segment count: {len(result.segments)}")
    print("---- preview ----")
    print(result.text[:400])


if __name__ == "__main__":
    main()
