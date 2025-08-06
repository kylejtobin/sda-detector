"""Test fixture for match/case statement violations.

This module demonstrates pattern matching that violates SDA principles.
Match/case statements should be replaced with discriminated union dispatch.
"""

from enum import Enum
from typing import Any


class Status(Enum):
    """Status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


def handle_status(status: Status) -> str:
    """VIOLATION: Match/case instead of behavioral enum."""
    # ❌ BAD: Pattern matching for business logic
    match status:  # Match/case violation!
        case Status.PENDING:
            return "Waiting to start"
        case Status.PROCESSING:
            return "Currently processing"
        case Status.COMPLETED:
            return "Successfully completed"
        case Status.FAILED:
            return "Operation failed"
        case _:
            return "Unknown status"


def process_command(command: dict[str, Any]) -> Any:
    """VIOLATION: Nested match statements."""
    # ❌ BAD: Complex nested pattern matching
    match command["type"]:  # Outer match violation!
        case "create":
            match command["resource"]:  # Nested match violation!
                case "user":
                    return create_user(command["data"])
                case "order":
                    return create_order(command["data"])
                case _:
                    return None
        case "update":
            return update_resource(command)
        case "delete":
            return delete_resource(command)
        case _:
            return None


def parse_response(response_code: int) -> str:
    """VIOLATION: Match on primitive values."""
    # ❌ BAD: Pattern matching on status codes
    match response_code:  # Match violation!
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"


# Dummy functions for the example
def create_user(data): return f"User: {data}"
def create_order(data): return f"Order: {data}"
def update_resource(cmd): return f"Update: {cmd}"
def delete_resource(cmd): return f"Delete: {cmd}"


# ============================================================================
# SDA-COMPLIANT ALTERNATIVES
# ============================================================================

from enum import StrEnum


class StatusSDA(StrEnum):
    """✅ GOOD: Behavioral enum with methods."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def get_message(self) -> str:
        """Behavioral method - enum knows its own message."""
        messages = {
            StatusSDA.PENDING: "Waiting to start",
            StatusSDA.PROCESSING: "Currently processing",
            StatusSDA.COMPLETED: "Successfully completed",
            StatusSDA.FAILED: "Operation failed",
        }
        return messages[self]


def handle_status_sda(status: StatusSDA) -> str:
    """✅ GOOD: Use behavioral method instead of match."""
    return status.get_message()


class CommandType(StrEnum):
    """✅ GOOD: Command types with dispatch."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    
    def execute(self, command: dict) -> Any:
        """Pure dispatch - no conditionals."""
        handlers = {
            CommandType.CREATE: lambda cmd: create_resource(cmd),
            CommandType.UPDATE: lambda cmd: update_resource(cmd),
            CommandType.DELETE: lambda cmd: delete_resource(cmd),
        }
        return handlers[self](command)


def create_resource(command: dict) -> Any:
    """Delegate to resource-specific creation."""
    resource_type = command.get("resource", "")
    # Use another discriminated union for resource types
    return f"Creating {resource_type}"


# The SDA way: Discriminated unions with behavioral methods
# Every branch becomes a type with its own behavior
# No match/case - just polymorphic dispatch