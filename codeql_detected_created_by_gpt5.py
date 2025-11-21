# bad_sample.py
import sqlite3
import subprocess
import pickle
import yaml
from flask import Flask, request, send_file

app = Flask(__name__)

# -------------------------------------------------------
# 1) SQL Injection
# -------------------------------------------------------
@app.route("/sql")
def sql_injection():
    q = request.args.get("q", "")
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    # ユーザ入力を直接クエリへ → 高確率で CodeQL が検出
    sql = "SELECT * FROM users WHERE name = '%s'" % q
    cur.execute(sql)
    return {"ok": True}

# -------------------------------------------------------
# 2) Command Injection (shell=True)
# -------------------------------------------------------
@app.route("/cmd")
def cmd_injection():
    host = request.args.get("host", "")
    # shell=True + ユーザ入力 → 高危険度
    cmd = f"ping -c 1 {host}"
    subprocess.check_output(cmd, shell=True)
    return {"cmd": "executed"}

# -------------------------------------------------------
# 3) eval() で任意コード実行
# -------------------------------------------------------
@app.route("/eval")
def eval_injection():
    expr = request.args.get("expr", "")
    # 外部入力を eval() に渡す → CRITICAL
    result = eval(expr)
    return {"result": result}

# -------------------------------------------------------
# 4) pickle.loads() に外部入力
# -------------------------------------------------------
@app.route("/pickle", methods=["POST"])
def pickle_load():
    data = request.get_data()
    # 任意コードが実行される危険なデシリアライズ
    obj = pickle.loads(data)
    return {"loaded_type": str(type(obj))}

# -------------------------------------------------------
# 5) Path Traversal
# -------------------------------------------------------
@app.route("/file")
def file_read():
    filename = request.args.get("file", "")
    # ユーザが "../../etc/passwd" を指定可能
    return send_file(filename)

# -------------------------------------------------------
# 6) unsafe YAML load
# -------------------------------------------------------
@app.route("/yaml", methods=["POST"])
def yaml_unsafe():
    data = request.data
    # yaml.safe_load でない → 任意オブジェクト生成の危険
    obj = yaml.load(data)
    return {"yaml": str(obj)}

# -------------------------------------------------------
# 7) ハードコードされた秘密情報
# -------------------------------------------------------
API_KEY = "hardcoded_super_secret_value_12345"

@app.route("/secret")
def secret():
    return {"api_key": API_KEY}

# -------------------------------------------------------
# Flask 起動（評価テスト用）
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)

