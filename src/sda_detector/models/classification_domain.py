"""Module classification domain intelligence - Self-Aware Path Analysis.

PURPOSE:
This module provides intelligent path and module classification, demonstrating
how domain models can encapsulate file system operations and classification logic.

SDA PRINCIPLES DEMONSTRATED:
1. **Self-Classifying Models**: ModuleClassifier determines its own type
2. **Computed Intelligence**: All derived data calculated on demand
3. **Pattern-Based Classification**: Uses sets for efficient pattern matching
4. **Boolean Coercion**: Eliminates conditionals through truthy evaluation
5. **Path Abstraction**: Wraps Path operations in domain methods

LEARNING GOALS:
- Understand how to wrap file system operations in domain models
- Learn pattern-based classification using sets and iteration
- Master boolean coercion to eliminate if/else statements
- See how computed fields provide rich derived information
- Recognize when iteration over data is acceptable (not business logic)

ARCHITECTURE NOTES:
This model shows that even file system operations can follow SDA patterns.
Instead of scattered path manipulation and classification logic, everything
is centralized in a self-aware domain model.

Teaching Example:
    >>> # Traditional approach:
    >>> if 'test' in path:
    >>>     module_type = 'tooling'
    >>> elif 'model' in path or 'domain' in path:
    >>>     module_type = 'domain'
    >>> else:
    >>>     module_type = 'mixed'
    >>> 
    >>> # SDA approach:
    >>> classifier = ModuleClassifier(path="src/models/user_domain.py")
    >>> print(classifier.classified_type)  # ModuleType.DOMAIN
    >>> print(classifier.python_files)  # ["src/models/user_domain.py"]

Key Insight:
File paths and module types are domain concepts that deserve rich models.
This eliminates scattered path manipulation throughout the codebase.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .core_types import ModuleType


class ModuleClassifier(BaseModel):
    """Domain intelligence for module classification operations.

    WHAT: A self-aware model that classifies modules by path patterns and
    provides intelligent file system operations.
    
    WHY: Module classification logic shouldn't be scattered across services.
    By centralizing it here, we ensure consistent classification and make
    the logic testable and reusable.
    
    HOW: Uses computed fields to derive module type, file lists, and path
    properties from a single input path string.
    
    Teaching Example:
        >>> # Classify a test file:
        >>> classifier = ModuleClassifier(path="tests/test_user.py")
        >>> print(classifier.classified_type)  # ModuleType.TOOLING
        >>> print(classifier.is_file)  # True
        >>> print(classifier.stem)  # "test_user"
        >>> 
        >>> # Classify a domain directory:
        >>> classifier = ModuleClassifier(path="src/domain/")
        >>> print(classifier.classified_type)  # ModuleType.DOMAIN
        >>> print(classifier.is_directory)  # True
        >>> print(classifier.python_files)  # List of all .py files
    
    SDA Pattern Demonstrated:
        Self-Analyzing Models - The model contains all logic to understand
        and classify itself, eliminating external classification services.
    """

    model_config = ConfigDict(frozen=True)

    path: str = Field(description="Path string for analysis")

    @computed_field
    @property
    def classified_type(self) -> ModuleType:
        """Domain intelligence: classify module type based on path patterns.
        
        Teaching Note: PATTERN-BASED CLASSIFICATION WITH SETS
        
        This method shows acceptable iteration in SDA:
        1. We iterate over DATA (classification patterns)
        2. Each iteration checks membership (data operation)
        3. First match wins (priority-based)
        4. Default to MIXED if no match
        
        The for loop here is NOT business logic - it's iterating
        over a data structure to find a match. This is similar to
        dictionary lookup but with pattern matching.
        
        Sets are used for O(1) membership testing with 'in'.
        """
        path_lower = self.path.lower()

        # Teaching: Pattern sets for each module type
        # Priority order: DOMAIN > INFRASTRUCTURE > TOOLING > FRAMEWORK > MIXED
        classification_patterns = {
            ModuleType.DOMAIN: {"model", "domain", "entity", "business"},
            ModuleType.INFRASTRUCTURE: {
                "redis",
                "postgres",
                "mysql",
                "database",
                "db",
                "storage",
                "cache",
                "client",
                "external",
                "api",
                "gateway",
                "adapter",
                "repository",
            },
            ModuleType.TOOLING: {"test", "tool", "script", "cli", "util", "helper"},
            ModuleType.FRAMEWORK: {"framework", "lib", "core", "base"},
        }

        # Teaching: Iteration over data structure is acceptable!
        # This is not business logic - it's pattern matching
        for module_type, patterns in classification_patterns.items():
            if any(pattern in path_lower for pattern in patterns):
                return module_type

        # Teaching: Default case - no patterns matched
        return ModuleType.MIXED

    @computed_field
    @property
    def path_obj(self) -> Path:
        """Domain intelligence: convert to Path object for operations.
        
        Teaching: Computed fields can cache expensive operations.
        Path construction happens once, then reused.
        """
        return Path(self.path)

    @computed_field
    @property
    def is_file(self) -> bool:
        """Domain intelligence: determine if this is a file."""
        return self.path_obj.is_file()

    @computed_field
    @property
    def is_directory(self) -> bool:
        """Domain intelligence: determine if this is a directory."""
        return self.path_obj.is_dir()

    @computed_field
    @property
    def python_files(self) -> list[str]:
        """Domain intelligence: get Python files based on path type.

        Teaching Note: BOOLEAN COERCION PATTERN
        
        This shows how to eliminate if/else using boolean coercion:
        1. Create lists conditionally (empty if condition false)
        2. Use 'or' operator for precedence (first truthy wins)
        
        The pattern:
            result = [value] if condition else []
        
        Creates a list with one item if true, empty if false.
        Empty lists are falsy, so 'or' picks the first non-empty.
        
        Files take precedence over directories in the resolution.
        """
        # Teaching: Boolean coercion - create lists based on conditions
        file_result = [str(self.path_obj)] if self.is_file else []  # Single file or empty
        directory_result = [str(f) for f in self.path_obj.glob("*.py")] if self.is_directory else []  # All .py files or empty

        # Teaching: 'or' operator for precedence - first non-empty list wins
        # This gives files priority over directories
        return file_result or directory_result

    @computed_field
    @property
    def stem(self) -> str:
        """Domain intelligence: get the path stem for naming."""
        return self.path_obj.stem

    def create_relative_path(self, target_path: str, module_name: str) -> str:
        """Domain intelligence: create relative path based on context.

        Teaching Note: CONDITIONAL EXPRESSION (TERNARY)
        
        Python's conditional expression (x if condition else y) is
        acceptable in SDA when:
        1. It's a simple value selection
        2. Not complex business logic
        3. Makes code more readable
        
        This determines package path structure based on whether
        target is a file (has suffix) or directory (no suffix).
        """
        target = Path(target_path)

        # Teaching: Conditional expression for path construction
        # If target has suffix (is file), use parent dir; else use target itself
        package_path = str(target.parent / module_name) if target.suffix else str(target / module_name)

        # Teaching: Path objects know how to make themselves relative
        # This is delegation to Path's intelligence, not our logic
        return str(Path(package_path).relative_to(Path.cwd()))
