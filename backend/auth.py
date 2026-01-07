import os
import json
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# User storage directory
USERS_DIR = Path("data/users")
USERS_DIR.mkdir(parents=True, exist_ok=True)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, pwd_hash = hashed.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False

def create_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user account."""
    # Check if user already exists
    if get_user_by_email(email):
        raise ValueError("User with this email already exists")
    
    # Generate user ID
    user_id = secrets.token_hex(16)
    
    # Create user data
    user_data = {
        "id": user_id,
        "name": name,
        "email": email.lower(),
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    # Save user to file
    user_file = USERS_DIR / f"{user_id}.json"
    with open(user_file, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    return {
        "id": user_id,
        "name": name,
        "email": email.lower()
    }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    email = email.lower()
    for user_file in USERS_DIR.glob("*.json"):
        try:
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                if user_data.get("email") == email:
                    return user_data
        except:
            continue
    return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    user_file = USERS_DIR / f"{user_id}.json"
    if user_file.exists():
        try:
            with open(user_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with email and password."""
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["password"]):
        return None
    
    # Update last login
    user["last_login"] = datetime.now().isoformat()
    user_file = USERS_DIR / f"{user['id']}.json"
    with open(user_file, 'w') as f:
        json.dump(user, f, indent=2)
    
    # Return user data without password
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }

def update_user_session(user_id: str) -> None:
    """Update user's last login timestamp."""
    user = get_user_by_id(user_id)
    if user:
        user["last_login"] = datetime.now().isoformat()
        user_file = USERS_DIR / f"{user_id}.json"
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
