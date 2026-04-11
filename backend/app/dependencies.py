import chromadb
from chromadb.api.models.Collection import Collection

_chroma_client: chromadb.ClientAPI | None = None
_collection: Collection | None = None

def get_chroma_collection(persist_dir: str | None = None) -> Collection:
    global _chroma_client, _collection

    if _collection is not None and persist_dir is None:
        return _collection

    if persist_dir:
        client = chromadb.PersistentClient(path=persist_dir)
    else:
        from app.config import settings
        if _chroma_client is None:
            _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        client = _chroma_client

    collection = client.get_or_create_collection(
        name="movies_tv",
        metadata={"hnsw:space": "cosine"},
    )

    if persist_dir is None:
        _collection = collection

    return collection
