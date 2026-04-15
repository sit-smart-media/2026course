# Part 4：LangSmith でデバッグ・観察する（60〜80分）

---

## 4-1. LangSmith とは

エージェントが複数のツールを呼びながら動くとき、**何が起きているか追いづらい**問題があります。

**LangSmith** は LangChain/LangGraph のための**トレーシング・デバッグツール**です。

- エージェントの各ステップを可視化
- LLM へ送ったプロンプトと返ってきた回答を確認
- どのツールが何回呼ばれたか確認
- 実行時間・トークン数の計測

---

## 4-2. LangSmith のセットアップ

**ステップ1：アカウント作成**

1. https://smith.langchain.com にアクセス
2. 「Sign Up」でアカウントを作成（GitHub アカウントが使えます）
3. 左メニュー「Settings」→「API Keys」→「Create API Key」

**ステップ2：`.env` に追記**

```
OPENAI_API_KEY=...（既存）

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__あなたのキー
LANGCHAIN_PROJECT=coding-agent-lab
```

**この設定をするだけでトレーシングが自動で有効になります。**  
コードの変更は不要です。

---

## 4-3. トレースを見てみよう

Part 3 の `coding_agent.py` をそのまま再実行してください：

```bash
uv run python coding_agent.py
```

実行後、https://smith.langchain.com を開くと：

```
Projects
└── coding-agent-lab
    └── Run: [タイムスタンプ]
        ├── LLMCall（最初の推論）
        │   ├── Input: ユーザーのタスク
        │   └── Output: run_python を呼ぶ指示
        ├── ToolCall: run_python
        │   └── Output: 実行結果
        ├── LLMCall（次の推論）
        └── ...
```

---

## 4-4. LangSmith で確認すべきポイント

### プロンプトの確認
「LLM に何を送ったか」が確認できます。  
ツールの docstring がそのままプロンプトに埋め込まれていることがわかります。

### エラーのデバッグ
ツールがエラーを返したとき、LLM がどう回復しようとしたか追えます。

### トークン使用量
各ステップで何トークン使ったかが見えます。  
コストを見積もるときに役立ちます。

---

## 4-5. ハンズオン：意図的にエラーを起こしてトレースを見る

`coding_agent.py` のタスクを以下に変えて実行してください：

```python
task = """
buggy.py というファイルを作成して、以下のバグのあるコードを書いてください：
  def divide(a, b):
      return a / b

次に divide(10, 0) を実行してテストしてください。
エラーが起きたら修正してください。
"""
```

LangSmith でエラーの発生 → 回復の過程を確認してみましょう。

---

## チェック

1. LangSmith でトレースが表示されましたか？
2. 最も多くトークンを使ったステップはどれでしたか？
3. エラーが起きたとき、エージェントは何回試行しましたか？

---

▶ 次へ：[振り返りと課題](./part5-review.md)
