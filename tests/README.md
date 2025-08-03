# SDA Testing Philosophy: "Test the Domain Intelligence, Trust Pydantic for the Rest"

## The F1 Car Principle

SDA has **sophisticated simplicity** - like a Formula 1 engine. Incredibly sophisticated engineering that produces elegant, predictable behavior.

Traditional enterprise has **chaotic simplicity** - like duct-taping lawn mower engines together. Each piece looks simple, but the interactions are unpredictable hell.

**We'd rather debug one sophisticated model with clear rules than hunt through 15 "simple" classes where the business logic is playing hide-and-seek.**

## Core Testing Principles

### 1. Intelligence Concentration Principle
- SDA concentrates ALL business logic into models
- Therefore: Test coverage should mirror this concentration
- Test heavily where domain intelligence lives, test lightly where it doesn't

### 2. Trust the Type System Principle
- Pydantic handles validation, serialization, immutability
- Therefore: Don't test what the type system guarantees
- Test the decisions your domain makes, not the plumbing Pydantic provides

### 3. Domain-Driven Test Design Principle
- Tests themselves should follow SDA patterns
- Test cases are domain models with behavior
- Test intelligence should live in test models, not test functions

## What We DON'T Test (The Elegance)

SDA eliminates entire categories of tests that traditional enterprise apps require:

❌ **State Mutation Tests** - Frozen models with `model_copy()` = no mutable state to test
❌ **Validation Logic Tests** - Pydantic Field constraints handle this declaratively
❌ **Data Transformation Tests** - Computed fields and model serialization handle this automatically
❌ **Integration Orchestration Tests** - Services only orchestrate, models decide = minimal coordination complexity

**Result**: ~60-70% fewer tests because we can't have invalid state transitions, runtime validation errors, or data integrity violations.

## The Testing Hierarchy (By Value)

### Tier 1: Critical Domain Intelligence (Must Test)
```python
@computed_field
@property
def can_be_cancelled(self) -> bool:
    # THIS is where business bugs hide in SDA
    return self.status in [OrderStatus.DRAFT, OrderStatus.PENDING]
```

**Where's the cancellation logic?**
```python
order.can_be_cancelled  # RIGHT FUCKING HERE
```

### Tier 2: Enum State Machines (Must Test)
```python
class OrderStatus(StrEnum):
    DRAFT = "draft"
    PAID = "paid"

    def can_transition_to(self, target: "OrderStatus") -> bool:
        # State transitions ARE the business logic
        return target in self._allowed_transitions[self]
```

### Tier 3: Protocol Contracts (Verify Architecture)
```python
# Ensure concrete implementations satisfy interfaces
assert isinstance(DetectionService(), CodeAnalyzer)
```

### Tier 4: Integration Reality (End-to-End Confidence)
```python
# Test against real code samples with known patterns
def test_detector_finds_known_patterns():
    report = analyze_module("fixtures/manual_json_usage.py")
    assert report.violations[ViolationType.MANUAL_JSON_SERIALIZATION]
```

### Tier 5: Service Orchestration (Light Touch)
```python
# Services are thin - just verify they coordinate correctly
def test_detection_service_orchestration():
    service = DetectionService()
    report = service.analyze_module("test.py", "test")
    assert isinstance(report, ArchitectureReport)
```

## The SDA Test Model Pattern (Dogfooding)

```python
class ViolationTestCase(BaseModel):
    """A test case that knows how to validate itself"""
    model_config = ConfigDict(frozen=True)

    name: str
    code_sample: str
    expected_violations: list[ViolationType]
    expected_patterns: list[PositivePattern]

    @computed_field
    @property
    def should_detect_manual_json(self) -> bool:
        return ViolationType.MANUAL_JSON_SERIALIZATION in self.expected_violations

    def verify_against(self, report: ArchitectureReport) -> TestResult:
        """The test case validates itself against reality"""
        violations_match = all(
            len(report.violations[v]) > 0 for v in self.expected_violations
        )
        patterns_match = all(
            len(report.patterns[p]) > 0 for p in self.expected_patterns
        )

        return TestResult(
            passed=violations_match and patterns_match,
            case=self,
            actual_report=report
        )
```

## SDA vs Traditional Complexity

### What's WORSE About Traditional Enterprise Architecture?

