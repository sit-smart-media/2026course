"""[基本実践①] WhisperX で sample.mp4 を文字起こし。

目的：
  - ASR の生ログを取得する
  - 単語単位タイムスタンプを観察する
  - 結果を results/ に保存する

実行：
  uv run python src/01_asr_basic.py
"""
from __future__ import annotations

import argparse
import time

import torch
import whisperx

from utils import RESULTS, SAMPLE_AUDIO, ASRResult, save_json, save_text


def transcribe(
    audio_path: str,
    model_size: str = "large-v3",
    language: str | None = None,
    batch_size: int = 8,
) -> ASRResult:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"[asr] device={device} model={model_size} compute_type={compute_type}")

    t0 = time.time()
    model = whisperx.load_model(model_size, device=device, compute_type=compute_type)
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=batch_size, language=language)
    detected_lang = result["language"]
    print(f"[asr] language={detected_lang} segments={len(result['segments'])}")

    align_model, metadata = whisperx.load_align_model(
        language_code=detected_lang, device=device
    )
    aligned = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device=device,
        return_char_alignments=False,
    )
    print(f"[asr] alignment done in {time.time() - t0:.1f}s")

    full_text = " ".join(seg["text"].strip() for seg in aligned["segments"])
    return ASRResult(text=full_text, segments=aligned["segments"], language=detected_lang)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", default=str(SAMPLE_AUDIO))
    parser.add_argument("--model", default="large-v3")  
    parser.add_argument("--language", default=None, help="ja / en / None(auto)")
    args = parser.parse_args()

    result = transcribe(args.audio, model_size=args.model, language=args.language)

    save_text(RESULTS / "01_asr_raw.txt", result.text)
    save_json(
        RESULTS / "01_asr_raw.json",
        {"language": result.language, "segments": result.segments},
    )
    print(f"[asr] saved: results/01_asr_raw.txt / .json")
    print(f"[asr] word count (aligned): {len(result.words)}")
    print("---- preview ----")
    print(result.text[:400])


if __name__ == "__main__":
    main()
