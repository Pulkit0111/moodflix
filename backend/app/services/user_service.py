from datetime import datetime, timezone

class UserService:
    def __init__(self, db):
        self.db = db

    def _users_ref(self, uid: str):
        return self.db.collection("users").document(uid)

    def get_or_create_profile(self, uid: str, name: str | None, email: str | None, avatar_url: str | None) -> dict:
        doc_ref = self._users_ref(uid)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        profile = {
            "name": name, "email": email, "avatar_url": avatar_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        doc_ref.set(profile)
        return profile

    def get_watchlist(self, uid: str) -> list[dict]:
        docs = self._users_ref(uid).collection("watchlist").order_by("added_at").stream()
        return [doc.to_dict() for doc in docs]

    def add_to_watchlist(self, uid: str, tmdb_id: int, media_type: str, title: str, poster_path: str | None):
        self._users_ref(uid).collection("watchlist").document(str(tmdb_id)).set({
            "tmdb_id": tmdb_id, "media_type": media_type, "title": title,
            "poster_path": poster_path, "added_at": datetime.now(timezone.utc).isoformat(),
        })

    def remove_from_watchlist(self, uid: str, tmdb_id: int):
        self._users_ref(uid).collection("watchlist").document(str(tmdb_id)).delete()

    def get_history(self, uid: str) -> list[dict]:
        docs = self._users_ref(uid).collection("watch_history").order_by("watched_at").stream()
        return [doc.to_dict() for doc in docs]

    def add_to_history(self, uid: str, tmdb_id: int, media_type: str, title: str, poster_path: str | None = None, rating: float | None = None):
        self._users_ref(uid).collection("watch_history").document(str(tmdb_id)).set({
            "tmdb_id": tmdb_id, "media_type": media_type, "title": title,
            "poster_path": poster_path, "watched_at": datetime.now(timezone.utc).isoformat(), "rating": rating,
        })

    def get_preferences(self, uid: str) -> dict:
        doc = self._users_ref(uid).get()
        if doc.exists:
            data = doc.to_dict()
            return {
                "favorite_genres": data.get("favorite_genres", []),
                "disliked_genres": data.get("disliked_genres", []),
                "preferred_decades": data.get("preferred_decades", []),
            }
        return {"favorite_genres": [], "disliked_genres": [], "preferred_decades": []}

    def update_preferences(self, uid: str, favorite_genres: list[str], disliked_genres: list[str], preferred_decades: list[str]):
        self._users_ref(uid).set(
            {"favorite_genres": favorite_genres, "disliked_genres": disliked_genres, "preferred_decades": preferred_decades},
            merge=True,
        )

    def get_search_history(self, uid: str, limit: int = 50) -> list[dict]:
        docs = self._users_ref(uid).collection("search_history").order_by("searched_at").limit(limit).stream()
        return [doc.to_dict() for doc in docs]

    def add_search_query(self, uid: str, query: str):
        self._users_ref(uid).collection("search_history").add({
            "query": query, "searched_at": datetime.now(timezone.utc).isoformat(),
        })
