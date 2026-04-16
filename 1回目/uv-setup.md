# uv ツールのインストールと利用方法

> 対象：プログラミング初心者（大学2〜3年生）  
> 前提：GitHub Desktopのインストールが完了していること

---

## uvとは

**uv** は、Pythonのパッケージ管理・プロジェクト管理を行う高速ツールです。従来の `pip` や `venv` の代わりに使えます。

| 従来のツール | uvでの代替 | メリット |
|-------------|-----------|---------|
| `pip install` | `uv pip install` | 10〜100倍高速 |
| `python -m venv` | `uv venv` | 自動で仮想環境を管理 |
| `pip` + `venv` + `pyenv` | `uv` 1つ | ツールが1つで済む |

---

## 1. uvのインストール

### Windows

PowerShellを**管理者として実行**し、以下のコマンドを入力：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

インストール後、ターミナルを**再起動**してください。

### macOS / Linux

ターミナルで以下を実行：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### インストールの確認

```bash
uv --version
```

バージョン番号が表示されればOKです（例：`uv 0.7.x`）。

---

## 2. Pythonのインストール（uvを使用）

uvを使うと、Python自体のインストールも簡単にできます。

```bash
uv python install
```

これで最新の安定版Pythonがインストールされます。

特定のバージョンを指定する場合：

```bash
uv python install 3.12
```

インストール済みのPythonを確認：

```bash
uv python list
```

---

## 3. プロジェクトの作成

### 新しいプロジェクトを作成

```bash
uv init my-project
cd my-project
```

以下のファイルが自動生成されます：

```
my-project/
├── pyproject.toml    ← プロジェクトの設定ファイル
├── README.md
└── main.py          ← サンプルスクリプト
```

### 既存のフォルダでプロジェクトを初期化

```bash
cd 既存のフォルダ
uv init
```

---

## 4. パッケージの管理

### パッケージの追加

```bash
uv add requests
```

これだけで：
- パッケージがダウンロードされる
- `pyproject.toml` に依存関係が記録される
- `uv.lock` にバージョンが固定される

### 複数パッケージの追加

```bash
uv add numpy pandas matplotlib
```

### パッケージの削除

```bash
uv remove requests
```

### インストール済みパッケージの確認

```bash
uv pip list
```

---

## 5. スクリプトの実行

### uv run でスクリプトを実行

```bash
uv run hello.py
```

`uv run` を使うと、仮想環境の作成とパッケージのインストールを**自動的に行ってから**スクリプトを実行します。`python hello.py` の代わりに `uv run hello.py` を使いましょう。

### 例：簡単なスクリプトを動かす

1. `hello.py` を以下の内容に編集：

```python
import requests

response = requests.get("https://api.github.com")
print(f"GitHub API Status: {response.status_code}")
print(f"Rate Limit: {response.headers['X-RateLimit-Limit']}")
```

2. 依存パッケージを追加して実行：

```bash
uv add requests
uv run hello.py
```

---

## 6. よく使うコマンドまとめ

| コマンド | 説明 |
|---------|------|
| `uv init` | 新しいプロジェクトを作成 |
| `uv add パッケージ名` | パッケージを追加 |
| `uv remove パッケージ名` | パッケージを削除 |
| `uv run ファイル名.py` | スクリプトを実行 |
| `uv python install` | Pythonをインストール |
| `uv python list` | インストール済みPythonの一覧 |
| `uv sync` | `pyproject.toml` に基づいて環境を同期 |
| `uv lock` | 依存関係のロックファイルを更新 |

---

## 7. トラブルシューティング

### `uv: command not found` と表示される

- ターミナルを再起動してください
- Windows：新しいPowerShellウィンドウを開く
- macOS/Linux：`source ~/.bashrc` または `source ~/.zshrc` を実行

### パッケージのインストールが失敗する

```bash
uv cache clean
uv add パッケージ名
```

キャッシュをクリアしてから再度インストールしてみてください。

---

## 参考リンク

- [uv公式ドキュメント](https://docs.astral.sh/uv/)
- [uv GitHub リポジトリ](https://github.com/astral-sh/uv)
