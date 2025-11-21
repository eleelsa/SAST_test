#!/usr/bin/env python

import os
import sys
import sqlite3
import random
import pickle

############################################################
# 処理フローにのらない、CWE で引っ掛かりそうなコードを記述 #
############################################################

# ❌ これは絶対にNG
API_KEY = "SECRET-KEY-1234567890"
PASSWORD = "P@ssw0rd"

def get_user(name):
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()

    # ❌ ユーザ入力を文字列連結 → SQLインジェクションの温床
    query = f"SELECT * FROM users WHERE name = '{name}'"
    cur.execute(query)

    return cur.fetchall()

def run_ping(target):
    # ❌ ユーザ入力をシェルコマンドに直接使用
    os.system(f"ping -c 1 {target}")

def generate_token():
    # ❌ random はセキュリティ用途に不適（予測される）
    return str(random.randint(100000, 999999))

def read_file(filename):
    # ❌ ユーザ入力パスをそのまま join すると危険
    base = "/var/app/data/"
    path = os.path.join(base, filename)
    
    with open(path, "r") as f:
        return f.read()

def load_user_data(blob):
    # ❌ 攻撃者入力で任意コード実行を誘発しうる
    return pickle.loads(blob)
