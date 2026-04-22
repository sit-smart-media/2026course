"""共通ユーティリティ：パス・LLMクライアント・保存。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

SAMPLE_AUDIO = DATA / "sample.mp4"


@dataclass
class LLMConfig:
    url: str = ""
    model: str = ""
    api_key: str = ""
    temperature: float = 0.0

    @classmethod
    def from_env(cls) -> "LLMConfig":
        load_dotenv(ROOT / ".env")
        return cls(
            url=os.environ["LLM_URL"],
            model=os.environ["LLM_MODEL"],
            api_key=os.environ["LLM_API_KEY"],
        )

    def client(self) -> OpenAI:
        return OpenAI(base_url=self.url, api_key=self.api_key)


@dataclass
class ASRResult:
    text: str
    segments: list[dict] = field(default_factory=list)
    language: str = ""

    @property
    def words(self) -> list[dict]:
        out = []
        for seg in self.segments:
            for w in seg.get("words", []) or []:
                out.append(w)
        return out


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def save_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
