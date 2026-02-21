#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 16:36:44 2026

@author: guotiankai
"""
import os

CHUNK_SIZE = 500
OVERLAP = 100

def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start = end - OVERLAP

    return chunks


def load_docs(folder="docs"):
    documents = []

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if not file.endswith(".txt"):
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "source": file,
                "chunk_id": i
            })

    return documents
