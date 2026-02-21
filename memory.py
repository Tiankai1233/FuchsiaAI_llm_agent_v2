#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 20:27:36 2026

@author: guotiankai
"""
import json
from db import get_db
from llm.client import chat


class Memory:

    def __init__(self, session_id, system_prompt):

        self.session_id = session_id
        self.db = get_db()

        # session
        self.db.execute("""
        INSERT OR IGNORE INTO sessions(id,title)
        VALUES (?,?)
        """, (session_id, None))

        # system once
        r = self.db.execute("""
        SELECT count(*) FROM messages
        WHERE session_id=? AND role='system'
        """, (session_id,)).fetchone()[0]

        if r == 0:
            self.add("system", system_prompt)

        self.db.commit()

    def add(self, role, content, meta=None):

        self.db.execute("""
        INSERT INTO messages(session_id,role,content,meta)
        VALUES (?,?,?,?)
        """, (
            self.session_id,
            role,
            content,
            json.dumps(meta or {}, ensure_ascii=False)
        ))

        self.db.commit()

    def history(self):

        rows = self.db.execute("""
        SELECT role,content FROM messages
        WHERE session_id=?
        ORDER BY id
        """, (self.session_id,)).fetchall()

        return [{"role": r["role"], "content": r["content"]} for r in rows]

    # 自动生成 title
    def maybe_title(self):

        row = self.db.execute(
            "SELECT title FROM sessions WHERE id=?",
            (self.session_id,)
        ).fetchone()

        if row["title"]:
            return

        first = self.db.execute("""
        SELECT content FROM messages
        WHERE session_id=? AND role='user'
        ORDER BY id LIMIT 1
        """, (self.session_id,)).fetchone()

        if not first:
            return

        prompt = [
            {"role": "system", "content": "生成5字左右中文标题"},
            {"role": "user", "content": first["content"]}
        ]

        title = chat(prompt).strip()

        self.db.execute(
            "UPDATE sessions SET title=? WHERE id=?",
            (title, self.session_id)
        )

        self.db.commit()
