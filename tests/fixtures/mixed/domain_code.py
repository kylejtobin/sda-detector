"""Pure domain code - should have high SDA pattern compliance."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field


# ✅ Pure domain enum with rich behavior
class AccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"

    @property
    def has_overdraft_protection(self) -> bool:
        """Business rule encoded in enum"""
        return self in [self.CHECKING, self.CREDIT]

    @property
    def earns_interest(self) -> bool:
        """Another business rule"""
        return self in [self.SAVINGS, self.INVESTMENT]

    @property
    def minimum_balance(self) -> Decimal:
        """Computed minimum balance based on account type"""
        minimums = {
            self.CHECKING: Decimal("0"),
            self.SAVINGS: Decimal("100"),
            self.CREDIT: Decimal("0"),
            self.INVESTMENT: Decimal("1000"),
        }
        return minimums[self]


# ✅ Rich value object
class Money(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount: Decimal = Field(decimal_places=2)
    currency: str = Field(min_length=3, max_length=3, default="USD")

    @computed_field
    @property
    def is_positive(self) -> bool:
        """Business logic in computed field"""
        return self.amount > 0

    @computed_field
    @property
    def is_negative(self) -> bool:
        """Business logic in computed field"""
        return self.amount < 0

    @computed_field
    @property
    def formatted(self) -> str:
        """Display formatting as computed field"""
        return f"{self.currency} {self.amount:.2f}"

    def add(self, other: "Money") -> "Money":
        """Domain operation"""
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        """Domain operation"""
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(amount=self.amount - other.amount, currency=self.currency)


# ✅ Rich domain entity
class Account(BaseModel):
    model_config = ConfigDict(frozen=True)

    account_number: str = Field(min_length=10, max_length=12)
    account_type: AccountType
    balance: Money
    owner_name: str = Field(min_length=1)
    is_active: bool = True

    @computed_field
    @property
    def is_overdrawn(self) -> bool:
        """Business logic in computed field"""
        return self.balance.is_negative

    @computed_field
    @property
    def available_balance(self) -> Money:
        """Complex business logic"""
        if self.account_type.has_overdraft_protection:
            # Checking and credit accounts have overdraft
            overdraft_limit = Money(amount=Decimal("500"), currency=self.balance.currency)
            return self.balance.add(overdraft_limit)
        else:
            # Savings and investment accounts - only available balance
            return (
                self.balance if self.balance.is_positive else Money(amount=Decimal("0"), currency=self.balance.currency)
            )

    @computed_field
    @property
    def meets_minimum_balance(self) -> bool:
        """Delegates to account type business rules"""
        return self.balance.amount >= self.account_type.minimum_balance

    @computed_field
    @property
    def can_withdraw(self) -> bool:
        """Business rule for withdrawals"""
        return self.is_active and self.available_balance.is_positive

    @computed_field
    @property
    def status_message(self) -> str:
        """Complex computed status"""
        if not self.is_active:
            return "Account Inactive"
        elif self.is_overdrawn:
            return "Account Overdrawn"
        elif not self.meets_minimum_balance:
            return "Below Minimum Balance"
        else:
            return "Account Active"

    def deposit(self, amount: Money) -> "Account":
        """Domain operation with immutable update"""
        if not amount.is_positive:
            raise ValueError("Deposit amount must be positive")
        if amount.currency != self.balance.currency:
            raise ValueError("Currency mismatch")

        new_balance = self.balance.add(amount)
        return self.model_copy(update={"balance": new_balance})

    def withdraw(self, amount: Money) -> "Account":
        """Domain operation with business rules"""
        if not amount.is_positive:
            raise ValueError("Withdrawal amount must be positive")
        if not self.can_withdraw:
            raise ValueError("Cannot withdraw from this account")
        if amount.amount > self.available_balance.amount:
            raise ValueError("Insufficient funds")

        new_balance = self.balance.subtract(amount)
        return self.model_copy(update={"balance": new_balance})

    def deactivate(self) -> "Account":
        """State change operation"""
        return self.model_copy(update={"is_active": False})

    def activate(self) -> "Account":
        """State change operation"""
        return self.model_copy(update={"is_active": True})


# ✅ Domain service that orchestrates domain models
class AccountService:
    """Focused domain service - coordinates domain logic"""

    def transfer_funds(self, from_account: Account, to_account: Account, amount: Money) -> tuple[Account, Account]:
        """Domain operation that coordinates multiple entities"""
        # Domain models handle their own validation and business rules
        updated_from = from_account.withdraw(amount)
        updated_to = to_account.deposit(amount)

        return updated_from, updated_to

    def calculate_interest(self, account: Account, annual_rate: Decimal) -> Money | None:
        """Domain calculation"""
        if not account.account_type.earns_interest:
            return None

        # Simple monthly interest calculation
        monthly_rate = annual_rate / 12
        interest_amount = account.balance.amount * monthly_rate

        return Money(amount=interest_amount, currency=account.balance.currency)

    def apply_monthly_interest(self, account: Account, annual_rate: Decimal) -> Account:
        """Domain operation"""
        interest = self.calculate_interest(account, annual_rate)
        if interest is None:
            return account

        return account.deposit(interest)


# Expected patterns:
# - 3+ pydantic_models (Money, Account, plus any others)
# - 1+ behavioral_enums (AccountType with methods and properties)
# - 12+ computed_fields (various @computed_field properties)
# - 8+ field_constraints (Field() usage with validation)
# - 6+ immutable_updates (model_copy usage)
# - Should be classified as MODULE TYPE: domain
# - Very few or zero violations (pure domain code)
