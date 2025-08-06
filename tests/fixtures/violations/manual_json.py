"""Manual JSON serialization violations - bypasses Pydantic type safety."""

import json
from json import dumps, loads

# ❌ Manual JSON serialization (detected violation)
user_data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
json_string = json.dumps(user_data)  # Manual serialization
parsed_data = json.loads(json_string)  # Manual deserialization

# ❌ Also catches imported forms
serialized = dumps(user_data)
deserialized = loads(serialized)


# ❌ Complex manual serialization
def serialize_order(order_dict):
    """Manual serialization function"""
    return json.dumps(order_dict, indent=2, sort_keys=True)


def deserialize_order(json_str):
    """Manual deserialization function"""
    return json.loads(json_str)


# ❌ Even in classes
class JsonHandler:
    def save_data(self, data):
        return json.dumps(data)

    def load_data(self, json_str):
        return json.loads(json_str)


# Expected violations: 6 manual_json_serialization detections
# (json.dumps, json.loads, dumps, loads, and 2 more in methods)
