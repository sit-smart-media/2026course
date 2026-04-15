"""
 uv sync
 uv run python part4.py
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
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
# LangSmith トレーシングは .env の設定で自動有効化される：
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=ls__あなたのキー
#   LANGCHAIN_PROJECT=coding-agent-lab
llm = ChatOpenAI(model="gpt-5-nano",
                 api_key=os.getenv("LLM_API_KEY"),
                 base_url=os.getenv("LLM_URL"),
                 verbose=True,  # 明示的にトレーシングを有効化
                )
agent = create_agent(llm, tools)

# --- タスクを実行（エラー回復のデモ） ---
task = """
buggy.py というファイルを作成して、以下のバグのあるコードを書いてください：
  def divide(a, b):
      return a / b

次に divide(10, 0) を実行してテストしてください。
エラーが起きたら修正してください。
"""

print("=== コーディングエージェント開始（LangSmith トレーシング有効） ===\n")

for step in agent.stream(
    {"messages": [("user", task)]},
    stream_mode="values",
):
    last = step["messages"][-1]
    last.pretty_print()
