"""Enum value unwrapping violations - primitive obsession with .value calls."""

from enum import Enum, StrEnum


class OrderStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class QueueType(StrEnum):
    STORAGE_PROCESSING = "storage_processing"
    PAYMENT_PROCESSING = "payment_processing"
    NOTIFICATION = "notification"


# ❌ Enum value unwrapping (detected violations)
def process_order():
    # Should use OrderStatus.DRAFT directly (StrEnum converts automatically)
    status = OrderStatus.DRAFT.value
    queue = QueueType.STORAGE_PROCESSING.value
    priority_level = Priority.HIGH.value

    return {"status": status, "queue": queue, "priority": priority_level}


# ❌ More unwrapping violations
class OrderProcessor:
    def __init__(self):
        self.default_status = OrderStatus.PENDING.value  # Primitive obsession
        self.queue_name = QueueType.PAYMENT_PROCESSING.value

    def set_priority(self, priority: Priority):
        # Storing primitive instead of rich enum
        self.priority_value = priority.value

    def get_status_string(self, status: OrderStatus) -> str:
        # Unnecessary unwrapping - StrEnum converts automatically
        return f"Order is {status.value}"


# ❌ Function using unwrapped values
def create_database_record(order_status: OrderStatus, priority: Priority):
    return {
        "status_code": order_status.value,  # Could use order_status directly
        "priority_num": priority.value,  # Losing type information
        "created_at": "2024-01-01",
    }


# ❌ Even more unwrapping
def send_notification(queue_type: QueueType):
    queue_name = queue_type.value  # Primitive obsession
    print(f"Sending to {queue_name}")


# Expected violations: 8+ enum_value_unwrapping detections
# All the .value calls that suggest primitive obsession
