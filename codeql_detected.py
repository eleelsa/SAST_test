#!/usr/bin/env python3

import subprocess
import sqlite3
import yaml
import pickle


#######################################
# ① コマンドインジェクション（確実に検出）
#######################################
def dangerous_command(user_input):
    # subprocess で user_input をそのまま渡す → OS コマンドインジェクション
    subprocess.run("ls " + user_input, shell=True)


#######################################
# ② SQLインジェクション（確実に検出）
#######################################
def dangerous_sql(name):
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()

    # 文字列連結 → 非パラメータ化 SQL → SQL Injection
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    cur.execute(query)

    return cur.fetchall()


#######################################
# ③ YAML 任意コード実行（確実に検出）
#######################################
def dangerous_yaml(user_input):
    # yaml.load は攻撃者入力で任意コード実行の危険あり
    return yaml.load(user_input, Loader=yaml.Loader)


#######################################
# ④ pickle 任意コード実行（確実に検出）
#######################################
def dangerous_pickle(blob):
    # pickle.loads は攻撃者データで任意コード実行可能
    return pickle.loads(blob)


# dangerous_command("example.txt")
# dangerous_sql("test_user")