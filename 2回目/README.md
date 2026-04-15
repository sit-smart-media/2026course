# 2回目：コーディングエージェントの基礎

**所要時間：90分**  
**形式：セルフスタディ + ハンズオン**

---

## 学習目標

この授業が終わるころには、以下のことができるようになります。

- コーディングエージェントがツールを使って問題を解決する仕組みを説明できる
- LangGraph と LangSmith を使って簡単なコーディングエージェントを自分で構築できる

---

## タイムライン

| 時間 | 内容 |
|------|------|
| 0〜15分 | [Part 1：エージェントとは何か？](./part1-agent-intro.md) |
| 15〜35分 | [Part 2：エージェントはどうやってツールを使うか](./part2-tools.md) |
| 35〜60分 | [Part 3：LangGraph でエージェントを作る](./part3-langgraph.md) |
| 60〜80分 | [Part 4：LangSmith でデバッグ・観察する](./part4-langsmith.md) |
| 80〜90分 | [振り返りと課題](./part5-review.md) |

---

## 事前準備

以下をインストール・設定しておいてください（前回の uv セットアップが済んでいること）。

```bash
uv init agent-lab
cd agent-lab
uv add langchain langgraph langsmith langchain-openai python-dotenv
```

OpenAI API キーまたは Anthropic API キーも必要です。先生から配布されたキーを使ってください。
