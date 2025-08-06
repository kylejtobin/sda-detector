"""Rich Analysis Context - Accumulating Domain Intelligence During Code Traversal.

PURPOSE:
This module demonstrates how to handle stateful analysis in a functional way,
using immutable context that flows through the analysis pipeline, accumulating
semantic understanding without mutable state.

SDA PRINCIPLES DEMONSTRATED:
1. **Immutable Context Flow**: State changes via model_copy(), never mutation
2. **Computed Intelligence**: Derived facts calculated from base data
3. **Scope Stacking**: Tracking nested structures functionally
4. **Pattern Detection by Name**: Inferring purpose from naming conventions
5. **Multi-Indicator Logic**: Combining signals for classification

LEARNING GOALS:
- Understand immutable state management in tree traversal
- Learn how context accumulates information without mutation
- Master computed fields for derived intelligence
- See how to infer code purpose from names and structure
- Recognize the power of immutable data structures

ARCHITECTURE NOTES:
This is the most sophisticated state management in the codebase. It shows
how to maintain context during recursive tree traversal without any mutable
state. The context flows DOWN the tree (via parameters) and findings flow
UP (via return values).

Teaching Example:
    >>> # Traditional mutable approach:
    >>> class Analyzer:
    >>>     def __init__(self):
    >>>         self.current_class = None  # Mutable!
    >>>         self.scope_stack = []  # Mutable!
    >>>     
    >>>     def enter_class(self, name):
    >>>         self.current_class = name  # Mutation!
    >>>         self.scope_stack.append(name)  # Mutation!
    >>> 
    >>> # SDA immutable approach:
    >>> context = RichAnalysisContext(current_file="test.py", module_type=ModuleType.DOMAIN)
    >>> new_context = context.enter_scope(class_scope)  # Returns NEW context
    >>> # Original context unchanged - immutable!

Key Insight:
Immutability eliminates entire categories of bugs: race conditions, unexpected
state changes, and action-at-a-distance. It makes code predictable and testable.
"""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .core_types import ModuleType


class ScopeType(StrEnum):
    """Behavioral enum for different code scope types.

    WHAT: Represents different levels of code organization (module, class,
    function, etc.) with semantic meaning for pattern detection.
    
    WHY: Different scope types have different architectural implications.
    Classes define structure, functions define behavior, try blocks indicate
    boundaries. This enum encodes that knowledge.
    
    HOW: Each scope type has properties that reveal its architectural
    significance, enabling context-aware analysis.
    
    Teaching Example:
        >>> scope = ScopeType.CLASS
        >>> print(scope.analysis_priority)  # 1 - highest priority
        >>> print(scope.creates_naming_scope)  # True - classes create namespaces
        >>> print(scope.suggests_business_logic)  # True - classes often have logic
    
    SDA Pattern Demonstrated:
        Smart Enums - The enum knows architectural implications of each
        scope type, eliminating external classification logic.
    """

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    CONDITIONAL = "conditional"
    TRY_BLOCK = "try_block"

    @property
    def analysis_priority(self) -> int:
        """Domain intelligence: analysis priority for different scope types.
        
        Teaching: Priority encodes architectural importance:
        1. CLASS - Defines structure, most important
        2. FUNCTION - Defines behavior, very important
        3. CONDITIONAL - Control flow, important
        4. TRY_BLOCK - Error handling, moderate
        5. MODULE - File level, least specific
        """
        priorities = {
            ScopeType.CLASS: 1,  # Highest - structural architecture
            ScopeType.FUNCTION: 2,  # High - behavior boundaries
            ScopeType.CONDITIONAL: 3,  # Medium - control flow patterns
            ScopeType.TRY_BLOCK: 4,  # Medium - error handling patterns
            ScopeType.MODULE: 5,  # Lower - file-level context
        }
        return priorities[self]

    @property
    def creates_naming_scope(self) -> bool:
        """Does this scope type create a new naming/variable scope?
        
        Teaching: In Python, only modules, classes, and functions create
        new namespaces. Conditionals and try blocks don't!
        """
        return self in {ScopeType.CLASS, ScopeType.FUNCTION, ScopeType.MODULE}

    @property
    def suggests_business_logic(self) -> bool:
        """Does this scope type commonly contain business logic?"""
        return self in {ScopeType.CLASS, ScopeType.FUNCTION}

    @property
    def suggests_infrastructure(self) -> bool:
        """Does this scope type suggest infrastructure/boundary code?"""
        return self in {ScopeType.TRY_BLOCK, ScopeType.MODULE}


