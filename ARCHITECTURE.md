# SDA DETECTOR ARCHITECTURE

## Core Principle
Objective pattern detection. Domain models analyze themselves. Services orchestrate. Report facts, not judgments.

## File Structure
```
src/sda_detector/
├── __main__.py                     # CLI entry point
├── __init__.py                     # Public API exports
├── service.py                      # Pure orchestration (~250 lines)
└── models/
    ├── __init__.py                 # Essential exports only
    ├── core_types.py               # PatternType, PositivePattern, discriminated unions
    ├── analysis_domain.py          # Finding model
    ├── context_domain.py           # ScopeType, AnalysisScope, RichAnalysisContext
    ├── classification_domain.py    # ModuleClassifier
    ├── reporting_domain.py         # ArchitectureReport
    └── analyzers/
        ├── __init__.py
        ├── ast_utils.py            # Shared AST utilities
        ├── conditional_analyzer.py # Conditional pattern analysis (~170 lines)
        ├── call_analyzer.py        # Function call pattern analysis (~155 lines)
        └── attribute_analyzer.py   # Attribute access pattern analysis (~160 lines)
```

## Key Architectural Patterns

### Pure Discriminated Union Dispatch
Every branching decision uses discriminated unions with behavioral enums:
- `ASTNodeType` - Classifies AST nodes and dispatches to analyzers
- `FileResult/AnalysisResult` - Eliminates try/except control flow
- `PathType` - Handles file system operations without conditionals
- `ModuleTypeClassifier` - Module classification without if/elif chains
- `CLIArgumentState` - CLI argument handling with pure dispatch

### Behavioral Enums
All enums contain their own logic through methods:
- Classification methods (`from_ast()`, `from_path()`)
- Behavioral methods (`to_findings()`, `create_finding()`)
- Pure dictionary dispatch for all branching

### Domain Model Intelligence
Models analyze themselves through computed fields and methods:
- `Finding` knows its own pattern classification
- `ConditionalDomain` classifies its own pattern type
- `ArchitectureReport` generates its own statistics
- Context flows immutably through analysis

## Achievements

### 100% Discriminated Union Dispatch
- Eliminated ALL if/elif/else chains in core business logic
- Replaced with pure dictionary dispatch and behavioral enums
- Zero isinstance/hasattr usage (except marked AST boundaries)

### Modular Architecture
- Extracted 427-line monolithic ast_domain.py into focused analyzers
- Each analyzer: 150-170 lines of pure SDA code
- Service layer: Pure orchestration with discriminated unions
- Clean separation of concerns throughout

### Pattern Detection Capabilities

**Violations Detected:**
- `isinstance/hasattr/getattr` usage
- Business conditionals (if/elif chains)
- Try/except for control flow
- Enum `.value` unwrapping
- Manual JSON serialization
- Dict.get() usage
- Anemic services (limited)

**Positive Patterns Recognized:**
- Pydantic models and operations
- Behavioral enums with methods
- Computed fields
- Type dispatch tables
- Discriminated unions
- Field constraints
- Immutable updates

### Validation Results
- **MyPy --strict**: ✅ Success - no issues found
- **Ruff**: ✅ All checks pass
- **Self-Analysis**: 97.3% patterns, 2.7% violations (boundary operations)
- **Test Coverage**: All fixtures detect patterns correctly

## Boundary Operations

The only acceptable violations are at system boundaries:
- AST node attribute access (marked with comments)
- File I/O operations (isolated in service layer)
- TYPE_CHECKING import guards

All boundary operations are:
1. Clearly marked with comments
2. Isolated to specific functions
3. Converted to domain models immediately

## Future Enhancements

### Additional Pattern Detection
**Low-hanging fruit (~100 lines total):**
- `cast()` usage detection
- `match/case` statement detection
- `Any` type annotation detection
- String literal detection for domain concepts
- Lazy initialization patterns

**Complex patterns (requires deeper analysis):**
- Primitive obsession detection
- Missing model_config detection
- Missing Field() constraints
- Optional misuse patterns
- Full anemic model analysis

### Architectural Improvements
- Enhanced reporting with detailed metrics
- Performance optimizations for large codebases
- Plugin system for custom pattern detection
- Integration with CI/CD pipelines
- Real-time IDE integration

## Educational Value

The codebase itself serves as a living demonstration of SDA principles:
- **Zero conditionals** in business logic shows the power of discriminated unions
- **Behavioral enums** demonstrate how to encode logic in types
- **Immutable context** shows functional programming patterns
- **Clean boundaries** demonstrate proper separation of concerns
- **Self-analysis capability** proves the architecture works

Every line of code teaches by example, making this tool both a detector and a reference implementation of Semantic Domain Architecture.

## Summary

The SDA Detector achieves sophisticated simplicity through:
- Complex architectural intelligence encoded in simple patterns
- Pure discriminated union dispatch eliminating all conditionals
- Domain models that understand and analyze themselves
- Clean separation between orchestration and intelligence
- Trust in type system guarantees over defensive programming

The architecture demonstrates that with proper type-driven design, complex analysis can be expressed through clean, simple, and maintainable patterns that teach by their very existence.
