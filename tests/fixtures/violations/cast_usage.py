"""Type casting violations - should use constructive transformation."""

from typing import Any, cast


# ❌ cast() violations (detected)
def force_string_type(data: Any) -> str:
    """Using cast to assert type instead of constructive transformation."""
    return cast(str, data)  # SDA violation - assertive not constructive


def process_response(response: dict) -> "User":
    """Casting dict to User without construction."""
    from models import User

    return cast(User, response)  # Should construct User.from_dict(response)


class DataProcessor:
    def get_typed_value(self, key: str) -> int:
        """Casting instead of proper type conversion."""
        value = self.data.get(key)
        return cast(int, value)  # Should validate and convert


# ❌ Multiple cast violations in one function
def transform_data(raw_data: list[Any]) -> list[str]:
    """Heavy use of cast instead of validation."""
    result = []
    for item in raw_data:
        # Should validate each item
        string_item = cast(str, item)
        result.append(string_item)
    return result


# ❌ Nested cast operations
def extract_nested_value(data: dict) -> float:
    """Casting at multiple levels."""
    nested = cast(dict, data.get("nested"))
    value = cast(float, nested.get("value"))
    return value


# ✅ SDA Alternative - Constructive Transformation
from pydantic import BaseModel


class User(BaseModel):
    """Domain model with constructive transformation."""

    name: str
    age: int

    @classmethod
    def from_raw(cls, data: dict) -> "User":
        """Constructive transformation - build don't assert."""
        return cls(name=data.get("name", ""), age=int(data.get("age", 0)))


def transform_constructively(raw: Any) -> str:
    """Constructive approach - validate and transform."""
    if not isinstance(raw, str):  # Boundary check
        return str(raw)  # Explicit conversion
    return raw
