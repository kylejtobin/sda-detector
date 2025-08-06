"""Rich domain model patterns - SDA principles in action."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field


# ✅ Behavioral enum with methods
class OrderStatus(StrEnum):
    DRAFT = "draft"
    PLACED = "placed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    def can_transition_to(self, target: "OrderStatus") -> bool:
        """Enum knows its own state machine rules"""
        transitions = {
            self.DRAFT: [self.PLACED, self.CANCELLED],
            self.PLACED: [self.PAID, self.CANCELLED],
            self.PAID: [self.SHIPPED, self.CANCELLED],
            self.SHIPPED: [self.DELIVERED],
            self.DELIVERED: [],
            self.CANCELLED: [],
        }
        return target in transitions.get(self, [])

    @property
    def is_terminal(self) -> bool:
        """Computed property on enum"""
        return self in [self.DELIVERED, self.CANCELLED]

    @property
    def can_be_cancelled(self) -> bool:
        """Business logic in the enum"""
        return self in [self.DRAFT, self.PLACED, self.PAID]


# ✅ Rich value object
class Money(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: Decimal) -> "Money":
        return Money(amount=self.amount * factor, currency=self.currency)

    @computed_field
    @property
    def formatted(self) -> str:
        """Computed field for display"""
        return f"{self.amount:.2f} {self.currency}"


# ✅ Domain model with computed fields and behavior
class LineItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_name: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: Money

    @computed_field
    @property
    def total_price(self) -> Money:
        """Computed field instead of separate function"""
        return self.unit_price.multiply(Decimal(self.quantity))

    @computed_field
    @property
    def is_bulk_order(self) -> bool:
        """Business logic in computed field"""
        return self.quantity >= 10


# ✅ Rich aggregate with domain intelligence
class Order(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str | None = None
    customer_email: str = Field(regex=r"^[^@]+@[^@]+\.[^@]+$")
    items: list[LineItem] = Field(min_items=1)
    status: OrderStatus = OrderStatus.DRAFT

    @computed_field
    @property
    def total_amount(self) -> Money:
        """Computed field aggregates line items"""
        if not self.items:
            return Money(amount=Decimal("0"), currency="USD")

        total = self.items[0].total_price
        for item in self.items[1:]:
            total = total.add(item.total_price)
        return total

    @computed_field
    @property
    def item_count(self) -> int:
        """Simple computed field"""
        return sum(item.quantity for item in self.items)

    @computed_field
    @property
    def can_be_cancelled(self) -> bool:
        """Delegates to enum intelligence"""
        return self.status.can_be_cancelled

    @computed_field
    @property
    def is_large_order(self) -> bool:
        """Business rule in computed field"""
        return self.total_amount.amount > Decimal("1000") or self.item_count > 20

    def place(self) -> "Order":
        """Domain method with state transition"""
        if not self.can_be_cancelled:
            raise ValueError("Order cannot be placed from current status")
        return self.model_copy(update={"status": OrderStatus.PLACED})

    def add_item(self, item: LineItem) -> "Order":
        """Immutable update pattern"""
        return self.model_copy(update={"items": self.items + [item]})


# ✅ Another rich domain model
class Customer(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str = Field(regex=r"^[^@]+@[^@]+\.[^@]+$")
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    order_count: int = Field(ge=0, default=0)

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed field for derived data"""
        return f"{self.first_name} {self.last_name}"

    @computed_field
    @property
    def is_premium_customer(self) -> bool:
        """Business classification logic"""
        return self.order_count >= 10

    @computed_field
    @property
    def discount_rate(self) -> Decimal:
        """Computed business rule"""
        return Decimal("0.15") if self.is_premium_customer else Decimal("0.05")


# Expected patterns:
# - 4+ pydantic_models (Money, LineItem, Order, Customer)
# - 1+ behavioral_enums (OrderStatus with methods)
# - 10+ computed_fields (all the @computed_field properties)
# - 6+ field_constraints (Field() usage with validation)
# - 4+ immutable_updates (model_copy usage)
