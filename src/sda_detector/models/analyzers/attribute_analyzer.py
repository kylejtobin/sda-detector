"""Attribute access analyzer following SDA architecture patterns - Detecting Property Access.

PURPOSE:
This analyzer detects attribute access patterns, particularly focusing on
enum value unwrapping (anti-pattern) and identifying candidates for computed fields.

SDA PRINCIPLES DEMONSTRATED:
1. **4-State Boolean Dispatch**: All combinations of 2 booleans handled
2. **Priority Classification**: Enum unwrapping takes precedence
3. **Pattern-Based Detection**: Recognizes computed field candidates by name
4. **List-Based Findings**: Patterns return lists (empty for no findings)
5. **Self-Analyzing Models**: Domain model classifies itself

LEARNING GOALS:
- Understand attribute access patterns in Python AST
- Learn to detect anti-patterns like .value on enums
- Master 4-state boolean dispatch (simpler than 8 or 16 state)
- See how to identify refactoring opportunities (computed fields)
- Recognize the power of name-based pattern detection

ARCHITECTURE NOTES:
This analyzer is simpler than conditional/call analyzers but demonstrates
the same principles. It shows that even simple checks (is it .value?)
can be expressed through pure type dispatch.

Teaching Example:
    >>> # What we're analyzing:
    >>> status.value  # ENUM_UNWRAPPING - use enum directly!
    >>> order.total  # COMPUTED_FIELD_CANDIDATE - should be @computed_field
    >>> user.name  # NORMAL_ACCESS - just a regular attribute
    >>> 
    >>> # How we analyze it:
    >>> attr = AttributeDomain(attribute_name="value", metadata=...)
    >>> pattern = attr.pattern_classification  # ENUM_UNWRAPPING
    >>> findings = pattern.create_finding(...)  # Returns violation finding

Key Insight:
Even simple binary checks (is it .value?) are expressed through the full
SDA pattern machinery. This consistency makes the codebase predictable.
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

    WHAT: Classifies attribute access into three categories based on
    the attribute name and its implications for code quality.
    
    WHY: Different attribute access patterns indicate different code smells
    or improvement opportunities. .value suggests enum misuse, while
    .total suggests a computed field opportunity.
    
    HOW: Each pattern knows whether to create findings and what type,
    returning a list (empty for patterns that don't need reporting).
    
    Teaching Categories:
        - ENUM_UNWRAPPING: Accessing .value on enums (anti-pattern)
        - COMPUTED_FIELD_CANDIDATE: Attributes that compute values
        - NORMAL_ACCESS: Regular attribute access (no action needed)
    
    SDA Pattern Demonstrated:
        List-Returning Patterns - Instead of conditionally creating findings,
        patterns always return a list (possibly empty). This eliminates
        None checks and makes the code more uniform.
    """

    ENUM_UNWRAPPING = "enum_unwrapping"
    COMPUTED_FIELD_CANDIDATE = "computed_field_candidate"
    NORMAL_ACCESS = "normal_access"

    def create_finding(self, file_path: str, line_number: int, attribute_name: str) -> list["Finding"]:
        """Behavioral method - patterns know how to create their own findings.

        Teaching Note: LIST-BASED FINDING CREATION
        
        Why return a list instead of Optional[Finding]?
        1. Uniform interface - always get a list
        2. No None checks needed
        3. Easy to extend (pattern could create multiple findings)
        4. Empty list is falsy but safe to iterate
        
        The dictionary values are lists created at call time.
        This is fine for small lists but could use lambdas for
        expensive computations.
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
    """Domain model for attribute access analysis - Understanding Property Patterns.

    WHAT: Represents an attribute access with classification logic to
    determine if it's an anti-pattern or improvement opportunity.
    
    WHY: Attribute access reveals design decisions - .value shows enum
    misunderstanding, .total shows missing computed fields, etc.
    
    HOW: Uses computed properties to detect patterns, then 4-state
    boolean dispatch to classify into final pattern type.
    
    Teaching Example:
        >>> # Analyzing: order.value (enum unwrapping)
        >>> attr = AttributeDomain(attribute_name="value", metadata=...)
        >>> print(attr.is_enum_unwrapping)  # True
        >>> print(attr.pattern_classification)  # ENUM_UNWRAPPING
        >>> 
        >>> # Analyzing: invoice.total (computed field candidate)
        >>> attr = AttributeDomain(attribute_name="total", metadata=...)
        >>> print(attr.suggests_computed_field)  # True
        >>> print(attr.pattern_classification)  # COMPUTED_FIELD_CANDIDATE
    
    SDA Pattern Demonstrated:
        Pattern Detection by Name - Using naming conventions to infer
        code patterns. This is heuristic but effective in practice.
    """

    model_config = ConfigDict(frozen=True)

    attribute_name: str = Field(description="Attribute being accessed")
    metadata: ASTNodeMetadata

    @computed_field
    @property
    def is_enum_unwrapping(self) -> bool:
        """Domain intelligence: detects enum .value unwrapping anti-pattern.
        
        Teaching: In SDA, enums should be used directly, not unwrapped.
        Instead of status.value == "active", use status == Status.ACTIVE.
        This preserves type safety and enables behavioral methods.
        """
        return self.attribute_name == "value"

    @computed_field
    @property
    def suggests_computed_field(self) -> bool:
        """Domain intelligence: identifies attributes that should be computed fields.
        
        Teaching: These attribute names suggest derived values that should
        be @computed_field properties in Pydantic models. This keeps
        computation close to data and ensures consistency.
        
        Examples:
        - order.total -> Should be computed from items
        - stats.avg -> Should be computed from data points
        - report.count -> Should be computed from collections
        """
        computed_patterns = ["total", "count", "sum", "avg", "max", "min"]
        return any(pattern in self.attribute_name.lower() for pattern in computed_patterns)

    @computed_field
    @property
    def pattern_classification(self) -> AttributePattern:
        """Classify attribute pattern using SDA priority dispatch.

        Teaching Note: 4-STATE BOOLEAN DISPATCH
        
        With 2 booleans, we have 2² = 4 possible states.
        This is simpler than 8 or 16 state dispatch but uses
        the same pattern:
        
        1. Compute boolean flags
        2. Create tuple key
        3. Map all possibilities
        4. Look up result
        
        Priority: ENUM_UNWRAPPING > COMPUTED_FIELD > NORMAL
        This reflects severity - enum misuse is worse than
        missing computed fields.
        """
        # Teaching: Pure boolean tuple dispatch - no conditionals!
        # All 4 combinations explicitly handled with clear priorities
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

    WHAT: Entry point for analyzing attribute access nodes, creating
    domain models and delegating analysis to them.
    
    WHY: Separates AST handling (boundary) from business logic (domain).
    The analyzer handles AST extraction, the domain handles classification.
    
    HOW: Factory method creates domain model from AST, then the model
    analyzes itself and returns findings.
    
    Teaching Note:
        This analyzer has TWO methods instead of one - from_ast() and
        analyze_node(). This separation shows that AST conversion and
        analysis are different concerns. Other analyzers combine them
        for simplicity, but both patterns are valid SDA.
    
    SDA Principle: Services orchestrate, models decide.
    """

    @classmethod
    def from_ast(cls, node: ast.AST, file_path: str) -> AttributeDomain:
        """Factory method for creating AttributeDomain from AST nodes.

        Teaching Note: FACTORY METHOD PATTERN
        
        This extracts data from the AST node and creates a clean
        domain model. After this point, no AST access is needed.
        
        The getattr() with default 'unknown' is defensive programming
        at the boundary. We don't trust external data but immediately
        convert it to safe domain values.
        
        Discriminated union guarantees this is ast.Attribute.
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
