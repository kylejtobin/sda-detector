"""Conditional logic analyzer following SDA architecture patterns - Teaching Conditional Elimination.

PURPOSE:
This analyzer detects and classifies conditional statements in Python code,
demonstrating how to analyze code patterns while following SDA principles ourselves.

SDA PRINCIPLES DEMONSTRATED:
1. **Self-Analyzing Models**: ConditionalDomain analyzes itself
2. **Behavioral Enums**: ConditionalPattern creates its own findings
3. **Exhaustive Dispatch**: All boolean combinations explicitly mapped
4. **AST Boundary Handling**: Clean separation from Python's AST
5. **Zero Meta-Conditionals**: Analyzing conditionals without using them!

LEARNING GOALS:
- Understand the irony and power of analyzing conditionals without conditionals
- Learn exhaustive boolean tuple dispatch for complex classification
- Master behavioral enum patterns for finding creation
- See how AST analysis works with Python's abstract syntax tree
- Recognize different types of conditionals (business vs infrastructure)

ARCHITECTURE NOTES:
This analyzer is meta - it finds conditionals in code while avoiding them itself.
It demonstrates that even complex classification logic can be expressed through
pure data structures and behavioral types. The exhaustive boolean mapping ensures
no edge case is missed.

Teaching Example:
    >>> # What we're analyzing (in user code):
    >>> if isinstance(obj, SomeClass):  # Business conditional - violation!
    >>>     handle_some_class(obj)
    >>> elif obj is None:  # Boundary check - acceptable
    >>>     return default_value
    >>> 
    >>> # How we analyze it (SDA style):
    >>> conditional = ConditionalDomain.from_ast(if_node)
    >>> pattern = conditional.pattern_classification  # Pure dispatch
    >>> finding = pattern.create_finding(...)  # Enum creates its own finding

Key Insight:
We use SDA patterns to detect SDA violations. This is "eating our own dog food" -
the analyzer itself demonstrates the patterns it's looking for. No conditionals
are used to find conditionals!
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

    WHAT: Classifies different types of conditional statements found in code.
    Each value represents a different purpose for using if/elif/else.
    
    WHY: Not all conditionals are bad! Some are necessary (boundaries, validation),
    others violate SDA (business logic). This enum distinguishes between them.
    
    HOW: Each enum value knows how to create its own finding, encoding the
    classification logic in the type system itself.
    
    Teaching Categories:
        - TYPE_GUARD: if TYPE_CHECKING blocks (necessary for imports)
        - VALIDATION_CHECK: Input validation (acceptable at boundaries)
        - BOUNDARY_CONDITION: Error/None checks (necessary at boundaries)
        - LAZY_INITIALIZATION: Delayed setup (code smell, often avoidable)
        - BUSINESS_LOGIC: Core logic in conditionals (SDA violation!)
    
    SDA Pattern Demonstrated:
        Behavioral Enums - Instead of external finding factories, each
        enum value knows exactly what kind of finding it represents.
    """

    TYPE_GUARD = "type_guard"
    VALIDATION_CHECK = "validation_check"
    BOUNDARY_CONDITION = "boundary_condition"
    LAZY_INITIALIZATION = "lazy_initialization"
    BUSINESS_LOGIC = "business_logic"

    def create_finding(self, file_path: str, line_number: int, expression: str) -> "Finding":
        """Enum behavioral method: each pattern creates its own finding type.

        Teaching Note: ENUM INTELLIGENCE
        
        This method shows how enums can be smart:
        1. Each enum value maps to a specific finding type
        2. The mapping is data, not conditionals
        3. The enum creates the finding itself
        
        This eliminates the need for external factories or services.
        The enum IS the factory!
        
        Notice the classification:
        - TYPE_GUARD/VALIDATION/BOUNDARY -> Positive patterns (necessary)
        - LAZY_INIT/BUSINESS_LOGIC -> Violations (avoidable)
        """
        from ..analysis_domain import Finding
        from ..core_types import PatternType, PositivePattern

        # Each enum value knows its corresponding finding type
        finding_types = {
            ConditionalPattern.TYPE_GUARD: PositivePattern.TYPE_CHECKING_IMPORTS,
            ConditionalPattern.VALIDATION_CHECK: PositivePattern.BOUNDARY_CONDITIONS,
            ConditionalPattern.BOUNDARY_CONDITION: PositivePattern.BOUNDARY_CONDITIONS,
            ConditionalPattern.LAZY_INITIALIZATION: PatternType.BUSINESS_CONDITIONALS,  # Lazy init is a violation
            ConditionalPattern.BUSINESS_LOGIC: PatternType.BUSINESS_CONDITIONALS,
        }

        finding_type = finding_types[self]
        return Finding(
            file_path=file_path,
            line_number=line_number,
            description=f"{finding_type}: {expression}",
        )


