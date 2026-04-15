# Part 2：エージェントはどうやってツールを使うか（15〜35分）

---

## 2-1. ツールとは

エージェントにおける「ツール」とは、**LLM が呼び出せる関数**のことです。

LLM 自体はテキストを生成するだけですが、ツールを介して**外の世界に作用**できます。

| ツールの例 | できること |
|-----------|-----------|
| `read_file` | ファイルの内容を読む |
| `write_file` | ファイルを書き込む |
| `run_bash` | シェルコマンドを実行する |
| `search_web` | Web を検索する |
| `run_python` | Python コードを実行する |

---

## 2-2. ツールの定義方法（LangChain）

LangChain では `@tool` デコレーターでツールを定義します。

```python
from langchain_core.tools import tool

@tool
def add_numbers(a: int, b: int) -> int:
    """2つの整数を足し算する"""
    return a + b

@tool
def read_file(path: str) -> str:
    """指定したパスのファイルを読み込む"""
    with open(path, "r") as f:
        return f.read()
```

**ポイント：** docstring がそのままエージェントへの説明になります。  
「このツールは何をするのか」を LLM が理解するために使われます。

---

## 2-3. LLM がツールを選ぶ仕組み

LLM はツールの一覧と説明を受け取り、**どのツールを呼ぶか JSON で返します**。

```
LLM への入力:
  - ユーザーの指示
  - 利用可能なツールの一覧（名前＋説明）

LLM の出力（Function Calling）:
{
  "tool": "read_file",
  "arguments": {"path": "calc.py"}
}
```

この仕組みは OpenAI / Anthropic / Google など主要な LLM が対応しています。

---

## 2-4. ハンズオン：最初のエージェントを動かす

`agent-lab` フォルダに移動し、以下のファイルを作成してください。

**`.env`**
```
OPENAI_API_KEY=先生から配布されたキー
```

**`simple_agent.py`**
```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- ツールを定義 ---
@tool
def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算する"""
    return a * b

@tool
def get_word_count(text: str) -> int:
    """テキストの単語数を数える"""
    return len(text.split())

tools = [multiply, get_word_count]

# --- エージェントを作成 ---
llm = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは親切なアシスタントです。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- 実行 ---
result = executor.invoke({"input": "12 × 34 を計算してください"})
print("\n最終回答:", result["output"])
```

実行してみましょう：
```bash
uv run python simple_agent.py
```

`verbose=True` にすると、エージェントがどのツールを呼んだか確認できます。

---

## チェック

1. `@tool` の docstring を変えると何が変わりますか？
2. `verbose=True` を外すとどうなりますか？試してみてください。

---

▶ 次へ：[Part 3：LangGraph でエージェントを作る](./part3-langgraph.md)
