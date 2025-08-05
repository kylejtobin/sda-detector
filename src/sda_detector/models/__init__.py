"""SDA Detector Models - Domain-driven architecture organized by business concerns.

This package organizes domain models by business functionality rather than
technical layers, following SDA principles for clear domain boundaries.

## Domain Organization

- **domain_types**: Core vocabulary (enums, fundamental types)
- **analysis_domain**: How we analyze code (findings, context, config)
- **reporting_domain**: How we present results (reports, formatting)
- **ast_intelligence**: Pure SDA AST analysis models

All models are re-exported here for backward compatibility with existing code.
"""

# Core Types - Fundamental domain vocabulary
# Analysis Domain - How we analyze code
from .analysis_domain import Finding

# Classification Domain - Module classification logic
from .classification_domain import ModuleClassifier

# Context Domain - Rich analysis context
from .context_domain import AnalysisScope, RichAnalysisContext
from .core_types import ModuleType, PatternType, PositivePattern

# Reporting Domain - How we present results
from .reporting_domain import ArchitectureReport

# Complete public API - Essential exports only
__all__ = [
    "AnalysisScope",
    "ArchitectureReport",
    "Finding",
    "ModuleClassifier",
    "ModuleType",
    "PatternType",
    "PositivePattern",
    "RichAnalysisContext",
]
