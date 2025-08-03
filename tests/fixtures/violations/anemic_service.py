"""Anemic service pattern - bag of functions with no cohesion."""

from typing import Any


# ❌ Anemic service (detected violation)
class OrderService:
    """Classic anemic service - just a bag of static functions"""

    @staticmethod
    def create_order(data: dict) -> dict:
        return {"id": 1, **data}

    @staticmethod
    def update_order(order_id: int, data: dict) -> dict:
        return {"id": order_id, **data}

    @staticmethod
    def delete_order(order_id: int) -> bool:
        return True

    @staticmethod
    def get_order(order_id: int) -> dict:
        return {"id": order_id}

    @staticmethod
    def validate_order(order: dict) -> bool:
        return "items" in order

    @staticmethod
    def format_order(order: dict) -> str:
        return f"Order #{order['id']}"

    @staticmethod
    def parse_order_data(raw: str) -> dict:
        return {"parsed": True}

    @staticmethod
    def transform_order(order: dict) -> dict:
        return {"transformed": True}

    @staticmethod
    def process_order(order: dict) -> dict:
        return {"processed": True}

    @staticmethod
    def handle_order(order: dict) -> dict:
        return {"handled": True}

    @staticmethod
    def convert_order(order: dict) -> dict:
        return {"converted": True}

    @staticmethod
    def execute_order(order: dict) -> dict:
        return {"executed": True}


# ❌ Another anemic service
class UserService:
    """Another bag of utility functions"""

    @staticmethod
    def get_user(user_id: int) -> dict:
        return {"id": user_id}

    @staticmethod
    def create_user(data: dict) -> dict:
        return {"id": 1, **data}

    @staticmethod
    def update_user(user_id: int, data: dict) -> dict:
        return {"id": user_id, **data}

    @staticmethod
    def delete_user(user_id: int) -> bool:
        return True

    @staticmethod
    def validate_user(user: dict) -> bool:
        return "email" in user

    @staticmethod
    def format_user(user: dict) -> str:
        return f"User #{user['id']}"

    @staticmethod
    def parse_user_data(raw: str) -> dict:
        return {"parsed": True}

    @staticmethod
    def transform_user(user: dict) -> dict:
        return {"transformed": True}

    @staticmethod
    def helper_function(data: Any) -> Any:
        return data


# Expected violations: 2 anemic_services detections
# Both OrderService and UserService have high static method ratios,
# utility method names, and too many methods
