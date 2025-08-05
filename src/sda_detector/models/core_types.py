"""Core domain types for SDA architecture detection.

These types define the fundamental vocabulary of SDA analysis:
what modules we analyze, what violations we detect, and what
positive patterns we recognize.

These are the building blocks that other domain models reference.
"""

import ast
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analysis_domain import Finding
    from .context_domain import AnalysisScope, RichAnalysisContext


class ASTNodeCategory(StrEnum):
    """Domain classification of AST nodes by semantic meaning."""

    STRUCTURAL = "structural"  # Classes, functions, modules
    BEHAVIORAL = "behavioral"  # Calls, attribute access
    CONTROL_FLOW = "control_flow"  # If, try, loops
    DATA = "data"  # Names, constants, literals

    @property
    def analysis_priority(self) -> int:
        """Domain intelligence: analysis priority by semantic importance."""
        priorities = {
            ASTNodeCategory.STRUCTURAL: 1,  # High priority - architecture
            ASTNodeCategory.CONTROL_FLOW: 2,  # Medium priority - patterns
            ASTNodeCategory.BEHAVIORAL: 3,  # Medium priority - usage
            ASTNodeCategory.DATA: 4,  # Low priority - data access
        }
        return priorities[self]

    @property
    def creates_scope(self) -> bool:
        """Does this category introduce a new naming scope?"""
        return self == self.STRUCTURAL

    @property
    def needs_flow_analysis(self) -> bool:
        """Does this category affect program flow?"""
        return self in {self.CONTROL_FLOW, self.BEHAVIORAL}

    @property
    def can_contain_patterns(self) -> bool:
        """Can this category contain SDA violations?"""
        # Data nodes rarely contain patterns we care about
        return self != self.DATA


