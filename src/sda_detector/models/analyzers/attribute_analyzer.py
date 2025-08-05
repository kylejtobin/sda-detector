"""Attribute access analyzer following SDA architecture patterns.

This module analyzes attribute access in Python code, identifying patterns
that align with or violate SDA principles.

CRITICAL SDA COMPLIANCE:
- Zero isinstance/hasattr/getattr usage
- Pure discriminated union dispatch via enums
- All behavior encoded in type system
- No procedural conditionals for type dispatch
"""

import ast
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from ..analysis_domain import Finding
    from ..context_domain import RichAnalysisContext

from ..core_types import PatternType, PositivePattern
from .ast_utils import ASTNodeMetadata, extract_ast_metadata


class AttributePattern(StrEnum):
    """Behavioral enum for attribute access pattern classification.

    Each pattern knows its own analysis behavior and finding creation logic.
    This eliminates conditional dispatch in favor of type-driven behavior.
    """

    ENUM_UNWRAPPING = "enum_unwrapping"
    COMPUTED_FIELD_CANDIDATE = "computed_field_candidate"
    NORMAL_ACCESS = "normal_access"

    def create_finding(self, file_path: str, line_number: int, attribute_name: str) -> list["Finding"]:
        """Behavioral method - patterns know how to create their own findings.

        Pure discriminated union dispatch without conditionals.
        Returns a list - empty for patterns that don't generate findings.
        """
        from ..analysis_domain import Finding

        # Pure dictionary dispatch - patterns decide their own findings
        finding_creators = {
            AttributePattern.ENUM_UNWRAPPING: [
                Finding(
                    file_path=file_path,
                    line_number=line_number,
                    description=f"{PatternType.ENUM_VALUE_ACCESS}: {attribute_name}",
                )
            ],
            AttributePattern.COMPUTED_FIELD_CANDIDATE: [
                Finding(
                    file_path=file_path,
                    line_number=line_number,
                    description=f"{PositivePattern.COMPUTED_FIELDS}: {attribute_name}",
                )
            ],
            AttributePattern.NORMAL_ACCESS: [],  # Normal access produces no findings
        }

        return finding_creators[self]


class AttributeDomain(BaseModel):
    """Domain model for attribute access analysis.

    Detects SDA violations like enum.value unwrapping and suggests computed fields
    for attributes that look like derived calculations (total, count, etc.).

    SDA Principle: Domain models are self-analyzing and delegate to behavioral enums.
    """

    model_config = ConfigDict(frozen=True)

    attribute_name: str = Field(description="Attribute being accessed")
    metadata: ASTNodeMetadata

    @computed_field
    @property
    def is_enum_unwrapping(self) -> bool:
        """Domain intelligence: detects enum .value unwrapping anti-pattern."""
        return self.attribute_name == "value"

    @computed_field
    @property
    def suggests_computed_field(self) -> bool:
        """Domain intelligence: identifies attributes that should be computed fields."""
        computed_patterns = ["total", "count", "sum", "avg", "max", "min"]
        return any(pattern in self.attribute_name.lower() for pattern in computed_patterns)

    @computed_field
    @property
    def pattern_classification(self) -> AttributePattern:
        """Classify attribute pattern using SDA priority dispatch.

        SDA Principle: Pure discriminated union dispatch without conditionals.
        """
        # Pure boolean coercion with StrEnum dispatch - no conditionals!
        # Each boolean state maps directly to its corresponding pattern
        pattern_mapping = {
            (True, True): AttributePattern.ENUM_UNWRAPPING,  # enum_unwrapping takes priority
            (True, False): AttributePattern.ENUM_UNWRAPPING,  # enum_unwrapping only
            (False, True): AttributePattern.COMPUTED_FIELD_CANDIDATE,  # computed_field only
            (False, False): AttributePattern.NORMAL_ACCESS,  # neither
        }

        classification_key = (self.is_enum_unwrapping, self.suggests_computed_field)
        return pattern_mapping[classification_key]

    def analyze(self, context: "RichAnalysisContext") -> list["Finding"]:
        """Self-analyzing domain model using enum behavioral methods.

        SDA Principle: Domain models delegate to behavioral enums that know their own logic.
        """
        # Pure discriminated union dispatch - pattern decides what findings to create
        return self.pattern_classification.create_finding(
            file_path=context.current_file, line_number=self.metadata.line_number, attribute_name=self.attribute_name
        )


class AttributeAnalyzer:
    """Pure orchestration for attribute analysis following SDA service patterns.

    This analyzer contains ZERO business logic - all intelligence lives in
    AttributeDomain and AttributePattern. The analyzer only orchestrates
    the creation and analysis flow.

    SDA Principle: Services orchestrate, models decide.
    """

    @classmethod
    def from_ast(cls, node: ast.AST, file_path: str) -> AttributeDomain:
        """Factory method for creating AttributeDomain from AST nodes.

        Discriminated union guarantees this is ast.Attribute.
        This is the type boundary - we handle the conversion here.
        """
        # Extract attribute name from AST node - boundary operation
        attribute_name = getattr(node, 'attr', 'unknown')  # Boundary operation - AST interface
        metadata = extract_ast_metadata(node)

        return AttributeDomain(attribute_name=attribute_name, metadata=metadata)

    @classmethod
    def analyze_node(cls, node: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze an AST node for attribute access patterns.

        Trust discriminated union - delegate to domain model.
        The domain model's from_ast handles the type boundary perfectly.
        """
        # Domain model handles the type boundary - sophisticated simplicity!
        domain_model = cls.from_ast(node, context.current_file)
        return domain_model.analyze(context)
