#!/usr/bin/env python

import os
import sys
import sqlite3

# CWE で引っ掛かりそうなコードを記述

def get_user(name):
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()

    # ❌ ユーザ入力を文字列連結 → SQLインジェクションの温床
    query = f"SELECT * FROM users WHERE name = '{name}'"
    cur.execute(query)

    return cur.fetchall()
