"""Runtime type checking violations - should use protocols/type dispatch."""

from typing import Any


# ❌ isinstance violations (detected)
def process_data(data: Any) -> str:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, int):
        return str(data)
    elif isinstance(data, list):
        return ",".join(str(x) for x in data)
    else:
        return "unknown"


# ❌ More isinstance checking
def handle_response(response: Any) -> dict:
    if isinstance(response, dict):
        return response
    elif isinstance(response, str):
        return {"message": response}
    elif isinstance(response, Exception):
        return {"error": str(response)}
    else:
        return {"data": response}


# ❌ hasattr violations (detected)
def get_name(obj: Any) -> str:
    if hasattr(obj, "name"):
        return obj.name
    elif hasattr(obj, "title"):
        return obj.title
    else:
        return "unknown"


# ❌ getattr violations (detected)
def get_value(obj: Any, key: str) -> Any:
    return getattr(obj, key, None)


# ❌ Combined type checking mess
class DataProcessor:
    def process(self, item: Any) -> Any:
        if isinstance(item, str):
            if hasattr(item, "encode"):
                return item.encode()
        elif isinstance(item, int):
            return str(item)
        elif isinstance(item, dict):
            if hasattr(item, "keys"):
                return list(item.keys())

        return getattr(item, "value", None)


# ❌ More runtime checking
def format_value(value: str | int | float) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return f"{value:.2f}"
    else:
        return "N/A"


# Expected violations:
# - 10+ isinstance_violations
# - 3+ hasattr_violations
# - 2+ getattr_violations
