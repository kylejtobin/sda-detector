# 🚨 SDA COMPLIANCE ENFORCER - ZERO TOLERANCE POLICY 🚨

## CRITICAL: YOU MUST ACTIVELY REVIEW ALL SDA RULES BEFORE ANY CODE ACTION

**DO NOT PROCEED WITHOUT READING THE FULL RULE DOCUMENTS. NO EXCEPTIONS.**

### MANDATORY RULE CONSULTATION (ZERO TOLERANCE)

🔥 **[Core SDA Principles](../.cursor/rules/000-sda-core.mdc)**
- **FUNDAMENTAL:** Software by Subtraction - Remove nonsense, don't add complexity
- **CONSTRUCTIVE PROOF:** Every type transition through explicit construction
- **LOCALITY OF BEHAVIOR:** Data drives behavior, logic lives with data
- **ZERO TOLERANCE:** NO isinstance, NO if/elif, NO cast, NO naked primitives

🔥 **[Anti-Patterns - What NOT to Do](../.cursor/rules/001-anti-patterns.mdc)**
- **BANNED CONSTRUCTS:** isinstance/hasattr/getattr with ZERO TOLERANCE
- **NO BOUNDARY EXCEPTIONS:** No "safe" wrappers, no legacy compatibility
- **INSTANT VIOLATIONS:** Runtime type checking, conditionals, type assertions
- **ENFORCEMENT:** Every violation is a bug waiting to happen

🔥 **[Type Dispatch & Discriminated Unions](../.cursor/rules/010-type-dispatch.mdc)**
- **ABSOLUTE LAW:** ALL branching logic MUST use discriminated unions
- **MANDATORY PATTERNS:** StrEnum behavioral methods, Pydantic discriminators
- **RESULT TYPES:** Replace exceptions with Result enums
- **GOLDEN RULE:** If you're writing `if`, stop and create a type instead

🔥 **[Domain Modeling with Pydantic](../.cursor/rules/020-domain-modeling.mdc)**
- **RICH TYPES:** Every domain concept gets a type - no naked primitives
- **IMMUTABILITY:** All models frozen by default
- **COMPUTED FIELDS:** For derived intelligence, not constants
- **DISCRIMINATED UNIONS:** Different states = different types

🔥 **[Boundary Intelligence](../.cursor/rules/030-boundaries.mdc)**
- **SINGLE EXTRACTION:** One place per external system type
- **IMMEDIATE CONVERSION:** External → Domain at boundary
- **PURE FUNCTIONS:** No side effects in transformation
- **TYPE SYSTEM PRINCIPLE:** Trust discriminated unions over type checkers

🔥 **[Service Architecture](../.cursor/rules/040-services.mdc)**
- **ORCHESTRATION ONLY:** Services orchestrate, models decide
- **STATELESS:** No business logic, no conditionals
- **DEPENDENCY INJECTION:** Use Protocols for external dependencies
- **PURE LOOKUP:** Dictionary dispatch for service access

🔥 **[Python Standards](../.cursor/rules/050-python-standards.mdc)**
- **TYPE SAFETY:** mypy --strict MUST pass, Any type BANNED
- **MODERN PYTHON:** 3.13+ syntax, union types with |
- **PACKAGE MANAGEMENT:** uv add for dependencies
- **ZERO TOLERANCE:** No cast(), no type: ignore without justification

🔥 **[Testing Philosophy](../.cursor/rules/060-testing.mdc)**
- **TEST INTELLIGENCE:** Test domain behavior, trust Pydantic
- **DON'T TEST PLUMBING:** Skip validation, frozen, type system
- **REAL MODELS:** No mocking domain models
- **ONE CONCEPT:** Each test validates one behavior

## VALIDATION PROTOCOL (MANDATORY)

