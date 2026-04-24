"""[セルフスタディ2] 精度向上ループ — CER/WER を指標にプロンプトを回す。

手順：
  1. 基準テキスト（reference）を `results/04_reference.txt` に置く。
  2. プロンプト variant を切り替え、CER（文字誤り率）と分かち書き WER を測る。
  3. CSV に記録し、改善理由をレポートする。

依存: jiwer。日本語の WER は fugashi があれば分かち書きで測る（無ければスキップ）。
  pip install jiwer
  pip install fugashi[unidic-lite]   # 任意

実行例：
  uv run python src/04_accuracy.py --variant strict
  uv run python src/04_accuracy.py --variant fewshot
  uv run python src/04_accuracy.py --all
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path

from jiwer import cer, wer

from utils import LLMConfig, RESULTS, save_text

try:
    import fugashi
    _TAGGER = fugashi.Tagger()
    def tokenize_ja(t: str) -> str:
        return " ".join(w.surface for w in _TAGGER(t))
except Exception:
    _TAGGER = None
    def tokenize_ja(t: str) -> str:
        return t


PROMPT_STRICT = """あなたは ASR 校正専門エンジンです。
新しい単語の追加は禁止。既存単語の置換・削除のみ許可。
判断不能なら原文維持。文字数を大きく変えない。出力はテキストのみ。"""

PROMPT_WITH_GLOSSARY = """あなたは ASR 校正専門エンジンです。
以下の専門用語に該当する音が出てきたら正しい綴りに直してください。

[用語リスト]
- 生成AI
- リテラシー
- ソフトウェア開発
- コンパイル
- コーディング
- WhisperX
- ASR
- LLM
- hallucination
- forced alignment

ルール：新語追加禁止、置換・削除のみ、判断不能なら原文維持。文字数を大きく変えない。出力はテキストのみ。"""

PROMPT_FEWSHOT = """あなたは ASR 校正専門エンジンです。日本語講義音声の文字起こしを校正します。

[用語リスト]
- 生成AI / リテラシー / ソフトウェア開発 / コンパイル / コーディング
- WhisperX / ASR / LLM / hallucination / forced alignment

[誤り→正例]
- 「生成A」→「生成AI」
- 「コンバイル」→「コンパイル」
- 「コーデング」→「コーディング」

ルール:
  - 新語追加禁止。置換・削除のみ。
  - 判断不能なら原文維持。
  - 文字数を大きく変えない（脱落させない）。
  - 出力はテキストのみ。説明は書かない。"""

PROMPT_REFLECT = """あなたは ASR 校正専門エンジンです。
2段階で考えてください：
  ステップ1（内部）：疑わしい箇所を列挙する
  ステップ2（出力）：最小限の置換・削除のみ適用したテキスト

