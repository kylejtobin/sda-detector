# 🧠 SDA Detector

**A Python AST analyzer that detects Semantic Domain Architecture patterns**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![Code style: SDA](https://img.shields.io/badge/code%20style-SDA-purple.svg)](https://github.com/kylejobin/sda-detector)
[![MIT License](https://img.shields.io/github/license/kylejobin/sda-detector)](LICENSE)

## 🎯 What is SDA Detector?

SDA Detector is an **objective observer tool** that analyzes Python codebases for Semantic Domain Architecture (SDA) patterns. It tells you what architectural patterns exist in your code **without judging them** - you decide what to do with that information.

The detector practices **eating your own dog food** - it demonstrates the very SDA principles it analyzes, making it both a practical tool and a learning resource.

### Core Principle: Pure Observation

This tool practices the **observer pattern** - it reports facts, not opinions. Instead of scoring your code as "good" or "bad," it provides neutral metrics like:

- **91.2% patterns, 8.8% violations** - Observable distribution
- **16 computed fields detected** - Type intelligence measurement
- **MODULE TYPE: domain** - Context classification
- **FILES ANALYZED: 12** - Scope coverage

## 🏗️ What is Semantic Domain Architecture?

SDA is an architectural philosophy built on one core principle: **data drives behavior**.

Instead of writing conditional logic that _checks_ data, you create types where data _selects_ behavior automatically. This fundamental shift transforms how you think about code:

- **Pydantic models that encode domain rules** - Instead of `validate_email(string)`, create `Email(BaseModel)` that validates itself
- **Enums with behavior instead of string literals** - Instead of `if status == "active"`, use `status.can_process_payment()`
- **Computed fields instead of functions** - Instead of `calculate_total(order)`, use `order.total` as a computed property
- **Type dispatch instead of if/else chains** - Instead of `if type == "A": do_a()`, use `handlers[type]()`
- **Protocols for interface contracts** - Define what you need from dependencies, not concrete implementations

The goal is to make your data so intelligent that it knows what to do with itself. When you achieve this, conditional logic largely disappears because the types handle decision-making through their structure and relationships.

## 🚀 Quick Start

### Installation

```bash
# Requires Python 3.12+ and Pydantic v2
pip install pydantic
```

### Basic Usage

```bash
# Analyze a single file
python sda_detector.py my_module.py

# Analyze a directory
python sda_detector.py src/domain/

# Analyze with custom name
python sda_detector.py src/models/ "User Domain Models"
```

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
  enum_value_unwrapping       1 🔍
    → my_module.py:89 - enum value unwrapping - consider StrEnum for automatic conversion, or validate if external serialization is needed instead of Status.ACTIVE.value
  anemic_services             1 🔍
    → my_module.py:156 - anemic service - 5 utility-style method names, 12 methods (high cohesion risk) - consider domain model methods or focused services

📊 ARCHITECTURAL FEATURES:
  pydantic_models             5 📊
    → my_module.py:12 - BaseModel: User
    → my_module.py:34 - BaseModel: Order
  computed_fields             8 📊
    → my_module.py:18 - @computed_field total_cost
    → my_module.py:29 - @computed_field full_name

MODULE TYPE: domain
FILES ANALYZED: 1
TOTAL VIOLATIONS: 7
TOTAL PATTERNS: 23
DISTRIBUTION: 76.7% patterns, 23.3% violations
```

## 📚 Educational Features

### Learn AST Analysis

The detector includes comprehensive educational documentation about Python's Abstract Syntax Tree:

```python
## How AST Visitors Work (Junior Dev Tutorial)

When you call `detector.visit(tree)`, Python automatically walks through
every node in the syntax tree and calls the appropriate visit method:

- `visit_ClassDef()` for class definitions: `class MyClass(BaseModel): ...`
- `visit_FunctionDef()` for function definitions: `def my_function(): ...`
- `visit_Call()` for function calls: `isinstance(obj, str)`
- `visit_If()` for if statements: `if condition: ...`
- `visit_Try()` for try/except blocks: `try: ... except: ...`
- `visit_Attribute()` for attribute access: `obj.attr` and `Enum.VALUE.value`
```

### Before/After Code Examples

See how SDA transforms procedural code into type-driven patterns:

#### Enum Value Unwrapping Detection

The detector identifies primitive obsession with enum values while acknowledging valid serialization needs:

```python
# ❌ Primitive obsession (detected violation)
queue = QueueType.STORAGE_PROCESSING.value
status = OrderStatus.PENDING.value

# ✅ Rich domain types (SDA pattern)
queue = QueueType.STORAGE_PROCESSING  # StrEnum used directly
status = OrderStatus.PENDING  # Type intelligence preserved

# ✅ Valid external serialization (when necessary)
api_payload = {"status": OrderStatus.PENDING.value}  # External API requirement
db_record = (order.id, order.status.value)  # Legacy database format
```

The detector message: _"consider StrEnum for automatic conversion, or validate if external serialization is needed"_ encourages developers to:

1. **Use StrEnum** for automatic string conversion in most cases
2. **Validate necessity** when `.value` is truly needed for external systems
3. **Question primitive obsession** in domain logic

#### Anemic Services Detection

The detector identifies services that are just "bags of functions" with no real cohesion:

```python
# ❌ Anemic service (detected violation)
class OrderService:
    @staticmethod
    def create_order(data): pass

    @staticmethod
    def update_order(id, data): pass

    @staticmethod
    def delete_order(id): pass

    @staticmethod
    def get_order(id): pass

    @staticmethod
    def validate_order(order): pass

    @staticmethod
    def format_order(order): pass

    @staticmethod
    def parse_order_data(raw): pass

    @staticmethod
    def transform_order(order): pass
    # ... 12+ utility methods with no shared state

# ✅ Rich domain model approach (SDA pattern)
class Order(BaseModel):
    id: OrderId
    status: OrderStatus
    items: list[LineItem]

    def place(self) -> "Order":
        # Domain logic in the model
        if not self.can_be_placed:
            raise ValueError("Order cannot be placed")
        return self.model_copy(update={"status": OrderStatus.PLACED})

    def add_item(self, item: LineItem) -> "Order":
        return self.model_copy(update={"items": self.items + [item]})

# ✅ Focused service (SDA pattern)
class OrderRepository:
    def __init__(self, db: Database):
        self.db = db  # Real state and dependencies

    async def save(self, order: Order) -> None:
        # Focused responsibility: persistence
        await self.db.execute(order.to_sql())
```

Detection criteria:

- **High static method ratio** (70%+ suggests no shared state)
- **Utility method names** (get*, create*, update*, parse*, etc.)
- **Too many methods** (8+ suggests multiple responsibilities)

#### Boolean Coercion Array Indexing - SDA's Purest Teaching Moment

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

**The broader SDA pattern:** Every piece of the detector demonstrates "data drives behavior":

- `ModuleClassifier` returns data that drives analysis rules
- `AnalysisContext` computes its own behavior from its state
- `Finding` knows how to format itself
- Report formatting uses dispatch tables

Boolean coercion is just this principle in its most **naked, undeniable form**.

### Living Documentation

The detector itself follows SDA principles, so reading its source code teaches you:

- **How to eliminate if/else chains** with type dispatch tables and boolean coercion
- **How to use computed fields** for domain logic instead of separate functions
- **How to create immutable domain models** with Pydantic that know their own behavior
- **How to implement the visitor pattern** for AST analysis using data-driven decisions
- **How to achieve "data drives behavior"** in its purest form through patterns like boolean coercion

Every class demonstrates the core principle: instead of checking what the data is, the data tells you what to do. The detector is both a tool and a masterclass in thinking with types instead of conditions.

## 🔍 What Does It Detect?

### SDA Violations (Anti-patterns)

#### Core SDA violations - logic that should be in the type system

- **business_conditionals** - if/elif chains that should be type dispatch
- **isinstance_violations** - Runtime type checking instead of protocols
- **hasattr_violations** - Attribute existence checks instead of typed models
- **getattr_violations** - Dynamic attribute access instead of domain models
- **dict_get_violations** - dict.get() instead of Pydantic models
- **try_except_violations** - Exception handling for control flow

#### Type system violations - missing type information

- **any_type_usage** - Using Any type annotation instead of specific types
- **missing_field_constraints** - Fields without validation rules
- **primitive_obsession** - Raw str/int instead of value objects
- **enum_value_unwrapping** - .value calls on StrEnum/Enum (primitive obsession)
- **missing_model_config** - No model configuration specified
- **no_forward_refs** - Missing forward references in self-referential types
- **manual_validation** - Hand-written validation instead of Pydantic
- **anemic_services** - Services that are just bags of stateless functions

### Positive Patterns (SDA-aligned)

#### Core SDA patterns - business logic in types

- **pydantic_models** - BaseModel classes encoding domain rules
- **behavioral_enums** - Enums with methods and computed properties
- **computed_fields** - @computed_field properties instead of functions
- **validators** - Pydantic field and model validators
- **protocols** - typing.Protocol interfaces for clean contracts
- **type_dispatch_tables** - Dictionary-based conditional elimination

#### Pydantic integration patterns

- **pydantic_validation** - model_validate\* calls for type safety
- **pydantic_serialization** - model_dump\* calls for data output
- **immutable_updates** - model_copy() for state changes
- **field_constraints** - Field() usage with validation rules
- **model_config_usage** - ModelConfig definitions for behavior control

#### Advanced type system patterns

- **union_types** - Union type annotations for flexible typing
- **literal_types** - Literal type annotations for exact values
- **discriminated_unions** - Tagged union patterns for state machines
- **forward_references** - Self-referential types for recursive structures
- **annotated_types** - Annotated type hints with metadata
- **generic_models** - Generic Pydantic models for reusability
- **recursive_models** - Self-referential models for tree structures

#### Pydantic advanced features

- **custom_validators** - @field_validator, @model_validator for complex rules
- **custom_serializers** - @field_serializer for output formatting
- **root_validators** - @root_validator (legacy) for model-level validation

#### Code organization patterns

- **enum_methods** - Methods on enum classes for behavior
- **boundary_conditions** - Proper error handling at system boundaries
- **type_checking_imports** - TYPE_CHECKING blocks for import optimization

## 🏗️ Architecture

The detector demonstrates SDA principles in its own design:

```
sda_detector.py
├── Configuration Types (ModuleType, ModuleClassifier)
├── Domain Types (ViolationType, PositivePattern)
├── Data Models (Finding, ArchitectureReport)
├── AST Analysis (NodeAnalyzer, SDAArchitectureDetector)
├── Display Models (DisplayConfig, ReportFormatter)
└── Pure Functions (analyze_module, print_report)
```

### Key Design Patterns

- **Immutable Models** - All domain objects use `frozen=True`
- **Computed Intelligence** - Business logic in computed fields, not functions
- **Type Safety** - Enums and protocols instead of string literals
- **Boundary Awareness** - Context-sensitive analysis for infrastructure vs domain code
- **Pure Observation** - Reports facts without prescriptive scoring

## 🎓 Learning Opportunities

### For Junior Developers

- **AST Fundamentals** - How Python represents code as structured data
- **Visitor Pattern** - How to traverse and analyze tree structures
- **Functional Programming** - List comprehensions, generator expressions, boolean coercion
- **Type System Usage** - Leveraging Python's type hints for architecture

### For Senior Developers

- **Domain Modeling** - Encoding business rules in types vs procedural code
- **Architectural Analysis** - Static analysis techniques for codebase assessment
- **Type-Driven Development** - Pushing logic into the type system
- **Observer vs Prescriber** - Building tools that inform rather than judge

## 🔧 Advanced Usage

### Module Classification

The detector automatically classifies modules by analyzing file paths:

- **DOMAIN** - Pure business logic (`domain`, `model`, `entity`, `value`, `service`, `business`)
- **INFRASTRUCTURE** - Boundary code (`redis`, `storage`, `client`, `external`, `infra`, `db`, `database`)
- **TOOLING** - Development tools (`detector`, `parser`, `analyzer`, `ast`, `visitor`, `scanner`, `lexer`)
- **FRAMEWORK** - Third-party integration (`dagster`, `fastapi`, `sqlalchemy`, `neo4j`, `pydantic`, `pytest`)
- **MIXED** - Combination of concerns

### Context-Aware Analysis

Different module types get appropriate analysis:

- **Domain modules** - Strict pattern enforcement, minimal boundary exceptions
- **Infrastructure modules** - Lenient on `hasattr()`, `try/except` for external APIs
- **Tooling modules** - Accepts necessary reflection and file system operations

### Observational Metrics

Pure facts without judgment:

- **Pattern Distribution** - Percentage of type-driven vs procedural patterns
- **File Coverage** - How many files were analyzed
- **Pattern Diversity** - Variety of architectural techniques used
- **Module Classification** - What type of code this appears to be

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

## 📖 Further Reading

### SDA Resources

- [Pydantic Documentation](https://docs.pydantic.dev/) - The foundation of SDA
- [Python AST Module](https://docs.python.org/3/library/ast.html) - Understanding syntax trees
- [Type-Driven Development](https://blog.ploeh.dk/2015/08/10/type-driven-development/) - Philosophy overview

### Related Concepts

- **Domain-Driven Design** - Business logic organization
- **Functional Programming** - Conditional elimination techniques
- **Static Analysis** - Code understanding without execution
- **Architecture Decision Records** - Documenting architectural choices

## 🛠️ Development

### Running Tests

```bash
# Self-analysis (dogfooding)
python sda_detector.py sda_detector.py

# Expected output: ~79% patterns, ~21% violations for tooling module
# The detector even catches its own enum .value violations! 🔍
```

### Code Style

The detector follows its own principles:

- Uses Pydantic models instead of dictionaries
- Employs computed fields instead of separate functions
- Leverages type dispatch instead of if/elif chains
- Maintains immutable state with model_copy()

### Contributing

When contributing, remember the core philosophy:

- **Observe, don't prescribe** - Add metrics, not judgments
- **Teach through code** - Include educational documentation
- **Practice SDA** - Use the patterns we're detecting
- **Stay focused** - Resist feature creep that dilutes the core purpose

### Recent Enhancements

- **Enum Value Unwrapping Detection** - Added `visit_Attribute()` to catch `.value` calls on StrEnum/Enum, promoting the SDA principle: "Build enums that ARE their values, not enums that HAVE values". Messages now acknowledge valid serialization needs while encouraging StrEnum usage.

- **Anemic Services Detection** - Added analysis for services that are just "bags of functions" with no cohesion. Detects high static method ratios, utility naming patterns, and excessive method counts that suggest missing domain models or unfocused responsibilities.

## 📄 License

[MIT License](LICENSE) – feel free to use this in your projects, educational materials, or as inspiration for your own architectural analysis tools.

## 🎯 Conclusion

SDA Detector is more than just a code analyzer - it's an **educational artifact** that demonstrates advanced Python techniques while providing practical architectural insights.

Whether you're learning about AST analysis, exploring type-driven development, or assessing your codebase's architectural patterns, this tool provides objective data to inform your decisions.

**The detector holds up a mirror to your code without fogging it with opinions.** 🪞✨
