"""SDA Pattern Analyzers - Focused domain models for pattern detection.

This package contains specialized analyzers that detect specific architectural
patterns in code. Each analyzer is a focused domain model that knows how to
analyze one type of AST pattern.

Following SDA principles:
- Each analyzer is a self-contained domain model
- Analyzers know how to analyze themselves from AST nodes
- No external business logic - all intelligence is in the models
"""

from .attribute_analyzer import AttributeAnalyzer, AttributeDomain, AttributePattern
from .call_analyzer import CallAnalyzer, CallDomain, CallPattern
from .conditional_analyzer import (
    ConditionalAnalyzer,
    ConditionalDomain,
    ConditionalPattern,
)

__all__ = [
    "AttributeAnalyzer",
    "AttributeDomain",
    "AttributePattern",
    "CallAnalyzer",
    "CallDomain",
    "CallPattern",
    "ConditionalAnalyzer",
    "ConditionalDomain",
    "ConditionalPattern",
]
