# SDA RULES QUICK REFERENCE

## 🚨 ZERO TOLERANCE VIOLATIONS (INSTANT BAN)
```python
# ❌ BANNED - NO EXCEPTIONS
isinstance(obj, Type)           # → Use discriminated unions
hasattr(obj, 'attr')           # → Use discriminated unions
getattr(obj, 'attr', default)  # → Use discriminated unions (except AST boundaries)
if condition:                   # → Use StrEnum with dispatch
elif condition:                 # → Use StrEnum with dispatch
match obj:                      # → Use discriminated unions
try/except for control:         # → Use Result types
cast(Type, value)              # → Use constructive transformation
type: ignore                    # → Only with SDA: justification
Any                            # → Use specific types or unions
"string_literal"               # → Use StrEnum for domain concepts
```

## ✅ REQUIRED PATTERNS

### 1. DISCRIMINATED UNIONS FOR ALL BRANCHING
```python
# ✅ CORRECT: StrEnum with behavioral methods
class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    def process(self) -> Result:
        processors = {
            Status.ACTIVE: self._process_active,
            Status.INACTIVE: self._process_inactive
        }
        return processors[self]()

# ✅ CORRECT: Pydantic discriminated union
class ActiveState(BaseModel):
    type: Literal["active"]
    data: ActiveData

class InactiveState(BaseModel):
    type: Literal["inactive"]
    reason: str

State = Annotated[Union[ActiveState, InactiveState], Field(discriminator="type")]
```

### 2. CONSTRUCTIVE TRANSFORMATION
```python
# ✅ CORRECT: Unpack, transform, reconstruct
def to_domain(raw: dict) -> DomainModel:
    # 1. Unpack components
    id_raw = raw.get("id")
    value_raw = raw.get("value")

    # 2. Transform to domain types
    domain_id = DomainId(id_raw) if id_raw else DomainId.anonymous()
    domain_value = Value.from_raw(value_raw)

    # 3. Reconstruct (construction IS validation)
    return DomainModel(id=domain_id, value=domain_value)
```

### 3. RESULT TYPES INSTEAD OF EXCEPTIONS
```python
# ✅ CORRECT: Result enum
class FileResult(StrEnum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    PERMISSION_ERROR = "permission_error"

    def to_findings(self, path: Path) -> list[Finding]:
        handlers = {
            FileResult.SUCCESS: lambda: [],
            FileResult.NOT_FOUND: lambda: [Finding.file_not_found(path)],
            FileResult.PERMISSION_ERROR: lambda: [Finding.permission_denied(path)]
        }
        return handlers[self]()
```

### 4. PURE DICTIONARY/TUPLE DISPATCH
```python
# ✅ CORRECT: Tuple-based classification
@computed_field
@property
def classification(self) -> PatternType:
    """Pure tuple dispatch for pattern classification."""
    pattern_map = {
        (True, False, False): PatternType.TYPE_CHECK,
        (False, True, False): PatternType.MANUAL_JSON,
        (False, False, True): PatternType.PYDANTIC_PATTERN,
        (False, False, False): PatternType.UNKNOWN
    }

    key = (self.is_type_check, self.is_json_operation, self.is_pydantic_method)
    return pattern_map.get(key, PatternType.UNKNOWN)
```

### 5. BOUNDARY OPERATIONS (ONLY AT EXTERNAL INTERFACES)
```python
# ✅ ALLOWED: Only at AST/external boundaries with comment
func = getattr(node, 'func', None)  # Boundary operation - AST interface

# Dictionary dispatch including None as valid type
type_extractors: dict[type, Callable[[Any], str]] = {
    type(None): lambda f: "unknown",
    ast.Name: lambda f: getattr(f, 'id', 'unknown'),  # Boundary operation
    ast.Attribute: lambda f: getattr(f, 'attr', 'unknown')  # Boundary operation
}
```

## ARCHITECTURE PATTERNS

### Models (Domain Intelligence)
```python
class Order(BaseModel):
    items: list[OrderItem]
    status: OrderStatus

    model_config = {"frozen": True}  # ALWAYS frozen

    @computed_field  # Derived intelligence
    @property
    def total(self) -> Money:
        return sum_money([item.subtotal for item in self.items])

    def can_ship(self) -> bool:  # Business logic IN model
        return self.status == OrderStatus.PAID
```

### Services (Pure Orchestration)
```python
class OrderService:
    """NO business logic, NO conditionals, pure orchestration."""

    def process(self, order: Order) -> ProcessResult:
        # Let the model decide
        return order.process()  # Polymorphism handles dispatch
```

### Boundaries (Single Extraction)
```python
def extract_domain(external: dict) -> DomainModel:
    """One place to convert external → domain."""
    # Immediate conversion at boundary
    return DomainModel.from_external(external)
```

## VALIDATION COMMANDS
```bash
# Must pass
mypy --strict src/
ruff check src/
ruff format src/

# Must return empty
grep -r "isinstance\|hasattr\|getattr" src/ --include="*.py" | grep -v "# Boundary"
grep -r "if \|elif \|match " src/ --include="*.py" | grep -v "__name__"
```

## REMEMBER
- **Software by Subtraction**: Remove nonsense, don't add complexity
- **Data Drives Behavior**: Logic lives with data
- **Constructive Proof**: Build types, don't assert them
- **Discriminated Unions**: For ALL branching, no exceptions
- **Immutability**: Frozen models, explicit transitions
