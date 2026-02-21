#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 17:06:07 2026

@author: guotiankai
"""
import json
import os

DATA_FILE = "data/chats.json"


class Memory:
    def __init__(self, session_id, system_prompt):
        self.session_id = session_id
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        self.load()

    def add_user(self, text):
        self.messages.append({"role": "user", "content": text})
        self.save()

    def add_assistant(self, text):
        self.messages.append({"role": "assistant", "content": text})
        self.save()

    def get(self):
        return self.messages

    # 🔹 保存到文件
    def save(self):
        os.makedirs("data", exist_ok=True)

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        else:
            all_data = {}

        all_data[self.session_id] = self.messages

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

    # 🔹 加载历史
    def load(self):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)

        if self.session_id in all_data:
            self.messages = all_data[self.session_id]