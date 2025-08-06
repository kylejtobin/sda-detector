"""Test fixture for Any type usage violations.

This module demonstrates usage of Any type that violates SDA principles.
Any type usage indicates failure to properly model domain types.
"""

from typing import Any, Optional


def process_data(data: Any) -> Any:
    """VIOLATION: Any in both parameter and return type."""
    # ❌ BAD: No type safety at all
    if isinstance(data, dict):  # Also an isinstance violation!
        return data.get("value")  # Returns Any
    return str(data)  # Type unclear


class DataStore:
    """VIOLATION: Using Any for storage instead of proper types."""
    
    def __init__(self):
        # ❌ BAD: Any type for values
        self._cache: dict[str, Any] = {}  # Any violation!
    
    def get(self, key: str) -> Any:
        """VIOLATION: Returns Any instead of specific type."""
        # ❌ BAD: No type information for callers
        return self._cache.get(key)  # Returns Any!
    
    def set(self, key: str, value: Any) -> None:
        """VIOLATION: Accepts Any instead of typed values."""
        # ❌ BAD: No validation or type checking
        self._cache[key] = value  # Stores Any!


def transform_list(items: list[Any]) -> list[str]:
    """VIOLATION: Any in generic types."""
    # ❌ BAD: List of Any provides no safety
    result = []
    for item in items:  # item is Any
        # Dangerous - no guarantee item can be stringified
        result.append(str(item))
    return result


def api_handler(request: dict[str, Any]) -> dict[str, Any]:
    """VIOLATION: Any in nested structures."""
    # ❌ BAD: Dictionary values are Any
    response: dict[str, Any] = {}  # Any violation!
    
    # No type safety for request data
    user_id = request.get("user_id")  # user_id is Any
    action = request.get("action")  # action is Any
    
    response["status"] = "ok"
    response["data"] = {"user": user_id, "action": action}  # All Any!
    
    return response


# ============================================================================
# SDA-COMPLIANT ALTERNATIVES
# ============================================================================

from pydantic import BaseModel
from enum import StrEnum


class DataType(StrEnum):
    """✅ GOOD: Explicit data types."""
    STRING = "string"
    NUMBER = "number"
    OBJECT = "object"


class TypedData(BaseModel):
    """✅ GOOD: Explicit domain model instead of Any."""
    data_type: DataType
    value: str | int | dict
    
    def process(self) -> str:
        """Domain method with type safety."""
        processors = {
            DataType.STRING: lambda v: str(v),
            DataType.NUMBER: lambda v: f"Number: {v}",
            DataType.OBJECT: lambda v: f"Object with {len(v)} keys" if isinstance(v, dict) else "Object",
        }
        return processors[self.data_type](self.value)


class TypedDataStore(BaseModel):
    """✅ GOOD: Typed storage with explicit domain models."""
    _cache: dict[str, TypedData] = {}
    
    def get(self, key: str) -> Optional[TypedData]:
        """Returns typed domain model."""
        return self._cache.get(key)
    
    def set(self, key: str, value: TypedData) -> None:
        """Accepts only typed values."""
        self._cache[key] = value


class ApiRequest(BaseModel):
    """✅ GOOD: Explicit request model."""
    user_id: int
    action: str
    data: dict[str, str]


class ApiResponse(BaseModel):
    """✅ GOOD: Explicit response model."""
    status: str
    data: dict[str, str | int]


def api_handler_sda(request: ApiRequest) -> ApiResponse:
    """✅ GOOD: Fully typed API handler."""
    # Type-safe access to request fields
    return ApiResponse(
        status="ok",
        data={"user": request.user_id, "action": request.action}
    )


# The SDA way: Every piece of data has a type
# No Any types - model your domain explicitly
# Use discriminated unions for variant types