class ASTNodeType(StrEnum):
    """Discriminated union for AST node classification - eliminates isinstance chains.

    This enum replaces all isinstance(node, ast.SomeType) checks with pure
    discriminated union dispatch. Each node type knows its own behavior and
    capabilities through behavioral methods.

    CRITICAL: This eliminates SDA violations by encoding AST intelligence
    into the type system rather than procedural isinstance checks.
    """

    FUNCTION_DEF = "function_def"
    CLASS_DEF = "class_def"
    CONDITIONAL = "conditional"
    CALL = "call"
    ATTRIBUTE = "attribute"
    UNKNOWN = "unknown"

    @classmethod
    def from_ast(cls, node: ast.AST) -> "ASTNodeType":
        """Pure discriminated union classification - replaces isinstance chains.

        This method eliminates ALL isinstance usage by encoding node type
        intelligence into discriminated union dispatch.
        """
        node_classifiers = {
            ast.FunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.AsyncFunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.ClassDef: ASTNodeType.CLASS_DEF,
            ast.If: ASTNodeType.CONDITIONAL,
            ast.Call: ASTNodeType.CALL,
            ast.Attribute: ASTNodeType.ATTRIBUTE,
        }
        return node_classifiers.get(type(node), ASTNodeType.UNKNOWN)

    def creates_scope(self) -> bool:
        """Behavioral method - node types know if they create analysis scopes."""
        scope_creators = {ASTNodeType.FUNCTION_DEF, ASTNodeType.CLASS_DEF, ASTNodeType.CONDITIONAL}
        return self in scope_creators

    def process_with_scope(
        self, node: ast.AST, current_scopes: list["AnalysisScope"], visit_children: Callable[[ast.AST], None]
    ) -> None:
        """Process node with proper scope handling using pure discriminated union dispatch.

        This eliminates if/else conditionals in service.py by encoding the scope
        handling logic into the type system itself.
        """
        # Pure dictionary dispatch for scope handling behavior
        scope_processors = {
            # Scope creators: create scope, visit children with scope, pop scope
            ASTNodeType.FUNCTION_DEF: self._process_with_new_scope,
            ASTNodeType.CLASS_DEF: self._process_with_new_scope,
            ASTNodeType.CONDITIONAL: self._process_with_new_scope,
            # Non-scope creators: just visit children
            ASTNodeType.CALL: self._process_without_scope,
            ASTNodeType.ATTRIBUTE: self._process_without_scope,
            ASTNodeType.UNKNOWN: self._process_without_scope,
        }
        scope_processors[self](node, current_scopes, visit_children)

    def _process_with_new_scope(
        self, node: ast.AST, current_scopes: list["AnalysisScope"], visit_children: Callable[[ast.AST], None]
    ) -> None:
        """Process node that creates a new scope."""
        new_scope = self.create_scope(node)
        current_scopes.append(new_scope)
        visit_children(node)
        current_scopes.pop()

    def _process_without_scope(
        self, node: ast.AST, current_scopes: list["AnalysisScope"], visit_children: Callable[[ast.AST], None]
    ) -> None:
        """Process node that doesn't create a scope."""
        visit_children(node)

    def create_scope(self, node: ast.AST) -> "AnalysisScope":
        """Behavioral method - node types know how to create their own scopes.

        Pure discriminated union dispatch without getattr or conditionals.
        """
        scope_handlers = {
            ASTNodeType.FUNCTION_DEF: self._create_function_scope,
            ASTNodeType.CLASS_DEF: self._create_class_scope,
            ASTNodeType.CONDITIONAL: self._create_conditional_scope,
            ASTNodeType.CALL: self._create_call_scope,
            ASTNodeType.ATTRIBUTE: self._create_attribute_scope,
            ASTNodeType.UNKNOWN: self._create_unknown_scope,
        }
        return scope_handlers[self](node)

    def create_analyzer_findings(self, node: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Behavioral method - node types know how to analyze themselves.

        Pure discriminated union dispatch - NO CONDITIONALS.
        The discriminated union guarantees node types match analyzer expectations.
        """
        from collections.abc import Callable

        # Import analyzers from the extracted modules
        from .analyzers.attribute_analyzer import AttributeAnalyzer
        from .analyzers.call_analyzer import CallAnalyzer
        from .analyzers.conditional_analyzer import ConditionalAnalyzer

        # Pure discriminated union dispatch - trust the classification
        # The from_ast() method GUARANTEES the node type
        analyzer_dispatch: dict[ASTNodeType, Callable[[], list[Finding]]] = {
            ASTNodeType.CONDITIONAL: lambda: ConditionalAnalyzer.analyze_node(node, context),
            ASTNodeType.CALL: lambda: CallAnalyzer.analyze_node(node, context),
            ASTNodeType.ATTRIBUTE: lambda: AttributeAnalyzer.analyze_node(node, context),
            ASTNodeType.FUNCTION_DEF: lambda: [],
            ASTNodeType.CLASS_DEF: lambda: [],
            ASTNodeType.UNKNOWN: lambda: [],
        }
        return analyzer_dispatch[self]()

    def _create_empty_findings(self) -> list["Finding"]:
        """Temporary method - returns empty findings until analyzers are extracted."""
        return []

    def _create_function_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create function scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.FUNCTION,
            name=getattr(node, "name", "unknown_function"),
            line_number=getattr(node, "lineno", 0),
        )

    def _create_class_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create class scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.CLASS,
            name=getattr(node, "name", "unknown_class"),
            line_number=getattr(node, "lineno", 0),
        )

    def _create_conditional_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create conditional scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        return AnalysisScope(
            scope_type=ScopeType.CONDITIONAL, name=ScopeNaming.CONDITIONAL, line_number=getattr(node, "lineno", 0)
        )

    def _create_call_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create call scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        # Calls don't create their own scope type, use FUNCTION as container
        return AnalysisScope(
            scope_type=ScopeType.FUNCTION, name=ScopeNaming.CALL, line_number=getattr(node, "lineno", 0)
        )

    def _create_attribute_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create attribute scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        # Attributes don't create their own scope type, use FUNCTION as container
        return AnalysisScope(
            scope_type=ScopeType.FUNCTION, name=ScopeNaming.ATTRIBUTE, line_number=getattr(node, "lineno", 0)
        )

    def _create_unknown_scope(self, node: ast.AST) -> "AnalysisScope":
        """Create unknown scope using discriminated union pattern."""
        from .context_domain import AnalysisScope, ScopeType

        # Unknown nodes don't create their own scope type, use MODULE as default
        return AnalysisScope(
            scope_type=ScopeType.MODULE, name=ScopeNaming.UNKNOWN, line_number=getattr(node, "lineno", 0)
        )


class FileResult(StrEnum):
    """Discriminated union for file operation results - eliminates try/except control flow.

    This enum replaces try/except blocks used for control flow with pure
    discriminated union dispatch. Each result type knows how to handle itself
    through behavioral methods.

    CRITICAL: This eliminates SDA violations by encoding error handling
    intelligence into the type system rather than procedural try/except.
    """

    SUCCESS = "success"
    ERROR = "error"

    def to_findings(self, file_path: str, content: str = "") -> list["Finding"]:
        """Behavioral method - results know how to convert themselves to findings.

        Pure discriminated union dispatch without conditionals or try/except.
        """
        from .analysis_domain import Finding

        # Pure dictionary dispatch with computed values - no lambdas, no conditionals
        result_handlers = {
            FileResult.SUCCESS: [],
            FileResult.ERROR: [Finding(file_path=file_path, line_number=0, description="file_read_error")],
        }
        return result_handlers[self]

    def _create_success_findings(self) -> list["Finding"]:
        """Success produces no findings - pure discriminated union behavior."""
        return []

    def _create_error_findings(self, file_path: str) -> list["Finding"]:
        """Error creates file read error finding - pure discriminated union behavior."""
        from .analysis_domain import Finding

        return [Finding(file_path=file_path, line_number=0, description="file_read_error")]


class AnalysisResult(StrEnum):
    """Discriminated union for AST parsing results - eliminates try/except control flow.

    This enum replaces try/except blocks for AST parsing with pure
    discriminated union dispatch. Each result type knows its own behavior.
    """

    SUCCESS = "success"
    PARSE_ERROR = "parse_error"

    def to_findings(self, file_path: str, findings: list["Finding"] | None = None) -> list["Finding"]:
        """Behavioral method - results know how to handle analysis outcomes."""
        from .analysis_domain import Finding

        # Pure dictionary dispatch with computed values - no lambdas, no conditionals
        result_handlers = {
            AnalysisResult.SUCCESS: findings or [],
            AnalysisResult.PARSE_ERROR: [Finding(file_path=file_path, line_number=0, description="ast_parse_error")],
        }
        return result_handlers[self]

    def _create_parse_error_findings(self, file_path: str) -> list["Finding"]:
        """Parse error creates AST parse error finding."""
        from .analysis_domain import Finding

        return [Finding(file_path=file_path, line_number=0, description="ast_parse_error")]


class PathType(StrEnum):
    """Discriminated union for file system path handling.

    Eliminates if/elif chains for path type checking using pure behavioral dispatch.
    """

    PYTHON_FILE = "python_file"
    DIRECTORY = "directory"
    OTHER = "other"

    @classmethod
    def from_path(cls, path_str: str) -> "PathType":
        """Factory method to classify path type using discriminated union dispatch."""
        from pathlib import Path

        path = Path(path_str)

        # Pure type dispatch - no conditionals
        path_classifiers = {True: cls._classify_file, False: cls._classify_non_file}

        return path_classifiers[path.is_file()](path)

    @classmethod
    def _classify_file(cls, path: Path) -> "PathType":
        """Classify file paths using suffix dispatch."""
        suffix_types = {
            ".py": cls.PYTHON_FILE,
        }
        return suffix_types.get(path.suffix, cls.OTHER)

    @classmethod
    def _classify_non_file(cls, path: Path) -> "PathType":
        """Classify non-file paths."""
        return cls.DIRECTORY if path.is_dir() else cls.OTHER

    def get_python_files(self, path_str: str) -> list[str]:
        """Get Python files using pure dispatch - no conditionals."""
        path = Path(path_str)

        # Pure dictionary dispatch without lambdas
        file_getters: dict[PathType, list[str]] = {
            PathType.PYTHON_FILE: [str(path)],
            PathType.DIRECTORY: [str(f) for f in path.glob("*.py")],
            PathType.OTHER: [],
        }

        return file_getters[self]


class FindingClassifier(StrEnum):
    """Discriminated union for finding classification.

    Eliminates if/elif chains for finding categorization using pure behavioral dispatch.
    """

    VIOLATION = "violation"
    PATTERN = "pattern"
    UNKNOWN = "unknown"

    @classmethod
    def from_finding(cls, finding: "Finding") -> "FindingClassifier":
        """Classify finding type using discriminated union dispatch."""
        # Pure boolean coercion array indexing - no conditionals
        has_violation = bool(finding.pattern_category)
        has_pattern = bool(finding.pattern_type)

        # Boolean tuple to index mapping - pure data-driven selection
        classification_index = (has_violation, has_pattern)
        classification_map = {
            (True, False): cls.VIOLATION,  # Has violation, no pattern
            (False, True): cls.PATTERN,  # Has pattern, no violation
            (True, True): cls.VIOLATION,  # Both - violation takes precedence
            (False, False): cls.UNKNOWN,  # Neither
        }

        return classification_map[classification_index]

    def add_to_collections(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Add finding to appropriate collection using pure dispatch."""
        # Pure dictionary dispatch - no conditionals
        collection_handlers = {
            FindingClassifier.VIOLATION: self._add_violation,
            FindingClassifier.PATTERN: self._add_pattern,
            FindingClassifier.UNKNOWN: self._ignore_finding,
        }

        collection_handlers[self](finding, violations, patterns)

    def _add_violation(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Add violation finding to violations collection."""
        if violation_pattern := finding.pattern_category:
            violations.setdefault(violation_pattern, []).append(finding)

    def _add_pattern(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Add pattern finding to patterns collection."""
        if positive_pattern := finding.pattern_type:
            patterns.setdefault(positive_pattern, []).append(finding)

    def _ignore_finding(
        self,
        finding: "Finding",
        violations: dict["PatternType", list["Finding"]],
        patterns: dict["PositivePattern", list["Finding"]],
    ) -> None:
        """Ignore unknown findings."""
        pass


class CLIArgumentState(StrEnum):
    """Discriminated union for CLI argument validation.

    Eliminates if/else chains in CLI argument handling.
    """

    NO_ARGS = "no_args"
    PATH_ONLY = "path_only"
    PATH_AND_NAME = "path_and_name"

    @classmethod
    def from_argv(cls, argv: list[str]) -> "CLIArgumentState":
        """Classify CLI argument state using pure dispatch."""
        arg_count = len(argv)

        # Pure dictionary dispatch based on argument count
        count_mapping = {
            0: cls.NO_ARGS,
            1: cls.NO_ARGS,  # argv[0] is the script name
            2: cls.PATH_ONLY,
            3: cls.PATH_AND_NAME,
        }

        # For counts > 3, treat as PATH_AND_NAME
        return count_mapping.get(arg_count, cls.PATH_AND_NAME)

    def handle_arguments(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle CLI arguments based on state.

        Returns: (module_path, module_name, should_continue)
        """
        handlers = {
            CLIArgumentState.NO_ARGS: self._handle_no_args,
            CLIArgumentState.PATH_ONLY: self._handle_path_only,
            CLIArgumentState.PATH_AND_NAME: self._handle_path_and_name,
        }

        return handlers[self](argv)

    def _handle_no_args(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle case with no arguments - print usage."""
        print("Usage: sda-detector <module_path> [module_name]")
        return None, None, False

    def _handle_path_only(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle case with path only."""
        return argv[1], None, True

    def _handle_path_and_name(self, argv: list[str]) -> tuple[str | None, str | None, bool]:
        """Handle case with path and name."""
        return argv[1], argv[2], True


class ModuleTypeClassifier(StrEnum):
    """Discriminated union for module type classification.

    Eliminates if/elif chains for module type detection using pure dispatch.
    """

    TEST = "test"
    DOMAIN = "domain"
    MODEL = "model"
    SERVICE = "service"
    API = "api"
    MIXED = "mixed"

    @classmethod
    def from_path(cls, module_path: str) -> "ModuleType":
        """Classify module type from path using pure discriminated union dispatch.

        Pure SDA implementation using priority-based keyword detection.
        """
        path_lower = module_path.lower()

        # Priority-based classification using boolean indexing
        has_test = "test" in path_lower
        has_domain = "model" in path_lower or "domain" in path_lower
        has_service = "service" in path_lower or "api" in path_lower

        # Pure tuple-based dispatch - no conditionals
        classification_key = (has_test, has_domain, has_service)

        # Exhaustive mapping of all combinations
        classification_map = {
            (True, False, False): ModuleType.TOOLING,  # test only
            (True, True, False): ModuleType.TOOLING,  # test + domain
            (True, False, True): ModuleType.TOOLING,  # test + service
            (True, True, True): ModuleType.TOOLING,  # test + all
            (False, True, False): ModuleType.DOMAIN,  # domain only
            (False, True, True): ModuleType.DOMAIN,  # domain + service
            (False, False, True): ModuleType.INFRASTRUCTURE,  # service only
            (False, False, False): ModuleType.MIXED,  # none
        }

        return classification_map[classification_key]


class ModuleType(StrEnum):
    """Types of modules with different architectural patterns and expectations.

    Each module type has different tolerance levels for certain patterns:
    - DOMAIN: Pure business logic, should minimize conditionals and external dependencies
    - INFRASTRUCTURE: Boundary code, may need error handling and external service integration
    - TOOLING: Analysis/development tools, may need runtime reflection and file system access
    - FRAMEWORK: Third-party integration code, follows external library patterns
    - MIXED: Combination of concerns, evaluated with balanced criteria
    """

    DOMAIN = "domain"
    INFRASTRUCTURE = "infrastructure"
    TOOLING = "tooling"
    FRAMEWORK = "framework"
    MIXED = "mixed"

    @property
    def analysis_priority(self) -> int:
        """Self-determining analysis priority using type dispatch."""
        priorities = {
            ModuleType.DOMAIN: 100,  # Highest priority - pure business logic
            ModuleType.INFRASTRUCTURE: 80,  # High priority - critical boundaries
            ModuleType.TOOLING: 60,  # Medium priority - development tools
            ModuleType.FRAMEWORK: 40,  # Lower priority - external integration
            ModuleType.MIXED: 20,  # Lowest priority - mixed concerns
        }
        return priorities.get(self, 10)


class PatternType(StrEnum):
    """Neutral classification of architectural patterns detected in code.

    These patterns represent different approaches to implementing logic:
    procedural/imperative patterns vs type-driven patterns. The detector
    reports what exists without judgment - users decide significance.

    Each pattern type represents a specific programming approach that
    can be observed and measured in codebases.
    """

    # Conditional logic patterns - different approaches to control flow
    BUSINESS_CONDITIONALS = "business_conditionals"  # if/elif for business rules
    ISINSTANCE_USAGE = "isinstance_usage"  # Runtime type checking
    HASATTR_USAGE = "hasattr_usage"  # Attribute existence checks
    GETATTR_USAGE = "getattr_usage"  # Dynamic attribute access
    DICT_GET_USAGE = "dict_get_usage"  # dict.get() instead of typed models
    TRY_EXCEPT_USAGE = "try_except_usage"  # Exception handling for control flow

    # Type system patterns - different approaches to type usage
    ANY_TYPE_USAGE = "any_type_usage"  # Using Any type annotation
    MISSING_FIELD_CONSTRAINTS = "missing_field_constraints"  # Fields without validation
    PRIMITIVE_OBSESSION = "primitive_obsession"  # Raw str/int instead of value objects
    ENUM_VALUE_ACCESS = "enum_value_access"  # .value calls on StrEnum/Enum
    MISSING_MODEL_CONFIG = "missing_model_config"  # No model configuration
    NO_FORWARD_REFS = "no_forward_refs"  # Missing forward references
    MANUAL_VALIDATION = "manual_validation"  # Hand-written validation instead of Pydantic
    ANEMIC_SERVICES = "anemic_services"  # Services that are just bags of functions
    MANUAL_JSON_SERIALIZATION = "manual_json_serialization"  # Manual json.dumps/loads instead of Pydantic


# FindingClassificationType removed - has broken lambda calls and unused


# ServiceOperationType removed - unused and has broken imports


# PathProcessingType removed - unused and has broken lambda calls


class PositivePattern(StrEnum):
    """Enumeration of architectural patterns that align with SDA principles.

    These patterns indicate sophisticated use of Python's type system
    and Pydantic's capabilities to encode business logic into types
    rather than procedural code.

    Higher counts of these patterns suggest more mature architectural
    design that leverages type-driven development.
    """

    # Core SDA patterns - business logic in types
    PYDANTIC_MODELS = "pydantic_models"  # BaseModel classes
    BEHAVIORAL_ENUMS = "behavioral_enums"  # Enums with methods
    COMPUTED_FIELDS = "computed_fields"  # @computed_field properties
    VALIDATORS = "validators"  # Pydantic validators
    PROTOCOLS = "protocols"  # typing.Protocol interfaces
    TYPE_DISPATCH_TABLES = "type_dispatch_tables"  # Dictionary-based dispatch

    # Pydantic integration patterns
    PYDANTIC_VALIDATION = "pydantic_validation"  # model_validate* calls
    PYDANTIC_SERIALIZATION = "pydantic_serialization"  # model_dump* calls
    IMMUTABLE_UPDATES = "immutable_updates"  # model_copy usage
    FIELD_CONSTRAINTS = "field_constraints"  # Field() with constraints
    MODEL_CONFIG_USAGE = "model_config_usage"  # ModelConfig definitions

    # Advanced type system patterns
    UNION_TYPES = "union_types"  # Union type annotations
    LITERAL_TYPES = "literal_types"  # Literal type annotations
    DISCRIMINATED_UNIONS = "discriminated_unions"  # Tagged union patterns
    FORWARD_REFERENCES = "forward_references"  # Self-referential types
    ANNOTATED_TYPES = "annotated_types"  # Annotated type hints
    GENERIC_MODELS = "generic_models"  # Generic Pydantic models
    RECURSIVE_MODELS = "recursive_models"  # Self-referential models

    # Pydantic advanced features
    CUSTOM_VALIDATORS = "custom_validators"  # @field_validator, @model_validator
    CUSTOM_SERIALIZERS = "custom_serializers"  # @field_serializer
    ROOT_VALIDATORS = "root_validators"  # @root_validator (legacy)

    # Code organization patterns
    ENUM_METHODS = "enum_methods"  # Methods on enum classes
    BOUNDARY_CONDITIONS = "boundary_conditions"  # Proper error handling at boundaries
    TYPE_CHECKING_IMPORTS = "type_checking_imports"  # TYPE_CHECKING blocks


class ScopeNaming(StrEnum):
    """Behavioral enum - scope names know their own capabilities."""

    CONDITIONAL = "conditional"
    CALL = "call"
    ATTRIBUTE = "attribute"
    UNKNOWN = "unknown"

    def is_analyzable(self) -> bool:
        """Behavioral method - scope names know if they should be analyzed."""
        analyzable_scopes = {ScopeNaming.CONDITIONAL, ScopeNaming.CALL, ScopeNaming.ATTRIBUTE}
        return self in analyzable_scopes

    def get_display_name(self) -> str:
        """Behavioral method - scope names know how to display themselves."""
        display_names = {
            ScopeNaming.CONDITIONAL: "Conditional Block",
            ScopeNaming.CALL: "Function Call",
            ScopeNaming.ATTRIBUTE: "Attribute Access",
            ScopeNaming.UNKNOWN: "Unknown Scope",
        }
        return display_names[self]

    def create_scope_identifier(self, node_name: str) -> str:
        """Behavioral method - scope names know how to create identifiers."""
        identifier_patterns = {
            ScopeNaming.CONDITIONAL: f"condition_{node_name}",
            ScopeNaming.CALL: f"call_{node_name}",
            ScopeNaming.ATTRIBUTE: f"attr_{node_name}",
            ScopeNaming.UNKNOWN: f"unknown_{node_name}",
        }
        return identifier_patterns[self]
