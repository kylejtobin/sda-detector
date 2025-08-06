"""SDA Pattern Analyzers - Focused domain models for pattern detection.

This package contains specialized analyzers that detect specific architectural
patterns in code. Each analyzer is a focused domain model that knows how to
analyze one type of AST pattern.

Following SDA principles:
- Each analyzer is a self-contained domain model
- Analyzers know how to analyze themselves from AST nodes
- No external business logic - all intelligence is in the models

These analyzers are imported directly by core_types.py for dispatch.
They are not part of the public API.
"""

# No exports - analyzers are internal implementation details
__all__: list[str] = []
