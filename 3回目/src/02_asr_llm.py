"""[基本実践②] ASR 生ログを LLM で補正。

設計：
  - LLM は「校正専用」。新しい単語の追加を禁止。
  - 結果を results/02_asr_llm_corrected.txt に保存。
  - 修正前後の diff も results/02_diff.txt に保存。

実行：
  uv run python src/02_asr_llm.py
"""
from __future__ import annotations

import argparse
import difflib

from utils import LLMConfig, RESULTS, load_json, save_text

SYSTEM_PROMPT = """あなたは ASR（自動音声認識）後処理専門の校正エンジンです。
目的は、音声認識誤りの可能性が高い箇所のみを最小限修正することです。

[絶対ルール]
1. 新しい単語を追加してはいけません（severe, extremely 等の強調語、推測情報、要約はすべて禁止）。
2. 文の構造・話者の口調・意味が一義に確定しない語は変更しないでください。
3. 修正対象は次の場合のみ：
   - 明らかな同音異義誤り
   - 文脈的に破綻している専門用語
   - 数値と単位の不整合
4. 判断不能な場合は、**原文のまま**にしてください。
5. 出力は補正後のテキストのみ。コメントや説明は出力しない。
"""


def correct_with_llm(raw_text: str, cfg: LLMConfig) -> str:
    client = cfg.client()
    resp = client.chat.completions.create(
        model=cfg.model,
        temperature=cfg.temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"[ASR raw]\n{raw_text}\n\n[corrected]"},
        ],
    )
    return resp.choices[0].message.content.strip()


def make_diff(before: str, after: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="asr_raw",
            tofile="llm_corrected",
            lineterm="",
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default=str(RESULTS / "01_asr_raw.txt"))
    args = parser.parse_args()

    with open(args.raw, encoding="utf-8") as f:
        raw_text = f.read()

    cfg = LLMConfig.from_env()
    print(f"[llm] model={cfg.model}")
    corrected = correct_with_llm(raw_text, cfg)

    save_text(RESULTS / "02_asr_llm_corrected.txt", corrected)

    diff = make_diff(raw_text, corrected)
    save_text(RESULTS / "02_diff.txt", diff)

    print("[llm] saved: results/02_asr_llm_corrected.txt / 02_diff.txt")
    print("---- diff preview ----")
    print("\n".join(diff.splitlines()[:40]))


if __name__ == "__main__":
    main()