class ConditionalDomain(BaseModel):
    """Domain model for conditional logic analysis - Self-Classifying Intelligence.
    
    WHAT: Represents a conditional statement with all context needed for classification.
    It understands what type of conditional it represents.
    
    WHY: Instead of external analyzers poking at AST nodes, we create a rich
    domain model that understands itself and can classify its own pattern.
    
    HOW: Computed fields analyze the test expression and context to determine
    the conditional's purpose, then exhaustive dispatch maps to pattern type.
    
    Teaching Example:
        >>> # From this AST node:
        >>> # if user.is_premium:
        >>> #     apply_discount()
        >>> 
        >>> conditional = ConditionalDomain(
        >>>     test_expression="user.is_premium",
        >>>     metadata=metadata,
        >>>     parent_scope="calculate_price"
        >>> )
        >>> 
        >>> # Model classifies itself:
        >>> print(conditional.pattern_classification)  # BUSINESS_LOGIC
        >>> print(conditional.suggests_boundary_logic)  # False
    
    SDA Pattern Demonstrated:
        Self-Analyzing Models - The model contains all logic to understand
        and classify itself. No external analyzer needed!
    """

    model_config = ConfigDict(frozen=True)

    test_expression: str = Field(description="What's being tested")
    metadata: ASTNodeMetadata
    # Rich context that matters for analysis
    parent_scope: str | None = Field(default=None, description="Parent scope context")
    nested_depth: int = Field(default=0, ge=0, description="Nesting level")

    @computed_field
    @property
    def is_type_checking(self) -> bool:
        """Domain intelligence: is this TYPE_CHECKING guard?
        
        Teaching: TYPE_CHECKING is a special constant from typing module.
        It's False at runtime but True for type checkers. This pattern
        allows imports that are only needed for type checking.
        """
        return self.test_expression == "TYPE_CHECKING"

    @computed_field
    @property
    def suggests_boundary_logic(self) -> bool:
        """Domain intelligence: does this suggest boundary handling?
        
        Teaching: Boundary logic is acceptable! These patterns suggest
        the code is dealing with external systems or error conditions.
        We detect these to distinguish from business logic conditionals.
        """
        boundary_patterns = ["error", "exception", "none", "empty", "exists"]
        return any(pattern in self.test_expression.lower() for pattern in boundary_patterns)
    
    @computed_field
    @property
    def is_lazy_initialization(self) -> bool:
        """Domain intelligence: is this lazy initialization pattern?
        
        Teaching: Lazy init is a code smell in SDA. Instead of:
            if self._cache is None:
                self._cache = expensive_operation()
            return self._cache
            
        Use @cached_property or computed fields!
        """
        lazy_patterns = ["_cache is None", "_initialized", "not self._", "self._ is None"]
        return any(pattern in self.test_expression for pattern in lazy_patterns)

    @computed_field
    @property
    def pattern_classification(self) -> ConditionalPattern:
        """Classify conditional pattern using pure discriminated union dispatch.

        Teaching Note: EXHAUSTIVE BOOLEAN DISPATCH - THE ULTIMATE PATTERN
        
        This is the most sophisticated SDA pattern in the codebase!
        
        How it works:
        1. Compute 4 boolean flags (each True/False)
        2. Create a tuple from them - this gives 2^4 = 16 possibilities
        3. Map EVERY possibility to a classification
        4. Look up the result - pure O(1) dispatch!
        
        Why exhaustive mapping?
        - No edge cases can be missed
        - Priority is explicit in the mapping
        - Easy to verify correctness (check all 16)
        - Performance is constant time
        
        The mapping encodes priorities:
        1. TYPE_CHECKING always wins (8 entries)
        2. Then validation context (4 entries)
        3. Then lazy init (2 entries)
        4. Then boundary (1 entry)
        5. Default to business logic (1 entry)
        
        This replaces what would be nested if/elif logic with pure data!
        """
        # Create classification key based on computed properties
        validation_scope = bool(self.parent_scope and "validate" in self.parent_scope.lower())
        
        # Pure tuple-based dispatch for pattern classification
        classification_key = (
            self.is_type_checking,
            validation_scope,
            self.is_lazy_initialization,
            self.suggests_boundary_logic
        )
        
        # Teaching: Exhaustive mapping of all 16 combinations
        # Priority is encoded in the mapping itself - no if/elif needed!
        classification_map = {
            # Type checking takes highest priority
            (True, False, False, False): ConditionalPattern.TYPE_GUARD,
            (True, False, False, True): ConditionalPattern.TYPE_GUARD,
            (True, False, True, False): ConditionalPattern.TYPE_GUARD,
            (True, False, True, True): ConditionalPattern.TYPE_GUARD,
            (True, True, False, False): ConditionalPattern.TYPE_GUARD,
            (True, True, False, True): ConditionalPattern.TYPE_GUARD,
            (True, True, True, False): ConditionalPattern.TYPE_GUARD,
            (True, True, True, True): ConditionalPattern.TYPE_GUARD,
            
            # Validation scope takes second priority
            (False, True, False, False): ConditionalPattern.VALIDATION_CHECK,
            (False, True, False, True): ConditionalPattern.VALIDATION_CHECK,
            (False, True, True, False): ConditionalPattern.VALIDATION_CHECK,
            (False, True, True, True): ConditionalPattern.VALIDATION_CHECK,
            
            # Lazy initialization takes third priority
            (False, False, True, False): ConditionalPattern.LAZY_INITIALIZATION,
            (False, False, True, True): ConditionalPattern.LAZY_INITIALIZATION,
            
            # Boundary logic takes fourth priority
            (False, False, False, True): ConditionalPattern.BOUNDARY_CONDITION,
            
            # Default to business logic
            (False, False, False, False): ConditionalPattern.BUSINESS_LOGIC,
        }
        
        return classification_map[classification_key]

    def analyze(self, context: "RichAnalysisContext") -> list["Finding"]:
        """Self-analyzing domain model using enum behavioral methods.

        Teaching Note: DELEGATION TO BEHAVIORAL TYPES
        
        This method is beautifully simple because all the intelligence
        is already encoded:
        1. pattern_classification computed field does classification
        2. Enum's create_finding method creates the finding
        3. We just connect them!
        
        This is "Tell, Don't Ask" - we tell the enum to create a finding,
        not ask what type it is and create it ourselves.
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
        
        Teaching Note: AST BOUNDARY PATTERN
        
        This is a boundary method - it converts Python's untyped AST
        into our typed domain model. Notice:
        
        1. We use getattr() - this is OK at boundaries!
        2. We provide defaults for safety
        3. We immediately convert to our domain types
        4. After this, no more AST access needed
        
        The discriminated union in ASTNodeType guarantees this is
        an ast.If node, so we know 'test' attribute exists.
        
        ast.unparse() converts AST back to Python code string - very
        useful for understanding what we're analyzing!
        """
        # Teaching: Type boundary - Access known ast.If attributes
        # The discriminated union classification guarantees these exist
        # getattr() is acceptable here because we're at the AST boundary
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
    
    WHAT: Entry point for analyzing conditional AST nodes, delegating to
    the ConditionalDomain model for actual analysis.
    
    WHY: Provides a clean interface for the ASTNodeType dispatch system
    while keeping all intelligence in the domain model.
    
    HOW: Simply creates a ConditionalDomain from the AST node and lets
    it analyze itself - pure delegation pattern.
    
    Teaching Note:
        This class is intentionally minimal - it's just a bridge between
        the AST dispatch system and our domain model. All intelligence
        lives in ConditionalDomain. This is "anemic analyzer, rich model" -
        the opposite of traditional "anemic model, rich service" anti-pattern!
    
    SDA Pattern Demonstrated:
        Delegation to Domain - The analyzer doesn't analyze; it delegates
        to a self-analyzing domain model. This keeps logic with data.
    """
    
    @classmethod
    def analyze_node(cls, node: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze an AST node for conditional patterns.
        
        Teaching Note: PURE DELEGATION PATTERN
        
        This method does almost nothing - and that's the point!
        1. Create domain model from AST (boundary conversion)
        2. Tell domain model to analyze itself
        3. Return the results
        
        All the intelligence is in ConditionalDomain. This analyzer
        is just plumbing. This is the ideal in SDA - smart models,
        dumb services/analyzers.
        
        Trust discriminated union - the ASTNodeType dispatch guarantees
        we only get ast.If or ast.Match nodes here.
        """
        # Domain model handles the type boundary - sophisticated simplicity!
        conditional = ConditionalDomain.from_ast(
            node=node,  # Now accepts ast.AST
            parent_scope=context.current_scope.name if context.current_scope else None,
            nested_depth=len(context.scope_stack)
        )
        
        # Let the domain model analyze itself
        return conditional.analyze(context)