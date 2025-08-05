"""Rich Analysis Context - Accumulating Domain Intelligence During Code Traversal.

This module demonstrates how SDA handles stateful analysis through immutable context models.
Instead of global state or mutable trackers, we use immutable context that flows through
the analysis pipeline, accumulating semantic understanding of code structure.

Key SDA Concepts Demonstrated:
- Immutable Context: State changes through model_copy(), never direct mutation
- Computed Fields: Derived intelligence that updates automatically from base data
- Scope Modeling: Rich domain types for different kinds of code scopes
- Context Stacking: Track nested code structures (functions within classes, etc.)
- Domain Intelligence: Models know their own semantic meaning and patterns

Educational Focus:
- Context flows through AST traversal, building understanding of code structure
- Each scope (function, class, conditional) has semantic meaning for pattern detection
- Immutable updates ensure thread safety and predictable behavior
- Computed fields provide derived intelligence without manual state management
"""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .core_types import ModuleType


class ScopeType(StrEnum):
    """Behavioral enum for different code scope types.

    Each scope type has semantic meaning for SDA pattern detection.
    Different scopes suggest different patterns and violation contexts.

    SDA Principle: Enums know their own behavior instead of external logic.
    """

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    CONDITIONAL = "conditional"
    TRY_BLOCK = "try_block"

    @property
    def analysis_priority(self) -> int:
        """Domain intelligence: analysis priority for different scope types."""
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
        """Does this scope type create a new naming/variable scope?"""
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

    Represents a single level of code nesting (function, class, etc.) with
    semantic intelligence about what patterns and violations are likely within.

    SDA Principle: Rich domain models that understand their own meaning.
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
        """Domain intelligence: does scope name suggest serialization activity?"""
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
        """Domain intelligence: does scope suggest infrastructure/boundary code?"""
        # Type-level boundary detection (try blocks handle errors at boundaries)
        if self.scope_type.suggests_infrastructure:
            return True

        # Name-based boundary detection
        boundary_patterns = ["client", "adapter", "wrapper", "handler", "connector"]
        return any(pattern in self.name.lower() for pattern in boundary_patterns)

    @computed_field
    @property
    def likely_contains_business_logic(self) -> bool:
        """Domain intelligence: does this scope likely contain business logic?"""
        return self.scope_type.suggests_business_logic and not self.is_boundary_scope and not self.is_validation_scope


class RichAnalysisContext(BaseModel):
    """Immutable analysis context that flows through AST traversal.

    This is the core of SDA's stateful analysis approach. Instead of global variables
    or mutable state, we pass immutable context through the analysis pipeline.
    The context accumulates semantic understanding of code structure and provides
    rich intelligence about the current analysis location.

    SDA Principles Demonstrated:
    - Immutability: All state changes via model_copy(), never direct mutation
    - Rich Context: Far beyond simple "current file" - semantic understanding
    - Computed Intelligence: Derived facts computed automatically from base data
    - Type Safety: All context information is properly typed and validated
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
        """The innermost scope we're currently analyzing."""
        return self.scope_stack[-1] if self.scope_stack else None

    @computed_field
    @property
    def nesting_level(self) -> int:
        """How deeply nested are we in scope hierarchy?"""
        return len(self.scope_stack)

    @computed_field
    @property
    def in_serialization_context(self) -> bool:
        """Domain intelligence: are we in serialization-related code?"""
        return any(scope.is_serialization_scope for scope in self.scope_stack)

    @computed_field
    @property
    def in_validation_context(self) -> bool:
        """Domain intelligence: are we in validation-related code?"""
        return any(scope.is_validation_scope for scope in self.scope_stack)

    @computed_field
    @property
    def in_boundary_context(self) -> bool:
        """Domain intelligence: are we in infrastructure/boundary code?"""
        # Multiple indicators can suggest boundary context
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
        """Name of current function scope, empty string if not in function."""
        function_scopes = [s for s in self.scope_stack if s.scope_type == ScopeType.FUNCTION]
        return function_scopes[-1].name if function_scopes else ""

    @computed_field
    @property
    def current_class_name(self) -> str:
        """Name of current class scope, empty string if not in class."""
        class_scopes = [s for s in self.scope_stack if s.scope_type == ScopeType.CLASS]
        return class_scopes[-1].name if class_scopes else ""

    def _file_suggests_boundary(self) -> bool:
        """Helper: does the filename suggest boundary/infrastructure code?"""
        file_path = Path(self.current_file)
        boundary_patterns = ["client", "adapter", "wrapper", "config", "settings"]
        return any(pattern in file_path.name.lower() for pattern in boundary_patterns)

    def enter_scope(self, scope: AnalysisScope) -> "RichAnalysisContext":
        """Enter a new scope, returning updated immutable context.

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

        Returns:
            New context with top scope removed, or same context if stack empty

        SDA Principle: Immutable updates ensure predictable state management
        """
        if not self.scope_stack:
            return self
        new_stack = self.scope_stack[:-1]
        return self.model_copy(update={"scope_stack": new_stack})
