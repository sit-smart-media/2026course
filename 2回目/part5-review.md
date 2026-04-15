# 振り返りと課題（80〜90分）

---

## 今日学んだこと

| 項目 | 内容 |
|------|------|
| エージェントの仕組み | LLM ＋ ツール ＋ ReAct ループ |
| ツールの定義 | `@tool` デコレーター、docstring が LLM への説明になる |
| LangGraph | グラフ構造でエージェントの動きを制御する |
| LangSmith | トレーシングでエージェントの内部動作を可視化する |

---

## 今日の課題（提出：次回授業まで）

以下のいずれか **1つ** に取り組み、GitHub リポジトリにプッシュしてください。

### レベル1（基本）
`coding_agent.py` を改造して、新しいツールを1つ以上追加してください。  
例：
- `list_files(directory)` — フォルダ内のファイル一覧を返す
- `search_in_file(path, keyword)` — ファイル内でキーワードを検索する

### レベル2（応用）
エージェントに「簡単な Python クイズを出して、答えを実行して確認する」タスクをやらせてください。  
LangSmith のスクリーンショットと共にどんなトレースになったか説明してください。

### レベル3（発展）
LangGraph で**自分でグラフを定義**し、「コード生成→テスト実行→失敗したら修正」という 3 ノードのエージェントを作ってください。  
参考：https://langchain-ai.github.io/langgraph/tutorials/introduction/

---

## 提出方法

1. GitHub の自分のリポジトリに `week02/` フォルダを作成
2. 作成したコードと `README.md`（何をしたか説明）をプッシュ
3. GitHub Copilot のコメント提案も活用してみてください

---

## 参考リソース

- LangGraph 公式チュートリアル：https://langchain-ai.github.io/langgraph/tutorials/introduction/
- LangSmith 公式ドキュメント：https://docs.smith.langchain.com/
- DeepLearning.AI エージェントコース：https://learn.deeplearning.ai/courses/agentic-ai/lesson/pu5xbv/welcome!
- エージェントデザインパターン（日本語）：https://github.com/sit-xinli/AgentDesignPatterns

---

## 進捗・課題の自己評価（5段階）

授業後に以下を記録してください。

| 評価項目 | 1〜5 |
|----------|------|
| エージェントの仕組みを説明できる | /5 |
| ツールを自分で定義して動かせた | /5 |
| LangSmith でトレースを確認できた | /5 |
