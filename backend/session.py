from typing import Optional
from fastapi import HTTPException, Cookie
import uuid

def create_session_id() -> str:
    """
    Generate a new unique session ID.
    """
    return str(uuid.uuid4())

def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    """
    Retrieve session ID from cookie or raise error if invalid.
    """
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Session ID is required. Please refresh the page to start a new session."
        )
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid session ID. Please refresh the page to start a new session."
        )
    return session_id
