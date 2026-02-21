#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 20:43:30 2026

@author: guotiankai
"""
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorStore:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.docs = []

    def build(self, documents):
        self.docs = documents

        embeddings = self.model.encode(
            [d["content"] for d in documents],
            show_progress_bar=True
        )

        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)

    def search(self, query, k=5):
        q = self.model.encode([query]).astype("float32")
        faiss.normalize_L2(q)
    
        scores, ids = self.index.search(q, k)
    
        results = []
        for score, idx in zip(scores[0], ids[0]):
            doc = self.docs[idx]
            doc["score"] = float(score)
            results.append(doc)
    
        return results