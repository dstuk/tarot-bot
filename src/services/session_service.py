"""Session management service with Redis and in-memory fallback."""
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
from src.models.user_session import UserSession, SessionState
from src.config import config


class InMemorySessionStore:
    """In-memory session storage for development."""

    def __init__(self):
        self.sessions: Dict[int, dict] = {}
        self.ttl = timedelta(hours=24)

    def get(self, user_id: int) -> Optional[dict]:
        """Get session data by user ID."""
        session_data = self.sessions.get(user_id)
        if session_data:
            # Check TTL
            updated_at = datetime.fromisoformat(session_data["updated_at"])
            if datetime.now() - updated_at > self.ttl:
                # Session expired
                del self.sessions[user_id]
                return None
        return session_data

    def set(self, user_id: int, session_data: dict) -> None:
        """Store session data."""
        self.sessions[user_id] = session_data

    def delete(self, user_id: int) -> None:
        """Delete session data."""
        if user_id in self.sessions:
            del self.sessions[user_id]

    def exists(self, user_id: int) -> bool:
        """Check if session exists."""
        return self.get(user_id) is not None


class RedisSessionStore:
    """Redis-based session storage for production."""

    def __init__(self, redis_url: str):
        try:
            import redis
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.ttl_seconds = 24 * 60 * 60  # 24 hours
        except ImportError:
            raise ImportError("redis package is required for Redis session storage")

    def _key(self, user_id: int) -> str:
        """Generate Redis key for user session."""
        return f"tarot:session:{user_id}"

    def get(self, user_id: int) -> Optional[dict]:
        """Get session data by user ID."""
        data = self.redis_client.get(self._key(user_id))
        if data:
            return json.loads(data)
        return None

    def set(self, user_id: int, session_data: dict) -> None:
        """Store session data with TTL."""
        key = self._key(user_id)
        self.redis_client.setex(key, self.ttl_seconds, json.dumps(session_data))

    def delete(self, user_id: int) -> None:
        """Delete session data."""
        self.redis_client.delete(self._key(user_id))

    def exists(self, user_id: int) -> bool:
        """Check if session exists."""
        return self.redis_client.exists(self._key(user_id)) > 0


class SessionService:
    """Service for managing user sessions."""

    def __init__(self):
        """Initialize session service with appropriate storage backend."""
        if config.use_redis:
            try:
                self.store = RedisSessionStore(config.redis_url)
            except Exception as e:
                print(f"Failed to initialize Redis, falling back to in-memory: {e}")
                self.store = InMemorySessionStore()
        else:
            self.store = InMemorySessionStore()

    def get_session(self, user_id: int) -> UserSession:
        """Get or create a user session."""
        session_data = self.store.get(user_id)
        if session_data:
            return UserSession.from_dict(session_data)
        else:
            # Create new session
            return UserSession(user_id=user_id)

    def save_session(self, session: UserSession) -> None:
        """Save user session to storage."""
        session.update()  # Update timestamp
        self.store.set(session.user_id, session.to_dict())

    def delete_session(self, user_id: int) -> None:
        """Delete a user session."""
        self.store.delete(user_id)

    def session_exists(self, user_id: int) -> bool:
        """Check if a session exists for the user."""
        return self.store.exists(user_id)

    def set_state(self, user_id: int, new_state: SessionState, language: str = None) -> None:
        """Update user session state."""
        session = self.get_session(user_id)
        session.set_state(new_state)
        if language:
            session.set_language(language)
        self.save_session(session)

    def get_state(self, user_id: int) -> SessionState:
        """Get current user state."""
        session = self.get_session(user_id)
        return session.state

    def get_language(self, user_id: int) -> str:
        """Get user's detected language."""
        session = self.get_session(user_id)
        return session.language


# Global session service instance
session_service = SessionService()
