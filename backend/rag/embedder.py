from sentence_transformers import SentenceTransformer
import functools

@functools.lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    model = get_model()
    embeddings = model.encode(chunks)

    return embeddings
