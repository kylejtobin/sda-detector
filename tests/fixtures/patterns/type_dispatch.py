"""Type dispatch patterns - conditional elimination using data structures."""

from collections.abc import Callable
from enum import StrEnum
from typing import Any


# ✅ Type dispatch table instead of if/else chains
class EventType(StrEnum):
    USER_CREATED = "user_created"
    ORDER_PLACED = "order_placed"
    PAYMENT_PROCESSED = "payment_processed"
    ORDER_SHIPPED = "order_shipped"


class EventProcessor:
    """Demonstrates type dispatch pattern"""

    def __init__(self):
        # ✅ Type dispatch table - data drives behavior
        self.handlers: dict[EventType, Callable[[dict], str]] = {
            EventType.USER_CREATED: self._handle_user_created,
            EventType.ORDER_PLACED: self._handle_order_placed,
            EventType.PAYMENT_PROCESSED: self._handle_payment_processed,
            EventType.ORDER_SHIPPED: self._handle_order_shipped,
        }

    def process_event(self, event_type: EventType, event_data: dict) -> str:
        """Use dispatch table instead of if/elif chain"""
        # ✅ Data selects the handler - no conditionals
        handler = self.handlers.get(event_type, self._handle_unknown)
        return handler(event_data)

    def _handle_user_created(self, data: dict) -> str:
        return f"User {data.get('user_id')} created"

    def _handle_order_placed(self, data: dict) -> str:
        return f"Order {data.get('order_id')} placed"

    def _handle_payment_processed(self, data: dict) -> str:
        return f"Payment {data.get('transaction_id')} processed"

    def _handle_order_shipped(self, data: dict) -> str:
        return f"Order {data.get('order_id')} shipped"

    def _handle_unknown(self, data: dict) -> str:
        return "Unknown event type"


# ✅ State-based dispatch
class OrderState(StrEnum):
    DRAFT = "draft"
    PLACED = "placed"
    PAID = "paid"
    SHIPPED = "shipped"


class OrderStateMachine:
    """State machine using dispatch tables"""

    def __init__(self):
        # ✅ State transition table
        self.transitions: dict[OrderState, list[OrderState]] = {
            OrderState.DRAFT: [OrderState.PLACED],
            OrderState.PLACED: [OrderState.PAID],
            OrderState.PAID: [OrderState.SHIPPED],
            OrderState.SHIPPED: [],
        }

        # ✅ Action dispatch table
        self.state_actions: dict[OrderState, Callable[[], str]] = {
            OrderState.DRAFT: lambda: "Order is being prepared",
            OrderState.PLACED: lambda: "Order has been placed",
            OrderState.PAID: lambda: "Payment confirmed",
            OrderState.SHIPPED: lambda: "Order is on its way",
        }

    def can_transition(self, from_state: OrderState, to_state: OrderState) -> bool:
        """Check valid transitions using dispatch table"""
        return to_state in self.transitions.get(from_state, [])

    def get_state_message(self, state: OrderState) -> str:
        """Get message using dispatch table"""
        action = self.state_actions.get(state, lambda: "Unknown state")
        return action()


# ✅ Boolean coercion array indexing (SDA's purest form)
class StatusIndicator:
    """Demonstrates boolean coercion pattern"""

    def get_status_icon(self, is_active: bool) -> str:
        """Data drives behavior - no conditionals"""
        # ✅ Boolean becomes array index - pure data selection
        icons = ["❌", "✅"]  # [False, True] -> [0, 1]
        return icons[int(is_active)]

    def get_priority_label(self, is_urgent: bool) -> str:
        """Another boolean dispatch example"""
        labels = ["Normal", "URGENT"]
        return labels[int(is_urgent)]

    def get_access_level(self, is_admin: bool) -> str:
        """Data selects access level"""
        levels = ["User", "Administrator"]
        return levels[int(is_admin)]


# ✅ More complex dispatch patterns
class MessageFormatter:
    """Format messages using type dispatch"""

    def __init__(self):
        # ✅ Formatter dispatch table
        self.formatters: dict[str, Callable[[Any], str]] = {
            "success": lambda msg: f"✅ Success: {msg}",
            "error": lambda msg: f"❌ Error: {msg}",
            "warning": lambda msg: f"⚠️  Warning: {msg}",
            "info": lambda msg: f"ℹ️  Info: {msg}",
        }

    def format_message(self, message_type: str, content: Any) -> str:
        """Use dispatch table for formatting"""
        formatter = self.formatters.get(message_type, lambda x: str(x))
        return formatter(content)


# ✅ Enum-based computation dispatch
class CalculationType(StrEnum):
    ADDITION = "add"
    SUBTRACTION = "subtract"
    MULTIPLICATION = "multiply"
    DIVISION = "divide"


class Calculator:
    """Calculator using enum dispatch"""

    def __init__(self):
        # ✅ Operation dispatch table
        self.operations: dict[CalculationType, Callable[[float, float], float]] = {
            CalculationType.ADDITION: lambda a, b: a + b,
            CalculationType.SUBTRACTION: lambda a, b: a - b,
            CalculationType.MULTIPLICATION: lambda a, b: a * b,
            CalculationType.DIVISION: lambda a, b: a / b if b != 0 else 0,
        }

    def calculate(self, operation: CalculationType, a: float, b: float) -> float:
        """Perform calculation using dispatch"""
        operation_func = self.operations.get(operation, lambda x, y: 0)
        return operation_func(a, b)


# Expected patterns:
# - Multiple type_dispatch_tables (handlers, transitions, formatters, operations)
# - Boolean coercion array indexing examples
# - Enum-based dispatch patterns
# - Elimination of if/elif chains through data structures
