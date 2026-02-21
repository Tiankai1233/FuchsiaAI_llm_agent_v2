#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 20:45:04 2026

@author: guotiankai
"""
from rag.retriever import retrieve

MIN_SCORE = 0.45

def rag(query):
    docs = retrieve(query, top_k=3)

    if not docs:
        return None, 0

    top_score = docs[0]["score"]

    if top_score < MIN_SCORE:
        print("RAG MISS — fallback")
        return None, top_score

    blocks = []

    for d in docs:
        blocks.append(
            f"SOURCE: {d['source']} (score {round(d['score'],2)})\n{d['content']}"
        )

    context = "\n\n".join(blocks)

    return context, top_score
