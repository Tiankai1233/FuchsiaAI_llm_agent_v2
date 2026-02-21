#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 19:54:58 2026

@author: guotiankai
"""
import sqlite3
from threading import Lock

DB_PATH = "agent.db"
_lock = Lock()
_conn = None


def get_db():

    global _conn

    with _lock:
        if _conn is None:
            _conn = sqlite3.connect(
                DB_PATH,
                check_same_thread=False,
                timeout=30
            )

            _conn.row_factory = sqlite3.Row
            _conn.execute("PRAGMA journal_mode=WAL;")

        return _conn


def init_db():

    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        id TEXT PRIMARY KEY,
        title TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        meta TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    db.commit()

