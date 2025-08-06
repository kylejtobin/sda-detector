"""Test fixture for repeated string literal violations.

This module demonstrates repeated string literals that should be domain concepts.
Repeated strings indicate missing enums or constants.
"""


class OrderProcessor:
    """Order processing with repeated string literals."""
    
    def __init__(self):
        # ❌ BAD: String literal "pending" appears multiple times
        self.status = "pending"  # First occurrence
    
    def start_processing(self):
        """VIOLATION: Repeated status string."""
        if self.status == "pending":  # Second occurrence of "pending"
            self.status = "processing"  # First occurrence of "processing"
            return True
        return False
    
    def complete_order(self):
        """VIOLATION: More repeated strings."""
        if self.status == "processing":  # Second occurrence of "processing"
            self.status = "completed"
            return "Order completed"
        elif self.status == "pending":  # Third occurrence of "pending"!
            return "Cannot complete pending order"
        return "Invalid state"
    
    def cancel_order(self):
        """VIOLATION: Even more string repetition."""
        if self.status != "completed":
            self.status = "cancelled"
            return "Order cancelled"
        return "Cannot cancel completed order"


def validate_environment(env: str) -> bool:
    """VIOLATION: Environment strings repeated."""
    # ❌ BAD: "production" appears 3 times
    if env == "production":  # First occurrence
        print("Running in production")  # Second occurrence in message
        return True
    elif env == "staging":
        print("Running in staging")
        return True
    elif env == "development":
        print("Running in development")
        return True
    else:
        print("Unknown environment, defaulting to production")  # Third occurrence!
        return False


def process_log_level(level: str) -> int:
    """VIOLATION: Log level strings repeated."""
    # ❌ BAD: These strings appear multiple times across the codebase
    if level == "debug":  # First occurrence
        return 10
    elif level == "info":  # First occurrence
        return 20
    elif level == "warning":  # First occurrence
        return 30
    elif level == "error":  # First occurrence
        return 40
    return 20  # Default to info


def get_log_message(level: str) -> str:
    """VIOLATION: Same strings repeated again."""
    # ❌ BAD: Repeating the same log level strings
    messages = {
        "debug": "Debug message",  # Second occurrence of "debug"
        "info": "Info message",  # Second occurrence of "info"
        "warning": "Warning message",  # Second occurrence of "warning"
        "error": "Error message",  # Second occurrence of "error"
    }
    return messages.get(level, "Unknown level")


# ============================================================================
# SDA-COMPLIANT ALTERNATIVES
# ============================================================================

from enum import StrEnum


class OrderStatus(StrEnum):
    """✅ GOOD: Domain concept as enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Environment(StrEnum):
    """✅ GOOD: Environment as explicit type."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    
    def validate(self) -> bool:
        """Behavioral method on enum."""
        print(f"Running in {self.value}")
        return True


class LogLevel(StrEnum):
    """✅ GOOD: Log levels as enum with behavior."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    
    def get_priority(self) -> int:
        """Each level knows its priority."""
        priorities = {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
        }
        return priorities[self]
    
    def get_message(self) -> str:
        """Each level knows its message format."""
        return f"{self.value.title()} message"


class OrderProcessorSDA:
    """✅ GOOD: Using enum instead of string literals."""
    
    def __init__(self):
        self.status = OrderStatus.PENDING
    
    def start_processing(self) -> bool:
        """Type-safe status checks."""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.PROCESSING
            return True
        return False


# The SDA way: Every repeated string is a missing domain concept
# Create enums for finite sets of values
# No magic strings - everything has a type