**1. Diffused Complexity**
- Business logic scattered across services, validators, transformers, mappers, handlers, processors
- Good luck finding where "can this order be cancelled?" is actually decided
- Change one rule? Touch 8 files and hope you found them all

**2. Runtime Terror**
- `NullPointerException` at 2 AM because someone passed `null`
- Invalid state mutations because "we forgot to check that case"
- Data integrity violations because validation was in the wrong layer

**3. Ceremony Complexity**
- 47 unit tests for a single business rule spread across multiple classes
- Mock hell - mocking mocks that mock other mocks
- Integration tests that test framework plumbing instead of business logic

### What's BETTER About SDA Complexity?

**1. Predictable Location**
```python
# Where's the cancellation logic?
order.can_be_cancelled  # RIGHT FUCKING HERE
```

**2. Impossible States**
```python
# Can this order be in an invalid state?
# NO. Pydantic prevents it at construction time.
```

**3. Type-Driven Discovery**
```python
# What can I do with an OrderStatus?
status.  # IDE shows you all the methods - they're RIGHT ON THE ENUM
```

## The Quality Pressure

**Domain Modeling Discipline** - SDA forces you to actually understand your business domain well enough to encode it properly.

Traditional enterprise apps let you be lazy - just throw everything in services and figure it out later. SDA forces you to think clearly about what your domain actually IS.

That's not complexity - that's **quality pressure**.

## Our Testing Mantra

> **"Test where intelligence lives, trust where types rule."**

We test business decisions, enum transitions, computed logic, and domain rules. We trust Pydantic for validation, serialization, immutability, and type safety.

**The goal**: High-confidence, low-ceremony testing that focuses on actual business value rather than infrastructure concerns.

**Bottom line**: SDA complexity is **concentrated, intentional, and discoverable**. Traditional complexity is **diffused, accidental, and hidden**.

## SDA Detector Testing Example

```python
# Test the actual domain intelligence
def test_analysis_context_boundary_detection():
    context = AnalysisContext(current_file="redis_client.py")
    assert context.is_boundary_context  # This computed field logic matters

def test_finding_location_formatting():
    finding = Finding(file_path="test.py", line_number=42, description="test")
    assert finding.location == "test.py:42"  # Computed field behavior

def test_violation_type_classification():
    # Test that our domain understanding is correct
    assert ViolationType.ISINSTANCE_VIOLATIONS # We know this is a violation
    assert PositivePattern.COMPUTED_FIELDS     # We know this is positive
```

**We don't test** Pydantic's validation, Field constraints, model serialization, or frozen model immutability. We **do test** the business intelligence we've encoded into our domain models.

## SDA Detector Component Analysis & Test Structure

### Our SDA Components (What We Actually Have)

**Domain Models** (`models.py`):
- `ViolationType` & `PositivePattern` (Behavioral Enums)
- `Finding` (Value Object with computed location)
- `AnalysisContext` (Smart Context with computed boundary detection)
- `ArchitectureReport` (Aggregate with computed metrics)
- `ModuleType` (Classification Enum)
- `DisplayConfig` & `ReportFormatter` (Presentation Models)

**Protocols** (`protocols.py`):
- Interface contracts for dependency injection

**Services** (`services.py`):
- `DetectionService` (Orchestrator)
- `SDAArchitectureDetector` (AST Visitor)
- `ModuleClassifier` (Classification Logic)
- `NodeAnalyzer` (AST Utilities)

### SDA-Aligned Test Structure

```
tests/
├── README.md                     # Testing philosophy (✅ already there)
├── fixtures/                     # Code samples for integration tests
│   ├── violations/               # Known anti-patterns
│   │   ├── manual_json.py       # json.dumps/loads usage
│   │   ├── anemic_service.py    # Bag-of-functions services
│   │   ├── isinstance_heavy.py  # Runtime type checks
│   │   └── enum_unwrapping.py   # .value primitive obsession
│   ├── patterns/                # Known SDA patterns
│   │   ├── rich_domain.py       # Computed fields, behavioral enums
│   │   ├── protocols.py         # Interface usage
│   │   └── type_dispatch.py     # Conditional elimination
│   └── mixed/                   # Real-world examples
│       ├── boundary_code.py     # Infrastructure patterns
│       └── domain_code.py       # Pure domain logic
├── domain/                      # Test the domain intelligence
│   ├── test_finding_intelligence.py
│   ├── test_context_intelligence.py
│   ├── test_report_intelligence.py
│   └── test_enum_behavior.py
├── integration/                 # End-to-end reality tests
│   ├── test_violation_detection.py
│   ├── test_pattern_detection.py
│   └── test_module_classification.py
├── contracts/                   # Protocol compliance tests
│   └── test_protocol_contracts.py
├── orchestration/              # Light service tests
│   └── test_service_coordination.py
└── shared/                     # Test domain models
    ├── test_models.py          # SDA test case models
    └── test_fixtures.py        # Shared test utilities
```

