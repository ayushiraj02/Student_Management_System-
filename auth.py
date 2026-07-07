import hashlib
import os
import json


class UserAuth:
    """Handles login authentication using JSON file"""

    def __init__(self, users_file):
        self.users_file = users_file
        self._ensure_users_file()

    def _ensure_users_file(self):
        """Create default admin user if file is missing or empty"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        needs_bootstrap = not os.path.exists(self.users_file)
        if not needs_bootstrap:
            try:
                with open(self.users_file, 'r') as f:
                    needs_bootstrap = not json.load(f)
            except (json.JSONDecodeError, OSError):
                needs_bootstrap = True

        if needs_bootstrap:
            default_users = {"admin": self._hash_password("admin123")}
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)

    def _hash_password(self, password):
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        """Verify username + password"""
        try:
            with open(self.users_file, 'r') as f:
                raw = f.read().strip()
                users = json.loads(raw) if raw else {}
            if username in users:
                return users[username] == self._hash_password(password)
            return False
        except Exception as e:
            print(f"Auth error: {e}")
            return False