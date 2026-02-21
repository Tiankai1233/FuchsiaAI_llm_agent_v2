#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 20:43:30 2026

@author: guotiankai
"""
from openai import OpenAI
import numpy as np

client = OpenAI()

class VectorStore:

    def __init__(self):
        self.embeddings = []
        self.docs = []

    def embed(self, texts):
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [d.embedding for d in resp.data]

    def build(self, documents):
        self.docs = documents
        contents = [d["content"] for d in documents]
        self.embeddings = np.array(self.embed(contents))

    def search(self, query, k=5):
        q_emb = np.array(self.embed([query])[0])

        # cosine similarity
        sims = self.embeddings @ q_emb / (
            np.linalg.norm(self.embeddings, axis=1) *
            np.linalg.norm(q_emb)
        )

        top_idx = sims.argsort()[-k:][::-1]

        results = []
        for idx in top_idx:
            doc = self.docs[idx]
            doc["score"] = float(sims[idx])
            results.append(doc)

        return results