ルール：新語追加禁止。文字数を大きく変えない。ステップ1は出力しない。出力はテキストのみ。"""

VARIANTS = {
    "strict": PROMPT_STRICT,
    "with_glossary": PROMPT_WITH_GLOSSARY,
    "fewshot": PROMPT_FEWSHOT,
    "reflect": PROMPT_REFLECT,
}


_PUNCT_RE = re.compile(r"[、。,.!?！？「」『』・〜ー（）\(\)\[\]【】＿_\-—:：;；]")


def normalize(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = _PUNCT_RE.sub("", t)
    t = re.sub(r"\s+", "", t)
    return t.strip()


def split_sentences(t: str) -> list[str]:
    parts = re.split(r"(?<=[。！？\n])", t)
    return [p.strip() for p in parts if p.strip()]


def correct_chunked(raw_text: str, system_prompt: str, cfg: LLMConfig, max_chars: int = 400) -> str:
    client = cfg.client()
    sentences = split_sentences(raw_text) or [raw_text]

    chunks: list[str] = []
    buf = ""
    for s in sentences:
        if len(buf) + len(s) > max_chars and buf:
            chunks.append(buf)
            buf = s
        else:
            buf += s
    if buf:
        chunks.append(buf)

    out: list[str] = []
    for ch in chunks:
        resp = client.chat.completions.create(
            model=cfg.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ch},
            ],
        )
        out.append(resp.choices[0].message.content.strip())
    return "\n".join(out)


def score_cer(reference: str, hypothesis: str) -> float:
    return cer(normalize(reference), normalize(hypothesis))


def score_wer_tokenized(reference: str, hypothesis: str) -> float:
    if _TAGGER is None:
        return float("nan")
    return wer(tokenize_ja(normalize(reference)), tokenize_ja(normalize(hypothesis)))


def length_ratio(reference: str, hypothesis: str) -> float:
    r = len(normalize(reference))
    return len(normalize(hypothesis)) / r if r else 0.0


def run_variant(variant: str, raw: str, ref: str, cfg: LLMConfig) -> dict:
    prompt = VARIANTS[variant]
    hyp = correct_chunked(raw, prompt, cfg)

    out_txt = RESULTS / f"04_corrected_{variant}.txt"
    save_text(out_txt, hyp)

    row = {
        "variant": variant,
        "cer_raw": score_cer(ref, raw),
        "cer_llm": score_cer(ref, hyp),
        "wer_raw": score_wer_tokenized(ref, raw),
        "wer_llm": score_wer_tokenized(ref, hyp),
        "len_ratio": length_ratio(ref, hyp),
    }
    row["cer_delta"] = row["cer_raw"] - row["cer_llm"]
    return row


def append_log(row: dict) -> Path:
    log_path = RESULTS / "04_wer_log.csv"
    is_new = not log_path.exists()
    fields = ["variant", "cer_raw", "cer_llm", "cer_delta", "wer_raw", "wer_llm", "len_ratio"]
    with log_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(fields)
        w.writerow([
            row["variant"],
            f"{row['cer_raw']:.4f}",
            f"{row['cer_llm']:.4f}",
            f"{row['cer_delta']:+.4f}",
            f"{row['wer_raw']:.4f}",
            f"{row['wer_llm']:.4f}",
            f"{row['len_ratio']:.3f}",
        ])
    return log_path


def print_row(row: dict) -> None:
    print(f"[score] variant={row['variant']}")
    print(f"  CER raw -> llm : {row['cer_raw']:.4f} -> {row['cer_llm']:.4f}  (delta {row['cer_delta']:+.4f}, >0=改善)")
    print(f"  WER raw -> llm : {row['wer_raw']:.4f} -> {row['wer_llm']:.4f}  (fugashi={'on' if _TAGGER else 'off'})")
    print(f"  len(hyp)/len(ref) : {row['len_ratio']:.3f}  (1.0 付近が望ましい)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default=str(RESULTS / "01_1_asr_raw.txt"))
    parser.add_argument(
        "--reference", default=str(RESULTS / "04_reference.txt"),
        help="手修正した正解テキスト",
    )
    parser.add_argument("--variant", choices=list(VARIANTS.keys()), default="strict")
    parser.add_argument("--all", action="store_true", help="全 variant を順に実行")
    args = parser.parse_args()

    ref_path = Path(args.reference)
    if not ref_path.exists():
        print(
            f"[err] reference file not found: {ref_path}\n"
            f"      まず 01 の出力を手修正したものを {ref_path} に置いてください。"
        )
        return

    raw = Path(args.raw).read_text(encoding="utf-8")
    ref = ref_path.read_text(encoding="utf-8")

    cfg = LLMConfig.from_env()
    targets = list(VARIANTS.keys()) if args.all else [args.variant]

    for v in targets:
        row = run_variant(v, raw, ref, cfg)
        log_path = append_log(row)
        print_row(row)
        print(f"  saved: 04_corrected_{v}.txt, {log_path.name}")


if __name__ == "__main__":
    main()
