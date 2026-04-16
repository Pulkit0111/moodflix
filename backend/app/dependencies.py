import base64
import json
import chromadb
from chromadb.api.models.Collection import Collection
from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth
import firebase_admin

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
            if settings.chroma_api_key:
                _chroma_client = chromadb.CloudClient(
                    api_key=settings.chroma_api_key,
                    tenant=settings.chroma_tenant,
                    database=settings.chroma_database,
                )
            else:
                _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        client = _chroma_client

    collection = client.get_or_create_collection(
        name="movies_tv",
        metadata={"hnsw:space": "cosine"},
    )

    if persist_dir is None:
        _collection = collection

    return collection


_firebase_initialized = False

def init_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        from app.config import settings
        if settings.firebase_service_account_json:
            service_account_dict = json.loads(base64.b64decode(settings.firebase_service_account_json))
            cred = firebase_admin.credentials.Certificate(service_account_dict)
        else:
            cred = firebase_admin.credentials.Certificate(settings.firebase_service_account_path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True

async def verify_firebase_token(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split("Bearer ")[1]
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
