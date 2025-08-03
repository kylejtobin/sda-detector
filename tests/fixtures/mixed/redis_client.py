"""Boundary/infrastructure code - legitimate use of patterns that would be violations in domain code."""

import json
import os
from typing import Any


# ✅ Legitimate boundary patterns (infrastructure module)
class RedisClient:
    """Infrastructure code that legitimately needs boundary patterns"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._connection = None

    def connect(self) -> bool:
        """Boundary code - legitimate try/except and hasattr usage"""
        try:
            # ✅ try/except legitimate for external system boundaries
            import redis  # type: ignore

            self._connection = redis.Redis(host=self.host, port=self.port)
            self._connection.ping()
            return True
        except Exception:
            return False

    def get(self, key: str) -> str | None:
        """Boundary method with legitimate error handling"""
        if not self._connection:
            return None

        try:
            # ✅ Boundary error handling
            result = self._connection.get(key)
            return result.decode("utf-8") if result else None
        except Exception:
            return None

    def set(self, key: str, value: str) -> bool:
        """Set value with boundary error handling"""
        if not self._connection:
            return False

        try:
            return bool(self._connection.set(key, value))
        except Exception:
            return False


# ✅ File system boundary operations
class FileHandler:
    """Infrastructure code for file operations"""

    def read_config(self, config_path: str) -> dict:
        """Legitimate JSON usage for external file format"""
        try:
            if os.path.exists(config_path):
                with open(config_path) as f:
                    # ✅ Legitimate json.loads for external file format
                    return json.loads(f.read())
        except (json.JSONDecodeError, OSError):
            pass
        return {}

    def write_config(self, config_path: str, config: dict) -> bool:
        """Legitimate JSON usage for external file format"""
        try:
            with open(config_path, "w") as f:
                # ✅ Legitimate json.dumps for external file format
                json.dump(config, f, indent=2)
            return True
        except OSError:
            return False

    def check_file_attributes(self, filepath: str) -> dict:
        """Legitimate hasattr/getattr for external objects"""
        file_info = {}

        try:
            stat = os.stat(filepath)
            # ✅ Legitimate hasattr on external objects
            if hasattr(stat, "st_size"):
                file_info["size"] = stat.st_size
            if hasattr(stat, "st_mtime"):
                file_info["modified"] = stat.st_mtime
            # ✅ Legitimate getattr with default
            file_info["permissions"] = getattr(stat, "st_mode", 0)
        except OSError:
            pass

        return file_info


# ✅ API client boundary code
class ExternalApiClient:
    """Infrastructure code for external API integration"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def make_request(self, endpoint: str, data: Any = None) -> dict:
        """Boundary method with legitimate type checking"""
        try:
            import requests  # type: ignore

            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.base_url}/{endpoint}"

            # ✅ Legitimate isinstance for external data handling
            if isinstance(data, dict):
                response = requests.post(url, json=data, headers=headers)
            elif isinstance(data, str):
                response = requests.post(url, data=data, headers=headers)
            else:
                response = requests.get(url, headers=headers)

            # ✅ Legitimate JSON handling for external API
            return response.json() if response.content else {}

        except Exception:
            return {"error": "Request failed"}

    def handle_response(self, response: Any) -> dict:
        """Handle various response types from external system"""
        # ✅ Legitimate isinstance for external data
        if isinstance(response, dict):
            return response
        elif isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"message": response}
        elif isinstance(response, list):
            return {"items": response}
        else:
            return {"data": str(response)}


# ✅ Database boundary adapter
class DatabaseAdapter:
    """Infrastructure code for database operations"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection = None

    def connect(self) -> bool:
        """Database connection with boundary error handling"""
        try:
            # Mock database connection
            self._connection = {"connected": True}
            return True
        except Exception:
            return False

    def execute_query(self, query: str, params: Any = None) -> list:
        """Execute query with parameter type handling"""
        if not self._connection:
            return []

        try:
            # ✅ Legitimate isinstance for parameter handling
            if isinstance(params, dict):
                # Named parameters
                pass
            elif isinstance(params, (list, tuple)):
                # Positional parameters
                pass
            elif params is None:
                # No parameters
                pass
            else:
                # Convert to string
                params = str(params)

            # Mock query execution
            return [{"result": "mock"}]

        except Exception:
            return []


# Expected patterns:
# - Legitimate boundary_conditions (try/except for external systems)
# - Legitimate isinstance/hasattr/getattr usage (infrastructure context)
# - Legitimate JSON usage (external file formats and APIs)
# - Should be classified as MODULE TYPE: infrastructure
