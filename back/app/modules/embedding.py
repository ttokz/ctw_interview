# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("BAAI/bge-m3")

# def bge_embedder(sentences: list[str]):
#     embeddings = model.encode(sentences)
#     return embeddings

import numpy as np

def random_emb(sentences: list[str]):
    return np.random.random_sample(size = (len(sentences), 100))
