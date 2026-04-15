"""
 uv sync
 uv run python part2.py
"""

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

import dotenv
import os

dotenv.load_dotenv()

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
llm = ChatOpenAI(model="gpt-5-nano",
                 api_key=os.getenv("LLM_API_KEY"),
                 base_url=os.getenv("LLM_URL"),
                )

agent = create_agent(llm, tools, system_prompt="あなたは親切なアシスタントです。")

# --- 実行 ---
result = agent.invoke({"messages": [("human", "12 × 34 を計算してください")]})
print("\n最終回答:", result["messages"][-1].content)