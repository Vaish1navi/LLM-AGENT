import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    # Allow the server to start even if embeddings are not usable yet.
    # Actual indexing/querying will fail with a clear error when called.
    GOOGLE_API_KEY = None

genai.configure(api_key=GOOGLE_API_KEY)
EMBEDDING_MODEL_NAME = "models/embedding-001"

# Vercel mounts `/var/task` as read-only. Chroma needs a writable directory.
# Use an env override if provided; otherwise fall back to /tmp.
CHROMA_PATH = os.environ.get("CHROMA_PATH") or os.environ.get("TMPDIR") or "/tmp/chroma_db"

_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    # Lazy-init so app startup won’t fail if embeddings are not usable yet.
    _client = chromadb.PersistentClient(path=CHROMA_PATH)
    _collection = _client.get_or_create_collection(name="hackrx_local_google_v1")
    return _collection

def get_embeddings(texts: list[str], task_type="retrieval_document") -> list[list[float]]:
    if not texts or not all(isinstance(t, str) and t for t in texts):
        return []
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=texts,
            task_type=task_type
        )
        return result['embedding']
    except Exception as e:
        print(f"An error occurred during Google embedding: {e}")
        return [[] for _ in texts]
def index_chunks(chunks: list[str], namespace: str):
    collection = _get_collection()
    print(f"[LOCAL DB] Indexing {len(chunks)} chunks using Google embeddings...")
    embeddings = get_embeddings(chunks)

    if not any(embeddings):
        print("[LOCAL DB] ERROR: Could not generate any embeddings. Skipping indexing.")
        return
    ids = [str(i) for i in range(len(chunks))]
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=ids
    )
    print("[LOCAL DB] Indexing complete.")
def query_chunks(query: str, namespace: str, top_k: int = 3) -> list:
    collection = _get_collection()
    print(f"[LOCAL DB] Querying for: '{query[:40]}...' using Google embeddings.")
    query_embedding = get_embeddings([query], task_type="retrieval_query")

    if not query_embedding:
        return []
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results['documents'][0]
def check_if_indexed(namespace: str) -> bool:
    count = collection.count()
    is_indexed = count > 0
    print(f"[LOCAL DB] Checking if indexed... Found {count} items. Indexed: {is_indexed}")
    return is_indexed