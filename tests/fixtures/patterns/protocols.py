"""Protocol usage patterns - interface contracts and dependency injection."""

from typing import Protocol, runtime_checkable


# ✅ Protocol for clean interfaces
@runtime_checkable
class EmailSender(Protocol):
    """Protocol defines what we need from email systems"""

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email and return success status"""
        ...

    def send_bulk_email(self, recipients: list[str], subject: str, body: str) -> int:
        """Send bulk email and return count of successful sends"""
        ...


# ✅ Another protocol
class PaymentProcessor(Protocol):
    """Protocol for payment processing capabilities"""

    def charge_card(self, amount: float, card_token: str) -> str:
        """Charge a card and return transaction ID"""
        ...

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        """Refund a payment"""
        ...


# ✅ Storage protocol
class DataRepository(Protocol):
    """Protocol for data persistence"""

    def save(self, entity_id: str, data: dict) -> None:
        """Save entity data"""
        ...

    def get(self, entity_id: str) -> dict:
        """Retrieve entity data"""
        ...

    def delete(self, entity_id: str) -> bool:
        """Delete entity"""
        ...


# ✅ Logger protocol
class Logger(Protocol):
    """Protocol for logging capabilities"""

    def info(self, message: str) -> None:
        """Log info message"""
        ...

    def error(self, message: str, exception: Exception = None) -> None:
        """Log error message"""
        ...


# ✅ Cache protocol
class CacheProvider(Protocol):
    """Protocol for caching capabilities"""

    def get(self, key: str) -> str | None:
        """Get cached value"""
        ...

    def set(self, key: str, value: str, ttl: int = 300) -> None:
        """Set cached value with TTL"""
        ...

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        ...


# ✅ Service using protocols (dependency injection)
class OrderService:
    """Service that depends on protocols, not concrete implementations"""

    def __init__(
        self,
        email_sender: EmailSender,
        payment_processor: PaymentProcessor,
        repository: DataRepository,
        logger: Logger,
        cache: CacheProvider,
    ):
        self.email_sender = email_sender
        self.payment_processor = payment_processor
        self.repository = repository
        self.logger = logger
        self.cache = cache

    def process_order(self, order_data: dict) -> str:
        """Process order using injected dependencies"""
        try:
            # Use protocol methods
            transaction_id = self.payment_processor.charge_card(order_data["amount"], order_data["card_token"])

            # Save to repository
            self.repository.save(order_data["id"], order_data)

            # Send confirmation email
            self.email_sender.send_email(
                order_data["customer_email"],
                "Order Confirmation",
                f"Your order has been processed. Transaction: {transaction_id}",
            )

            # Cache result
            self.cache.set(f"order:{order_data['id']}", transaction_id)

            self.logger.info(f"Order {order_data['id']} processed successfully")
            return transaction_id

        except Exception as e:
            self.logger.error(f"Failed to process order {order_data['id']}", e)
            raise


# ✅ Another service using protocols
class NotificationService:
    """Service using email protocol"""

    def __init__(self, email_sender: EmailSender, logger: Logger):
        self.email_sender = email_sender
        self.logger = logger

    def send_welcome_email(self, customer_email: str, customer_name: str) -> None:
        """Send welcome email to new customer"""
        subject = "Welcome to our service!"
        body = f"Hello {customer_name}, welcome to our platform!"

        success = self.email_sender.send_email(customer_email, subject, body)
        if success:
            self.logger.info(f"Welcome email sent to {customer_email}")
        else:
            self.logger.error(f"Failed to send welcome email to {customer_email}")


# Expected patterns:
# - 6+ protocols (EmailSender, PaymentProcessor, DataRepository, Logger, CacheProvider, etc.)
# - Clean dependency injection in services
# - No concrete dependencies in business logic