class AnalysisScope(BaseModel):
    """Individual scope in the analysis context stack.

    WHAT: Represents one level of code nesting (a class, function, or block)
    with intelligence about what patterns are likely within it.
    
    WHY: Code behavior often depends on context. A conditional in a validation
    function is different from one in business logic. This model captures that.
    
    HOW: Combines scope type with name analysis to infer purpose, using
    computed fields to derive semantic meaning.
    
    Teaching Example:
        >>> # A validation function scope:
        >>> scope = AnalysisScope(
        >>>     scope_type=ScopeType.FUNCTION,
        >>>     name="validate_order",
        >>>     line_number=42
        >>> )
        >>> print(scope.is_validation_scope)  # True - name contains 'validate'
        >>> print(scope.is_boundary_scope)  # False - validation isn't boundary
        >>> print(scope.likely_contains_business_logic)  # False - it's validation
    
    SDA Pattern Demonstrated:
        Name-Based Intelligence - Inferring code purpose from naming
        conventions. This is heuristic but surprisingly effective.
    """

    model_config = ConfigDict(frozen=True)

    scope_type: ScopeType = Field(description="Semantic type of this scope")
    name: str = Field(description="Identifier name for this scope")
    line_number: int = Field(ge=1, description="Source code line where scope begins")

    @computed_field
    @property
    def analysis_priority(self) -> int:
        """Delegate to enum for consistent priority logic."""
        return self.scope_type.analysis_priority

    @computed_field
    @property
    def is_serialization_scope(self) -> bool:
        """Domain intelligence: does scope name suggest serialization activity?
        
        Teaching Note: PATTERN DETECTION BY NAMING CONVENTION
        
        This shows acceptable use of 'any()' with generator expression.
        We're checking if ANY pattern matches - this is data operation,
        not business logic. The patterns list encodes domain knowledge
        about common serialization naming conventions.
        """
        serialization_patterns = ["json", "dump", "serialize", "export", "save"]
        return any(pattern in self.name.lower() for pattern in serialization_patterns)

    @computed_field
    @property
    def is_validation_scope(self) -> bool:
        """Domain intelligence: does scope name suggest validation activity?"""
        validation_patterns = ["validate", "check", "verify", "ensure", "assert"]
        return any(pattern in self.name.lower() for pattern in validation_patterns)

    @computed_field
    @property
    def is_boundary_scope(self) -> bool:
        """Domain intelligence: does scope suggest infrastructure/boundary code?
        
        Teaching Note: MULTI-SIGNAL CLASSIFICATION
        
        This combines two signals:
        1. Type-based: Try blocks suggest boundary (error handling)
        2. Name-based: Certain names suggest adapters/connectors
        
        The 'if' here is acceptable - it's combining signals, not
        making business decisions. Early return for efficiency.
        """
        # Teaching: Type-level boundary detection
        if self.scope_type.suggests_infrastructure:
            return True

        # Teaching: Name-based boundary detection
        boundary_patterns = ["client", "adapter", "wrapper", "handler", "connector"]
        return any(pattern in self.name.lower() for pattern in boundary_patterns)

    @computed_field
    @property
    def likely_contains_business_logic(self) -> bool:
        """Domain intelligence: does this scope likely contain business logic?
        
        Teaching: Business logic is what's LEFT after excluding:
        - Boundary/infrastructure code
        - Validation code
        This is process of elimination - elegant!
        """
        return self.scope_type.suggests_business_logic and not self.is_boundary_scope and not self.is_validation_scope


