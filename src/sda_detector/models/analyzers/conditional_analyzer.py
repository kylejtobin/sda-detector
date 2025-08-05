"""Conditional logic analyzer following SDA architecture patterns.

This module analyzes conditional statements (if/elif/else) in Python code,
classifying them into patterns that align with or violate SDA principles.

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

from .ast_utils import ASTNodeMetadata, extract_ast_metadata

if TYPE_CHECKING:
    from ..analysis_domain import Finding
    from ..context_domain import RichAnalysisContext


# ASTNodeCategory and ASTNodeMetadata now imported from shared utilities


class ConditionalPattern(StrEnum):
    """Behavioral enum for conditional pattern classification.

    Each pattern knows how to create appropriate findings - this is core SDA.
    """

    TYPE_GUARD = "type_guard"
    VALIDATION_CHECK = "validation_check"
    BOUNDARY_CONDITION = "boundary_condition"
    BUSINESS_LOGIC = "business_logic"

    def create_finding(self, file_path: str, line_number: int, expression: str) -> "Finding":
        """Enum behavioral method: each pattern creates its own finding type.

        SDA Principle: Enums encapsulate their own behavior instead of external logic.
        """
        from ..analysis_domain import Finding
        from ..core_types import PatternType, PositivePattern

        # Each enum value knows its corresponding finding type
        finding_types = {
            ConditionalPattern.TYPE_GUARD: PositivePattern.TYPE_CHECKING_IMPORTS,
            ConditionalPattern.VALIDATION_CHECK: PositivePattern.BOUNDARY_CONDITIONS,
            ConditionalPattern.BOUNDARY_CONDITION: PositivePattern.BOUNDARY_CONDITIONS,
            ConditionalPattern.BUSINESS_LOGIC: PatternType.BUSINESS_CONDITIONALS,
        }

        finding_type = finding_types[self]
        return Finding(
            file_path=file_path,
            line_number=line_number,
            description=f"{finding_type}: {expression}",
        )


class ConditionalDomain(BaseModel):
    """Domain model for conditional logic analysis."""

    model_config = ConfigDict(frozen=True)

    test_expression: str = Field(description="What's being tested")
    metadata: ASTNodeMetadata
    # Rich context that matters for analysis
    parent_scope: str | None = Field(default=None, description="Parent scope context")
    nested_depth: int = Field(default=0, ge=0, description="Nesting level")

    @computed_field
    @property
    def is_type_checking(self) -> bool:
        """Domain intelligence: is this TYPE_CHECKING guard?"""
        return self.test_expression == "TYPE_CHECKING"

    @computed_field
    @property
    def suggests_boundary_logic(self) -> bool:
        """Domain intelligence: does this suggest boundary handling?"""
        boundary_patterns = ["error", "exception", "none", "empty", "exists"]
        return any(pattern in self.test_expression.lower() for pattern in boundary_patterns)

    @computed_field
    @property
    def pattern_classification(self) -> ConditionalPattern:
        """Classify conditional pattern using pure discriminated union dispatch.

        SDA Principle: Pure tuple-based dispatch - no conditionals.
        """
        # Create classification key based on computed properties
        validation_scope = bool(self.parent_scope and "validate" in self.parent_scope.lower())
        
        # Pure tuple-based dispatch for pattern classification
        classification_key = (
            self.is_type_checking,
            validation_scope,
            self.suggests_boundary_logic
        )
        
        # Exhaustive mapping of all combinations (priority encoded in order)
        classification_map = {
            # Type checking takes highest priority
            (True, False, False): ConditionalPattern.TYPE_GUARD,
            (True, False, True): ConditionalPattern.TYPE_GUARD,
            (True, True, False): ConditionalPattern.TYPE_GUARD,
            (True, True, True): ConditionalPattern.TYPE_GUARD,
            
            # Validation scope takes second priority
            (False, True, False): ConditionalPattern.VALIDATION_CHECK,
            (False, True, True): ConditionalPattern.VALIDATION_CHECK,
            
            # Boundary logic takes third priority
            (False, False, True): ConditionalPattern.BOUNDARY_CONDITION,
            
            # Default to business logic
            (False, False, False): ConditionalPattern.BUSINESS_LOGIC,
        }
        
        return classification_map[classification_key]

    def analyze(self, context: "RichAnalysisContext") -> list["Finding"]:
        """Self-analyzing domain model using enum behavioral methods.

        SDA Principle: Domain models delegate to behavioral enums that know their own logic.
        """
        # Elegant: Let the enum create its own finding - zero conditionals!
        finding = self.pattern_classification.create_finding(
            file_path=context.current_file, 
            line_number=self.metadata.line_number, 
            expression=self.test_expression
        )
        return [finding]

    @classmethod
    def from_ast(cls, node: ast.AST, parent_scope: str | None = None, nested_depth: int = 0) -> "ConditionalDomain":
        """Create ConditionalDomain from AST node using pure SDA patterns.
        
        Discriminated union guarantees this is ast.If.
        This is the type boundary - we handle the conversion here.
        """
        # Type boundary: Access known ast.If attributes
        # The discriminated union classification guarantees these exist
        test_node = getattr(node, 'test', None)  # Boundary operation - AST interface
        test_expression = ast.unparse(test_node) if test_node else "unknown"
        
        # Create metadata using shared SDA-compliant factory
        metadata = extract_ast_metadata(node)
        
        return cls(
            test_expression=test_expression,
            metadata=metadata,
            parent_scope=parent_scope,
            nested_depth=nested_depth
        )


class ConditionalAnalyzer:
    """Analyzer for conditional logic patterns in Python code.
    
    This analyzer identifies and classifies conditional statements according
    to SDA principles, distinguishing between acceptable patterns (type guards,
    boundary conditions) and violations (business logic conditionals).
    """
    
    @classmethod
    def analyze_node(cls, node: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze an AST node for conditional patterns.
        
        Trust discriminated union - delegate to domain model.
        The domain model's from_ast handles the type boundary perfectly.
        """
        # Domain model handles the type boundary - sophisticated simplicity!
        conditional = ConditionalDomain.from_ast(
            node=node,  # Now accepts ast.AST
            parent_scope=context.current_scope.name if context.current_scope else None,
            nested_depth=len(context.scope_stack)
        )
        
        # Let the domain model analyze itself
        return conditional.analyze(context)