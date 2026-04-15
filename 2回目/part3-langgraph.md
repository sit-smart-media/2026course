# Part 3：LangGraph でエージェントを作る（35〜60分）

---

## 3-1. LangChain vs LangGraph

Part 2 で使った `AgentExecutor` はシンプルなエージェント向きです。  
**LangGraph** はより複雑な「条件分岐・ループ・並列処理」が必要なエージェント向きです。

```
LangChain AgentExecutor: シンプル、すぐ動く
LangGraph:               柔軟、ループ・分岐が明示的に書ける
```

LangGraph ではエージェントを**グラフ（ノード＋エッジ）**として表現します。

```
[START] → [llm_node] → [tools_node] → [llm_node] → ... → [END]
                ↑__________________________|
                     ループ（必要な限り繰り返す）
```

---

## 3-2. LangGraph の基本概念

| 用語 | 意味 |
|------|------|
| **State** | グラフ全体で共有されるデータ（メッセージ履歴など） |
| **Node** | State を受け取り、更新して返す関数 |
| **Edge** | ノード間の接続。条件付きエッジで分岐できる |

---

## 3-3. ハンズオン：LangGraph でコーディングエージェントを作る

**`coding_agent.py`** を作成してください。

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import subprocess
import os

load_dotenv()

# --- コーディング用ツール ---

@tool
def read_file(path: str) -> str:
    """ファイルの内容を読み込む"""
    if not os.path.exists(path):
        return f"エラー: {path} が見つかりません"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@tool
def write_file(path: str, content: str) -> str:
    """ファイルに内容を書き込む"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{path} を書き込みました"

@tool
def run_python(code: str) -> str:
    """Pythonコードを実行して結果を返す"""
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        text=True,
        timeout=10,
    )
    output = result.stdout
    if result.stderr:
        output += "\nSTDERR:\n" + result.stderr
    return output or "(出力なし)"

tools = [read_file, write_file, run_python]

# --- エージェント作成（LangGraph prebuilt） ---
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools)

# --- タスクを実行 ---
task = """
以下のタスクをこなしてください：
1. fibonacci.py というファイルを作成する
2. フィボナッチ数列の最初の10個を計算する関数を書く
3. 実行して結果を確認する
"""

print("=== コーディングエージェント開始 ===\n")

for step in agent.stream(
    {"messages": [("user", task)]},
    stream_mode="values",
):
    last = step["messages"][-1]
    last.pretty_print()
```

実行：
```bash
uv run python coding_agent.py
```

---

## 3-4. グラフの構造を確認する

`create_react_agent` の内部グラフを可視化してみましょう。

```python
# coding_agent.py の末尾に追加
print("\n=== グラフ構造 ===")
print(agent.get_graph().draw_ascii())
```

出力例：
```
        +-----------+
        | __start__ |
        +-----------+
              *
              *
         +-------+
         | agent |
         +-------+
         ...  ...
    +-------+  +-----------+
    | tools |  | __end__   |
    +-------+  +-----------+
```

`agent` ノードが LLM の判断、`tools` ノードがツール実行を担当しています。

---

## チェック

1. `run_python` ツールで意図的にエラーを起こすコードを渡すと、エージェントはどう対処しますか？
2. ツールを1つ追加するとしたら何を追加しますか？理由とともに考えてください。

---

▶ 次へ：[Part 4：LangSmith でデバッグ・観察する](./part4-langsmith.md)