class RichAnalysisContext(BaseModel):
    """Immutable analysis context that flows through AST traversal.

    WHAT: An immutable data structure that accumulates context during
    code analysis, providing rich information about the current location.
    
    WHY: Mutable state during tree traversal is error-prone. Race conditions,
    unexpected mutations, and debugging nightmares. Immutable context eliminates
    these problems while providing rich analysis capabilities.
    
    HOW: Uses Pydantic's model_copy() for immutable updates, computed fields
    for derived intelligence, and scope stacking for nested contexts.
    
    Teaching Example:
        >>> # Start with file context:
        >>> ctx = RichAnalysisContext.for_file("order.py", ModuleType.DOMAIN)
        >>> 
        >>> # Enter a class (immutably):
        >>> class_scope = AnalysisScope(ScopeType.CLASS, "Order", 10)
        >>> ctx2 = ctx.enter_scope(class_scope)  # NEW context
        >>> print(ctx.current_class_name)  # "" - original unchanged!
        >>> print(ctx2.current_class_name)  # "Order" - new context
        >>> 
        >>> # Enter a method (immutably):
        >>> method_scope = AnalysisScope(ScopeType.FUNCTION, "calculate_total", 20)
        >>> ctx3 = ctx2.enter_scope(method_scope)
        >>> print(ctx3.nesting_level)  # 2 - class + function
        >>> print(ctx3.in_business_logic_context)  # True - likely business logic
    
    SDA Principles Demonstrated:
        - Immutability: All state changes via model_copy(), never mutation
        - Rich Context: Semantic understanding beyond "current file"
        - Computed Intelligence: Derived facts from base data
        - Type Safety: Everything properly typed and validated
    """

    model_config = ConfigDict(frozen=True)

    current_file: str = Field(description="Path to the file being analyzed")
    module_type: ModuleType = Field(description="Semantic classification of this module")
    scope_stack: list[AnalysisScope] = Field(
        default_factory=list, description="Stack of nested scopes (functions, classes, conditionals)"
    )

    @classmethod
    def for_file(cls, file_path: str, module_type: ModuleType) -> "RichAnalysisContext":
        """Factory method for creating analysis context for a file.

        This classmethod provides clean, type-safe context creation following
        SDA patterns. It encapsulates the context creation logic and ensures
        consistent initialization.

        Args:
            file_path: Path to the file being analyzed
            module_type: Semantic classification of the module

        Returns:
            New RichAnalysisContext ready for analysis

        SDA Principle: Factory methods provide clean domain model creation
        """
        return cls(current_file=file_path, module_type=module_type, scope_stack=[])

    @computed_field
    @property
    def current_scope(self) -> AnalysisScope | None:
        """The innermost scope we're currently analyzing.
        
        Teaching: Safe list access - returns None if stack empty.
        The [-1] index gets the last (most recent) scope.
        """
        return self.scope_stack[-1] if self.scope_stack else None

    @computed_field
    @property
    def nesting_level(self) -> int:
        """How deeply nested are we in scope hierarchy?"""
        return len(self.scope_stack)

    @computed_field
    @property
    def in_serialization_context(self) -> bool:
        """Domain intelligence: are we in serialization-related code?
        
        Teaching: Bubbling up properties - if ANY scope in the stack
        is serialization-related, we're in serialization context.
        """
        return any(scope.is_serialization_scope for scope in self.scope_stack)

    @computed_field
    @property
    def in_validation_context(self) -> bool:
        """Domain intelligence: are we in validation-related code?"""
        return any(scope.is_validation_scope for scope in self.scope_stack)

    @computed_field
    @property
    def in_boundary_context(self) -> bool:
        """Domain intelligence: are we in infrastructure/boundary code?
        
        Teaching Note: COMBINING MULTIPLE SIGNALS
        
        This shows sophisticated classification using three signals:
        1. File name patterns (client.py, adapter.py)
        2. Scope analysis (any scope suggests boundary?)
        3. Module type (infrastructure/framework modules)
        
        Using 'or' to combine - if ANY signal says boundary, it is.
        This is conservative - better to over-identify boundaries.
        """
        # Teaching: Multiple indicators for robust classification
        file_suggests_boundary = self._file_suggests_boundary()
        scope_suggests_boundary = any(scope.is_boundary_scope for scope in self.scope_stack)
        module_suggests_boundary = self.module_type in {ModuleType.INFRASTRUCTURE, ModuleType.FRAMEWORK}

        return file_suggests_boundary or scope_suggests_boundary or module_suggests_boundary

    @computed_field
    @property
    def in_business_logic_context(self) -> bool:
        """Domain intelligence: are we likely in business logic code?"""
        return any(scope.likely_contains_business_logic for scope in self.scope_stack) and not self.in_boundary_context

    @computed_field
    @property
    def in_type_checking_context(self) -> bool:
        """Domain intelligence: are we in a TYPE_CHECKING conditional block?"""
        return any(scope.name == "TYPE_CHECKING" for scope in self.scope_stack)

    @computed_field
    @property
    def current_function_name(self) -> str:
        """Name of current function scope, empty string if not in function.
        
        Teaching: List comprehension + conditional expression pattern.
        1. Filter scopes to find functions
        2. Take the last one (innermost)
        3. Return name or empty string
        
        This avoids exceptions and None - always returns a string.
        """
        function_scopes = [s for s in self.scope_stack if s.scope_type == ScopeType.FUNCTION]
        return function_scopes[-1].name if function_scopes else ""

    @computed_field
    @property
    def current_class_name(self) -> str:
        """Name of current class scope, empty string if not in class."""
        class_scopes = [s for s in self.scope_stack if s.scope_type == ScopeType.CLASS]
        return class_scopes[-1].name if class_scopes else ""

    def _file_suggests_boundary(self) -> bool:
        """Helper: does the filename suggest boundary/infrastructure code?
        
        Teaching: Private method for internal logic. The underscore
        signals this is not part of the public API.
        """
        file_path = Path(self.current_file)
        boundary_patterns = ["client", "adapter", "wrapper", "config", "settings"]
        return any(pattern in file_path.name.lower() for pattern in boundary_patterns)

    def enter_scope(self, scope: AnalysisScope) -> "RichAnalysisContext":
        """Enter a new scope, returning updated immutable context.

        Teaching Note: IMMUTABLE STATE TRANSITION
        
        This is the key pattern for immutable updates:
        1. Create new data ([*self.scope_stack, scope] spreads + appends)
        2. Use model_copy() with update dict
        3. Return NEW context (original unchanged)
        
        The [*list, item] syntax is Python's spread operator - creates
        a new list with existing items plus the new one.
        
        Args:
            scope: New scope to enter (function, class, conditional, etc.)

        Returns:
            New context with scope added to stack

        SDA Principle: Immutable state transitions via model_copy()
        """
        new_stack = [*self.scope_stack, scope]
        return self.model_copy(update={"scope_stack": new_stack})

    def exit_scope(self) -> "RichAnalysisContext":
        """Exit current scope, returning updated immutable context.

        Teaching Note: SAFE SCOPE POPPING
        
        Two important patterns here:
        1. Guard clause - if stack empty, return self (no change)
        2. List slicing [:-1] removes last element immutably
        
        This can't fail - either we have scopes to pop or we don't.
        No exceptions, no mutations, completely safe.
        
        Returns:
            New context with top scope removed, or same context if stack empty

        SDA Principle: Immutable updates ensure predictable state management
        """
        if not self.scope_stack:
            return self
        new_stack = self.scope_stack[:-1]
        return self.model_copy(update={"scope_stack": new_stack})
