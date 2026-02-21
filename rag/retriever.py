#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 16:37:41 2026

@author: guotiankai
"""
from rag.loader import load_docs
from rag.store import VectorStore

_docs = load_docs()

_store = VectorStore()
_store.build(_docs)

def retrieve(query, top_k=5):
    return _store.search(query, top_k)