**BEFORE ANY CODE CHANGES - NO EXCEPTIONS:**
1. **READ THE RELEVANT SDA RULE DOCUMENTS ACTIVELY**
2. **IDENTIFY ALL POTENTIAL VIOLATIONS IN EXISTING CODE**
3. **DESIGN DISCRIMINATED UNION REPLACEMENTS FIRST**
4. **IMPLEMENT WITH PURE ENUM BEHAVIORAL DISPATCH**
5. **VALIDATE WITH COMMANDS BELOW**

## ENFORCEMENT COMMANDS (MUST RUN)
```bash
# MANDATORY - MUST PASS
mypy --strict  # Type checking - NON-NEGOTIABLE
ruff check    # Linting - MUST BE CLEAN
ruff format   # Formatting - MUST BE APPLIED

# ZERO TOLERANCE VALIDATION
# Check for BANNED constructs:
grep -r "isinstance" . --include="*.py"  # MUST RETURN EMPTY (except boundaries with justification)
grep -r "hasattr" . --include="*.py"     # MUST RETURN EMPTY (except boundaries with justification)
grep -r "getattr" . --include="*.py"     # MUST RETURN EMPTY (except boundaries with justification)
grep -r "if " . --include="*.py" | grep -v "__name__"  # REVIEW ALL CONDITIONALS
```

## SDA TRANSFORMATION MANDATES

**EVERY VIOLATION MUST BE REPLACED:**
- **isinstance → Discriminated union with Literal discriminator**
- **if/elif chains → StrEnum behavioral methods with dispatch dict**
- **try/except control → Result enum with to_findings() methods**
- **match/case → Discriminated union with type dispatch**
- **Optional fields → Discriminated union types with state intelligence**
- **Primitive obsession → Value objects with @computed_field**
- **String literals → StrEnum with behavioral methods**
- **cast() → Constructive transformation (unpack, transform, reconstruct)**

## CONSTRUCTIVE PROOF PATTERN (HEART OF SDA)
```python
# ✅ REQUIRED: Constructive transformation
def to_domain(raw: dict) -> DomainModel:
    # Step 1: Unpack components explicitly
    id_raw = raw.get("id")
    value_raw = raw.get("value")

    # Step 2: Transform individually to domain types
    domain_id = DomainId(id_raw) if id_raw else DomainId.anonymous()
    domain_value = Value.from_raw(value_raw)

    # Step 3: Reconstruct target type (construction IS validation)
    return DomainModel(id=domain_id, value=domain_value)
```

## COMPLIANCE VERIFICATION

**YOU MUST VERIFY ZERO VIOLATIONS:**
- ❌ **BANNED:** Any isinstance, hasattr, getattr usage
- ❌ **BANNED:** Any if/elif chains for business logic
- ❌ **BANNED:** Any match/case statements
- ❌ **BANNED:** Any try/except for control flow
- ❌ **BANNED:** Any cast() or type assertions
- ❌ **BANNED:** Any naked primitives with domain meaning
- ❌ **BANNED:** Any business logic in services
- ✅ **REQUIRED:** Pure discriminated union dispatch everywhere
- ✅ **REQUIRED:** StrEnum behavioral methods for all choices
- ✅ **REQUIRED:** Immutable models with model_copy updates
- ✅ **REQUIRED:** Constructive transformation at boundaries

## SOPHISTICATED SIMPLICITY PATTERNS (LEARNED)

**When Type System Challenges Arise:**
1. **Trust discriminated unions over type checkers** - Domain models encode more intelligence than MyPy can verify
2. **Use type(None) as dictionary key** - None is a valid type for pure dispatch
3. **Boundary operations marked explicitly** - getattr allowed ONLY at AST boundaries with comment
4. **Type ignore LAST RESORT** - Only with detailed justification explaining domain guarantees

**FAILURE TO COMPLY = IMMEDIATE CODE REJECTION**

## REMEMBER: SOFTWARE BY SUBTRACTION
- Remove architectural nonsense
- Data drives behavior
- Business logic lives with data
- Every violation removed makes the system more powerful

**READ THE RULES. ENFORCE THE PATTERNS. NO COMPROMISES.**
