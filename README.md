# 🧠 SDA Detector

**Transform your Python code from procedural checking to type-driven intelligence**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![Code style: SDA](https://img.shields.io/badge/code%20style-SDA-purple.svg)](https://github.com/kylejobin/sda-detector)
[![License](https://img.shields.io/github/license/kylejtobin/sda-detector)](https://github.com/kylejobin/sda-detector/blob/main/LICENSE)

> **"What if your data knew what to do with itself?"**

You know that moment when you're reading code and you realize the actual business logic is scattered across seventeen files, hidden behind three layers of abstraction, defended by try/except blocks that catch exceptions that should never happen?

That's not architecture. That's archaeology.

## 🎯 What is SDA Detector?

SDA Detector analyzes Python codebases to identify Semantic Domain Architecture patterns - a paradigm where **data drives behavior** instead of conditional logic checking data. It's both a practical analysis tool and a living demonstration of these principles.

The detector doesn't prescribe or judge - it observes and reports. You get objective metrics about your code's architectural patterns, not opinions about whether they're "good" or "bad".

### Core Principle: Software by Subtraction

SDA works not because of what it adds, but because of what it **refuses to do**. Every pattern you don't need. Every layer you don't add. Every abstraction you don't create. Your models should be domain experts, not data buckets.

```python
# What we write (data bucket)
class Temperature:
    celsius: float

# What we should write (domain expert)
class Temperature(BaseModel):
    celsius: Decimal = Field(ge=-273.15)  # Knows absolute zero

    @property
    def fahrenheit(self) -> Decimal:
        return self.celsius * Decimal('1.8') + 32

    @property
    def state_of_water(self) -> WaterState:
        return WaterState.from_celsius(self.celsius)  # Water knows its physics
```

One teaches you about temperature. The other one just... holds a number.

## 📖 SDA in 30 Seconds

Here's every SDA principle in one example:

```python
from enum import StrEnum
from decimal import Decimal
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated, Union

class PaymentStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    def next_status(self, event_type: str) -> "PaymentStatus":
        """State machine with pure dictionary dispatch."""
        transitions = {
            ("pending", "approve"): PaymentStatus.COMPLETED,
            ("pending", "reject"): PaymentStatus.FAILED,
            ("failed", "retry"): PaymentStatus.PENDING,
        }
        return transitions.get((self.value, event_type), self)

class CardPayment(BaseModel):
    type: Literal["card"]
    card_number: str = Field(pattern=r"^\d{16}$")
    amount: Decimal = Field(gt=0, decimal_places=2)

    def process(self) -> PaymentStatus:
        # Card processing logic
        return PaymentStatus.COMPLETED

class BankTransfer(BaseModel):
    type: Literal["bank"]
    account_number: str
    routing_number: str
    amount: Decimal = Field(gt=0, decimal_places=2)

    def process(self) -> PaymentStatus:
        # Bank transfer logic
        return PaymentStatus.PENDING

PaymentMethod = Annotated[
    Union[CardPayment, BankTransfer],
    Field(discriminator="type")
]

class Payment(BaseModel):
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING

    model_config = {"frozen": True}  # Immutable

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Derived state, not stored."""
        return self.status == PaymentStatus.COMPLETED

    def process(self) -> "Payment":
        """Returns new Payment with updated status."""
        new_status = self.method.process()
        return self.model_copy(update={"status": new_status})
```

**Zero conditionals.** Types select behavior. Data drives decisions. States are immutable. Business rules live in the model.

This is SDA.

## 🏗️ What is Semantic Domain Architecture?

SDA is an architectural philosophy built on one core truth: **data drives behavior**.

Instead of writing conditional logic that _checks_ data, you create types where data _selects_ behavior automatically. This fundamental shift transforms how you think about code.

### The Problem We All Face

You know what's wild? Half the developers I show this to act like I just invented fire. "You can put methods... on your models?" Yes. Yes you can. It's been possible since roughly 1967 when Ole-Johan Dahl and Kristen Nygaard invented object-oriented programming. **We just... forgot.**

We've been writing this:

```python
# The "architecture" we've all built
class Order:
    items: list[dict]
    status: str

class OrderService:
    def calculate_total(self, order: Order) -> float:
        # 50 lines of logic

    def can_cancel(self, order: Order) -> bool:
        # 30 lines of logic

    def apply_discount(self, order: Order, discount: float) -> float:
        # 40 lines of logic
```

When we should write this:

```python
class Order(BaseModel):
    items: list[LineItem]
    status: OrderStatus

    @computed_field
    @property
    def total(self) -> Money:
        return sum((item.total for item in self.items), Money.zero())

    def cancel(self) -> "Order":
        return self.status.cancel_order(self)  # Status knows the state machine
```

The order knows how to be an order. Revolutionary concept, I know.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/kylejobin/sda-detector.git
cd sda-detector

# One-command setup (installs all dependencies and package in dev mode)
make setup
```

### Basic Usage

```bash
# Analyze any file (after running 'make setup')
make run FILE=my_module.py

# Self-analysis (dogfooding)
make self-analyze

# Manual execution
uv run python -m sda_detector my_module.py

# Analyze a directory
uv run python -m sda_detector src/domain/

# Analyze with custom name
uv run python -m sda_detector src/models/ "User Domain Models"
```

## 🧪 The SDA Litmus Test

Run this on your most important module:

```bash
grep -c "if " your_module.py        # Conditionals
grep -c "isinstance" your_module.py # Type checking
grep -c ".get(" your_module.py      # Dictionary diving
grep -c "try:" your_module.py       # Exception control flow
```

Sum those numbers:
- **< 20**: You're doing well
- **20-50**: SDA would help significantly
- **50-100**: You need SDA yesterday
- **> 100**: Stop reading and start refactoring

### Example Output

```
🧠 SDA ARCHITECTURE ANALYSIS - MY_MODULE.PY
======================================================================
🔍 SDA PATTERNS DETECTED:
  business_conditionals       3 🔍
    → my_module.py:45 - business logic conditional
    → my_module.py:67 - business logic conditional
  isinstance_violations       2 🔍
    → my_module.py:23 - isinstance() runtime check
    → my_module.py:78 - isinstance() runtime check
  manual_json_serialization   2 🔍
    → my_module.py:15 - json.dumps() manual serialization
    → my_module.py:32 - json.loads() manual serialization
  enum_value_unwrapping       1 🔍
    → my_module.py:89 - enum value unwrapping - consider StrEnum for automatic conversion
  anemic_services             1 🔍
    → my_module.py:156 - anemic service - 5 utility-style method names, 12 methods

📊 ARCHITECTURAL FEATURES:
  pydantic_models             5 📊
    → my_module.py:12 - BaseModel: User
    → my_module.py:34 - BaseModel: Order
  computed_fields             8 📊
    → my_module.py:18 - @computed_field total_cost
    → my_module.py:29 - @computed_field full_name

MODULE TYPE: domain
FILES ANALYZED: 1
TOTAL VIOLATIONS: 9
TOTAL PATTERNS: 23
DISTRIBUTION: 71.9% patterns, 28.1% violations
```

## 💡 The Patterns That Actually Matter

### 1. Rich Types Over Primitive Obsession (The Bug Factory Pattern)

Every time you type `amount: float`, somewhere a developer cries debugging a currency mismatch. I've seen production systems lose thousands of dollars because someone forgot that the payment gateway expects cents but the invoice system uses dollars. True story.

```python
# The bug factory
def process_payment(amount: float, currency: str) -> float:
    # Hope everyone remembers amount is in cents!
    # Hope everyone passes currency in the same format!
    # Hope no one does math without considering currency!
    ...

# The domain model that prevents 3am debugging sessions
class Money(BaseModel):
    amount: Decimal
    currency: Currency

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def split_evenly(self, ways: int) -> list[Money]:
        """No lost pennies in rounding."""
        base_amount = (self.amount / ways).quantize(Decimal('0.01'))
        remainder = self.amount - (base_amount * ways)

        splits = [Money(base_amount, self.currency) for _ in range(ways)]
        # Add the remainder pennies to the first split
        if remainder:
            splits[0] = Money(base_amount + remainder, self.currency)
        return splits
```

Now `money + money` either works correctly or fails loudly. No silent bugs. No "wait, was that in cents or dollars?" at 3am.

### 2. Constructive Type Transformation (The Heart of SDA)

Every type transition must be provable through construction, not assertion. This is the difference between hoping your code works and knowing it does.

```python
# The assertion approach (hope and pray)
def process_payment(data: dict) -> Payment:
    # "Trust me, this dict has the right shape"
    return cast(Payment, data)  # type: ignore  # Famous last words

# The constructive approach (mathematical proof)
def process_payment(data: dict) -> Payment:
    # Step 1: Unpack explicitly
    amount_raw = data.get("amount")
    currency_raw = data.get("currency")

    # Step 2: Transform to domain types
    amount = Money.from_string(amount_raw) if amount_raw else Money.zero()
    currency = Currency(currency_raw) if currency_raw else Currency.USD

    # Step 3: Construct - if this succeeds, it's correct
    return Payment(amount=amount, currency=currency)
```

No casts. No type ignores. No "trust me bro" comments. The successful construction IS the proof.

### 3. Make Invalid States Unrepresentable (Discriminated Unions)

Remember every time you've written defensive programming nightmares? The pattern that eliminates entire categories of bugs:

```python
# The defensive programming nightmare we've all written
def send_notification(user_data: dict) -> None:
    # First, let's check if we have what we need...
    if "email" in user_data:
        # But wait, is it actually an email?
        if "@" in user_data["email"]:  # Top-tier email validation right here
            # Do we have a subject?
            subject = user_data.get("email_subject", "No Subject")
            # What about the body?
            body = user_data.get("email_body", "")
            send_email(user_data["email"], subject, body)
    elif "phone" in user_data:
        # Is it a valid phone number? Who knows!
        send_sms(user_data["phone"], user_data.get("sms_message", ""))
    else:
        # The famous "this should never happen" comment
        raise ValueError("No contact method")  # Narrator: It happened.

# The SDA way: discriminated unions make bugs impossible
class EmailNotification(BaseModel):
    type: Literal["email"] = "email"
    address: EmailAddress  # Can't be invalid - type validates!
    subject: str = Field(min_length=1)  # Can't forget - it's required!
    body: str

    def send(self) -> NotificationResult:
        return send_email(self.address, self.subject, self.body)

class SmsNotification(BaseModel):
    type: Literal["sms"] = "sms"
    phone: PhoneNumber  # Validated at construction
    message: str = Field(max_length=160)  # Remember SMS limits?

    def send(self) -> NotificationResult:
        return send_sms(self.phone, self.message)

Notification = Annotated[
    Union[EmailNotification, SmsNotification],
    Field(discriminator="type")
]

# Now this is impossible to mess up
def send_notification(notification: Notification) -> NotificationResult:
    return notification.send()  # The type knows what to do
```

The magic is in that `discriminator="type"`. Pydantic looks at the type field and automatically creates the right class. No isinstance checks, no manual dispatch. The type system is your router.

### 4. State Machines That Actually State Machine

Your business logic is full of state machines. Order workflows, user lifecycles, payment flows. But I bet they're implemented as string comparisons scattered across service methods, held together by hopes and comments that say "TODO: refactor this."

```python
class PaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

    def can_refund(self) -> bool:
        return self == self.COMPLETED

    def can_retry(self) -> bool:
        return self == self.FAILED

    def next_status(self, event: PaymentEvent) -> "PaymentStatus":
        transitions = {
            (self.PENDING, PaymentEvent.PROCESS): self.PROCESSING,
            (self.PROCESSING, PaymentEvent.SUCCEED): self.COMPLETED,
            (self.PROCESSING, PaymentEvent.FAIL): self.FAILED,
            (self.COMPLETED, PaymentEvent.REFUND): self.REFUNDED,
            (self.FAILED, PaymentEvent.RETRY): self.PENDING,
        }

        next_status = transitions.get((self, event))
        if next_status is None:
            raise InvalidTransition(f"Cannot {event} from {self}")
        return next_status

    def valid_events(self) -> set[PaymentEvent]:
        # Now you can actually ask "what can I do from here?"
        all_transitions = {...}  # The transition table
        return {event for (status, event), _ in all_transitions.items() if status == self}
```

Your enum now encodes your entire payment flow. One source of truth. No more "wait, can a refunded payment be processed again?" debates at sprint planning.

### 5. Boolean Coercion Array Indexing - SDA's Purest Teaching Moment

This pattern represents **SDA distilled to its essence** - it's impossible to think procedurally when you see it:

```python
# ❌ Procedural thinking (checking conditions)
if is_enum:
    self.context = self.context.model_copy(update={"in_enum_class": True})
else:
    self.context = self.context.model_copy(update={})

# ✅ SDA thinking (data drives behavior)
enum_context_updates = [
    {},  # False case (index 0)
    {"in_enum_class": True}  # True case (index 1)
]
self.context = self.context.model_copy(update=enum_context_updates[int(is_enum)])

# More examples of pure data-driven selection:
message = ["Failed", "Success"][int(operation_succeeded)]  # Data selects message
icon = ["❌", "✅"][bool(task.completed)]                   # Data selects display
handler = [self.reject, self.approve][int(valid)]          # Data selects function
```

**Why this pattern is transformative:**

When you see `result = ["inactive", "active"][bool(user.is_verified)]`, you **can't fall back on procedural habits**. There's no `if` keyword to lean on. You're forced to think:

- **"My data is selecting behavior"** (not "I'm checking a condition")
- **Data becomes the driver** (not conditions as controllers)
- **Values have inherent meaning** (not arbitrary checks)

This forces the mental model shift that SDA requires. It's like learning a language through immersion vs. translation - no procedural crutches allowed.

## 📚 Real-World Transformation

Let's fix the code we've all written at some point:

```python
# The "architecture" we've all built (and regretted)
class Product:
    sku: str
    name: str
    price: float  # Is this dollars? Cents? Bitcoin?
    discount_percentage: float
    stock_level: int
    reserved_stock: int
    category: str

class ProductService:
    def get_available_stock(self, product: Product) -> int:
        return product.stock_level - product.reserved_stock

    def calculate_price(self, product: Product) -> float:
        if product.discount_percentage > 0:
            return product.price * (1 - product.discount_percentage / 100)
        return product.price

    def can_purchase(self, product: Product, quantity: int) -> tuple[bool, str]:
        if quantity <= 0:
            return False, "Invalid quantity"

        available = self.get_available_stock(product)
        if available < quantity:
            return False, f"Only {available} items available"

        if product.category == "limited_edition" and quantity > 2:
            return False, "Limited edition items have a maximum quantity of 2"

        return True, "OK"

    def reserve_stock(self, product: Product, quantity: int) -> Product:
        # Mutates the product! What could go wrong?
        product.reserved_stock += quantity
        return product
```

And here's what it becomes with SDA:

```python
class StockLevel(BaseModel):
    total: Count = Field(ge=0)
    reserved: Count = Field(ge=0)

    model_config = {"frozen": True}  # Immutable!

    @field_validator('reserved')
    @classmethod
    def reserved_cannot_exceed_total(cls, v: Count, info: ValidationInfo) -> Count:
        if total := info.data.get('total'):
            if v > total:
                raise ValueError('Reserved cannot exceed total stock')
        return v

    @computed_field
    @property
    def available(self) -> Count:
        return Count(self.total - self.reserved)

    def reserve(self, quantity: Count) -> "StockLevel":
        """Immutable reservation - returns new StockLevel"""
        if quantity > self.available:
            raise InsufficientStock(requested=quantity, available=self.available)
        return self.model_copy(update={'reserved': self.reserved + quantity})

class ProductCategory(StrEnum):
    STANDARD = "standard"
    LIMITED_EDITION = "limited_edition"
    CLEARANCE = "clearance"

    @property
    def max_purchase_quantity(self) -> Count | None:
        """Some categories have purchase limits"""
        limits = {
            self.LIMITED_EDITION: Count(2),
            self.STANDARD: None,
            self.CLEARANCE: None
        }
        return limits[self]

class Price(BaseModel):
    amount: Money
    discount: Percent = Percent(0)

    @computed_field
    @property
    def final_amount(self) -> Money:
        """The actual price after discount"""
        if self.discount == Percent(0):
            return self.amount
        discount_multiplier = (Percent(100) - self.discount) / Percent(100)
        return self.amount * discount_multiplier

class Product(BaseModel):
    sku: ProductSku
    name: str
    price: Price
    stock: StockLevel
    category: ProductCategory

    model_config = {"frozen": True}

    def check_purchase_eligibility(self, quantity: Count) -> PurchaseEligibility:
        """All purchase rules in one place"""
        # Note: These conditionals are boundary validation, not business logic
        # In pure SDA, this would use a validation chain pattern
        if quantity <= 0:
            return PurchaseEligibility.invalid_quantity()

        if quantity > self.stock.available:
            return PurchaseEligibility.insufficient_stock(
                requested=quantity,
                available=self.stock.available
            )

        if max_qty := self.category.max_purchase_quantity:
            if quantity > max_qty:
                return PurchaseEligibility.exceeds_limit(max_qty)

        return PurchaseEligibility.eligible()

    def reserve_stock(self, quantity: Count) -> "Product":
        """Returns new Product with updated stock"""
        return self.model_copy(update={'stock': self.stock.reserve(quantity)})
```

What changed? Everything:
- No more float prices (was it dollars? cents? euros? bitcoin?)
- Stock logic lives with stock data
- Categories know their own rules
- Immutable operations (no more "who changed my product?!" debugging sessions)
- The model teaches you the business rules

## 🔄 Migration Patterns

### Start With Your Pain Points

Don't boil the ocean. Find the code that hurts most:

1. **The Bug Factory** - That module everyone's afraid to touch
2. **The String Status Soup** - Where business state lives in string comparisons
3. **The Defensive Nightmare** - Try/except wrapped in if/else wrapped in hope

### The Strangler Fig Pattern for SDA

Wrap your existing chaos with a clean SDA boundary:

```python
# Step 1: Create SDA wrapper around legacy code
class PaymentProcessor(BaseModel):
    """Clean SDA interface to legacy payment system"""

    @classmethod
    def from_legacy_data(cls, legacy_dict: dict) -> "PaymentProcessor":
        """Single extraction point from legacy system"""
        # All the messy conversion happens here ONCE
        return cls(...)

    def to_legacy_format(self) -> dict:
        """Single point to convert back if needed"""
        return {...}

# Step 2: Gradually move logic from legacy into the model
# Step 3: Eventually delete the legacy code entirely
```

### The "One Model at a Time" Approach

Pick ONE anemic model and make it smart:

```python
# Before: Anemic model + fat service
class User:
    id: int
    email: str
    status: str

class UserService:
    def can_purchase(self, user): ...
    def send_notification(self, user): ...
    def calculate_discount(self, user): ...

# After: Smart model, no service needed
class User(BaseModel):
    id: UserId
    email: Email
    status: UserStatus

    @computed_field
    @property
    def discount_tier(self) -> DiscountTier:
        return self.status.get_discount_tier()

    def can_purchase(self, product: Product) -> PurchaseEligibility:
        return self.status.check_purchase_eligibility(product)
```

Watch how this ripples through your codebase - suddenly other code gets simpler too.

## 🔍 What Does It Detect?

### SDA Violations (And Why They're Costing You)

#### isinstance_violations
**What it means:** Your code asks "what are you?" instead of "what can you do?"
**The cost:** Every isinstance is a future bug when someone adds a new type
**The fix:** Discriminated unions that handle dispatch automatically

#### business_conditionals
**What it means:** Business logic scattered in if/elif chains instead of types
**The cost:** Every condition is a place where logic can diverge and drift
**The fix:** StrEnum with behavioral methods or discriminated unions

#### dict_get_violations
**What it means:** Defensive programming against your own data structures
**The cost:** Silent failures, None propagation, "KeyError in production"
**The fix:** Pydantic models that guarantee structure at construction

#### try_except_violations
**What it means:** Using exceptions for control flow instead of type dispatch
**The cost:** Hidden execution paths, performance overhead, unclear intent
**The fix:** Result types or discriminated unions for explicit paths

#### any_type_usage
**What it means:** You've given up on type safety (Any = "I don't know")
**The cost:** Every Any is a runtime error waiting to happen
**The fix:** Use Union types or proper domain models

#### enum_value_unwrapping
**What it means:** Calling .value defeats the entire purpose of enums
**The cost:** Losing type safety, string comparisons creep back in
**The fix:** StrEnum auto-converts, methods on enum handle behavior

### Positive Patterns (What Good Looks Like)

#### Core SDA patterns - business logic in types
- **pydantic_models** - BaseModel classes encoding domain rules
- **behavioral_enums** - Enums with methods and computed properties
- **computed_fields** - @computed_field properties instead of functions
- **validators** - Pydantic field and model validators
- **protocols** - typing.Protocol interfaces for clean contracts
- **type_dispatch_tables** - Dictionary-based conditional elimination

## 🎓 Learning Opportunities

### For Junior Developers
- **AST Fundamentals** - How Python represents code as structured data
- **Visitor Pattern** - How to traverse and analyze tree structures
- **Type System Usage** - Leveraging Python's type hints for architecture

### For Senior Developers
- **Domain Modeling** - Encoding business rules in types vs procedural code
- **Architectural Analysis** - Static analysis techniques for codebase assessment
- **Type-Driven Development** - Pushing logic into the type system

### The Mental Model Shift

The hardest part isn't learning the patterns - it's unlearning the procedural habits. When you stop asking "how do I check this?" and start asking "how do I make this impossible?", you've made the shift.

## 🤔 "But What About..."

### "This looks like overengineering"
Show them the two-line `send_notification` function. Ask them to count the lines in their current notification code. Overengineering is 15 classes doing what one smart model could do.

### "My team won't understand this"
Your team already doesn't understand the current code. At least SDA models explain themselves through their types and methods. A `PaymentStatus` enum with a `can_refund()` method is self-documenting.

### "We don't have time to refactor"
You don't have time NOT to. Track how much time you spent last sprint on:
- Bugs that SDA makes impossible (wrong type, invalid state)
- Understanding existing code (scattered logic)
- Defensive programming that didn't defend anything

### "Our codebase is too complex for this"
Complex codebases need SDA most. Complexity × conditionals = exponential confusion. Complexity + types = manageable domains.

### "What about performance?"
Pydantic v2 is written in Rust. Your performance bottleneck is not type validation, it's your database queries and network calls. Profile first, assume never.

## 🤝 Philosophy

### Why No Scoring?

Traditional linters give you scores like "73/100" or grades like "B+". This approach has problems:

- **Context Blindness** - A Redis client legitimately needs different patterns than a domain model
- **Gaming Incentives** - Teams chase scores instead of understanding principles
- **Prescriptive Bias** - Tools impose their author's opinions about "good" code

### Observer Pattern Instead

SDA Detector reports **what exists** and lets you decide what it means:

- **"91.2% patterns, 8.8% violations"** - Factual distribution
- **"MODULE TYPE: infrastructure"** - Context classification
- **"13 computed fields detected"** - Architectural sophistication measurement

You interpret these facts based on your context, goals, and constraints.

### When NOT to Use SDA

Be honest about boundaries:

- **Simple Scripts** - 50-line utilities don't need architecture
- **Pure I/O Boundaries** - Database drivers, API clients need different patterns
- **Performance-Critical Loops** - Sometimes you need that ugly optimization
- **Learning Projects** - Don't learn SDA and Python at the same time

## 🛠️ Development

### VS Code Setup

```bash
# Initialize the project (creates .venv automatically)
make setup

# VS Code should auto-detect: .venv/bin/python
# If not, use Ctrl+Shift+P -> "Python: Select Interpreter" -> ".venv/bin/python"
```

### Running Tests

```bash
# Self-analysis (dogfooding)
make self-analyze

# Or run on any file
make run FILE=path/to/your/file.py

# Expected output: ~85% patterns, ~15% violations for tooling module
# The detector practices what it preaches! 🔍
```

### Using SDA in Your Team

#### Start With New Code
- Don't refactor everything at once
- Apply SDA patterns to new features
- Let the old code look bad in comparison

#### The Gateway Drug: Enums with Methods
Start here - it's easy to understand and has immediate value:
```python
class OrderStatus(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"

    def can_cancel(self) -> bool:
        return self == OrderStatus.PENDING
```

#### Code Review Checklist
- [ ] Could this if/elif be an enum dispatch?
- [ ] Could this dict be a Pydantic model?
- [ ] Could this validation live in the type?
- [ ] Could this service method be a model method?
- [ ] Is this isinstance check necessary?

## 📄 License

[MIT License](LICENSE) – feel free to use this in your projects, educational materials, or as inspiration for your own architectural analysis tools.

## 🎯 Why SDA Detector Matters

SDA Detector is more than just a code analyzer - it's a **living demonstration** of what happens when you push Python's type system to its limits. It shows that Python can achieve the same type-driven elegance typically associated with Haskell or Rust.

But more importantly, it's about remembering what we forgot. That objects can have behavior. That types can encode business rules. That we can write code where bugs are impossible rather than unlikely.

**The detector doesn't just analyze code for SDA patterns - it proves they work by using them itself.**

Every conditional eliminated is a bug that can't happen. Every type that knows its business is a 3am debugging session avoided. Every model that teaches you the domain is documentation that can't lie.

This is software by subtraction. And it works. 🪞✨