### SDA Component → Test Type Mapping

**1. Behavioral Enums → Behavior Tests**
```python
# Test ViolationType & PositivePattern enum intelligence
def test_violation_type_knows_its_nature():
    assert ViolationType.ISINSTANCE_VIOLATIONS.is_runtime_check
    assert ViolationType.MANUAL_JSON_SERIALIZATION.suggests_pydantic_alternative
```

**2. Value Objects → Computed Field Tests**
```python
# Test Finding.location computed field
def test_finding_formats_location():
    finding = Finding(file_path="src/test.py", line_number=42, description="test")
    assert finding.location == "src/test.py:42"
```

**3. Smart Context → Intelligence Tests**
```python
# Test AnalysisContext computed behavior
def test_context_detects_boundary_modules():
    context = AnalysisContext(current_file="redis_client.py")
    assert context.is_boundary_context  # Computed from file patterns
```

**4. Aggregates → Metrics Tests**
```python
# Test ArchitectureReport computed metrics
def test_report_calculates_distribution():
    report = ArchitectureReport(violations={...}, patterns={...})
    assert report.pattern_distribution["patterns"] > 0.8  # Computed percentage
```

**5. Services → Orchestration Tests**
```python
# Light touch - just verify coordination
def test_detection_service_orchestrates():
    service = DetectionService()
    report = service.analyze_module("fixtures/violations/manual_json.py", "test")
    assert isinstance(report, ArchitectureReport)
```

**6. Protocols → Contract Tests**
```python
# Verify implementations satisfy interfaces
def test_detection_service_implements_code_analyzer():
    assert isinstance(DetectionService(), CodeAnalyzer)
```

### Test Tooling Setup (SDA Style)

**PyTest Configuration** - But with SDA fixtures:
```python
# conftest.py
from sda_detector import ViolationType, PositivePattern

@pytest.fixture
def manual_json_fixture():
    return CodeFixture(
        name="manual_json_usage",
        content='import json\ndata = json.dumps({"test": "value"})',
        expected_violations=[ViolationType.MANUAL_JSON_SERIALIZATION],
        expected_patterns=[]
    )
```

**SDA Test Models** (Dogfooding):
```python
class CodeFixture(BaseModel):
    """A code sample that knows what it should detect"""
    model_config = ConfigDict(frozen=True)

    name: str
    content: str
    expected_violations: list[ViolationType]
    expected_patterns: list[PositivePattern]

    @computed_field
    @property
    def should_fail_analysis(self) -> bool:
        return len(self.expected_violations) > 0

    def verify_against(self, report: ArchitectureReport) -> TestResult:
        """The fixture validates itself against reality"""
        return TestResult(
            fixture=self,
            violations_found=self._check_violations(report),
            patterns_found=self._check_patterns(report)
        )
```

### What Makes This SDA Testing?

1. **Domain-Driven Test Structure** - Tests organized by domain concepts, not technical layers
2. **Test Models with Behavior** - Test cases are Pydantic models that know how to validate themselves
3. **Concentrated Intelligence Testing** - Focus on computed fields, enum behavior, domain logic
4. **Trust the Type System** - Don't test Pydantic's validation/serialization
5. **Reality-Based Integration** - Test against real code samples with known patterns

### The Tools We DON'T Need

❌ **Heavy mocking frameworks** - Services are too thin to need complex mocks
❌ **State mutation testing** - Frozen models prevent invalid states
❌ **Validation frameworks** - Pydantic handles this
❌ **Complex test orchestration** - Domain models test themselves

### The Tools We DO Need

✅ **PyTest** - For test discovery and execution
✅ **Fixtures as models** - Code samples with expected behaviors
✅ **Simple assertions** - Test the domain intelligence directly
✅ **Real code samples** - Integration tests against actual patterns

This structure reflects the SDA principle: **test where intelligence lives, trust where types rule**. Each component type gets tested according to where its business logic actually resides.
