"""SDA Detector Models - Domain-driven architecture with behavioral intelligence.

This package organizes domain models following SDA principles:
- Rich domain models with business logic
- Behavioral enums with methods
- Self-analyzing models through computed fields
- Immutable models with pure functional updates

## Domain Organization

- **core_types**: Fundamental enums and discriminated unions
- **analysis_domain**: Core findings and pattern detection
- **context_domain**: Rich analysis context that flows through traversal
- **classification_domain**: Module and path classification intelligence
- **reporting_domain**: Report generation and metrics
- **analyzers/**: Self-analyzing domain models for specific patterns
"""

# Only export what's needed by external users (main __init__.py)
from .core_types import ModuleType, PatternType, PositivePattern
from .reporting_domain import ArchitectureReport

__all__ = [
    "ArchitectureReport",
    "ModuleType",
    "PatternType",
    "PositivePattern",
]
