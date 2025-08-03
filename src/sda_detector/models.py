"""Domain models for SDA architecture detection.

These models embody the core SDA principle: data drives behavior.
Each model contains ALL the logic for its domain concept, using
computed fields, validation, and methods to eliminate procedural logic.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field


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


class ViolationType(StrEnum):
    """Enumeration of architectural patterns that violate SDA principles.

    These patterns indicate places where business logic is implemented
    using procedural/imperative patterns instead of being encoded into
    the type system using Pydantic models and computed fields.

    Each violation type represents a specific anti-pattern that can
    usually be refactored into a more type-driven approach.
    """

    # Core SDA violations - logic that should be in the type system
    BUSINESS_CONDITIONALS = "business_conditionals"  # if/elif for business rules
    ISINSTANCE_VIOLATIONS = "isinstance_violations"  # Runtime type checking
    HASATTR_VIOLATIONS = "hasattr_violations"  # Attribute existence checks
    GETATTR_VIOLATIONS = "getattr_violations"  # Dynamic attribute access
    DICT_GET_VIOLATIONS = "dict_get_violations"  # dict.get() instead of typed models
    TRY_EXCEPT_VIOLATIONS = "try_except_violations"  # Exception handling for control flow

    # Type system violations - missing type information
    ANY_TYPE_USAGE = "any_type_usage"  # Using Any type annotation
    MISSING_FIELD_CONSTRAINTS = "missing_field_constraints"  # Fields without validation
    PRIMITIVE_OBSESSION = "primitive_obsession"  # Raw str/int instead of value objects
    ENUM_VALUE_UNWRAPPING = "enum_value_unwrapping"  # .value calls on StrEnum/Enum
    MISSING_MODEL_CONFIG = "missing_model_config"  # No model configuration
    NO_FORWARD_REFS = "no_forward_refs"  # Missing forward references
    MANUAL_VALIDATION = "manual_validation"  # Hand-written validation instead of Pydantic
    ANEMIC_SERVICES = "anemic_services"  # Services that are just bags of functions
    MANUAL_JSON_SERIALIZATION = "manual_json_serialization"  # Manual json.dumps/loads instead of Pydantic


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


class Finding(BaseModel):
    """Represents a single architectural pattern detected in the codebase.

    A Finding is an immutable record of something we observed - either a violation
    of SDA principles or a positive pattern that aligns with SDA.

    This is pure data with computed properties, following SDA principles.
    The model teaches us what constitutes a finding and how to display it.

    Attributes:
        file_path: Which file the pattern was found in
        line_number: Which line in the file (for navigation)
        description: Human-readable description of what was found
    """

    model_config = ConfigDict(frozen=True)

    file_path: str = Field(description="Path to the file containing this finding")
    line_number: int = Field(ge=0, description="Line number where pattern was found")
    description: str = Field(min_length=1, description="Description of the pattern found")

    @computed_field
    @property
    def location(self) -> str:
        """Computed property that formats file location for display.

        This is a SDA pattern - instead of having a separate function
        format_location(finding), we encode the formatting logic
        directly into the domain model using a computed field.

        Returns:
            Formatted string like "file.py:123" for easy navigation
        """
        return f"{self.file_path}:{self.line_number}"


class AnalysisConfig(BaseModel):
    """Configuration options for AST analysis behavior.

    Currently minimal, but designed to be extensible for future analysis modes
    like strict mode, legacy compatibility mode, or domain-specific rulesets.
    """

    model_config = ConfigDict(frozen=True)

    classify_modules: bool = True  # Enable module type classification


class AnalysisContext(BaseModel):
    """Immutable context state for AST analysis with computed behavioral properties.

    This model demonstrates core SDA principles:
    1. Immutable state using frozen=True
    2. Computed fields that derive behavior from data
    3. Type-driven logic instead of conditionals
    4. Rich domain model that teaches about analysis context

    The context tracks where we are in the AST traversal and provides
    smart contextual behavior through computed fields.
    """

    model_config = ConfigDict(frozen=True)

    current_file: str = Field(default="", description="File currently being analyzed")
    current_class: str = Field(default="", description="Class currently being analyzed")
    current_function: str = Field(default="", description="Function currently being analyzed")
    in_enum_class: bool = Field(default=False, description="Whether we're inside an enum class")
    classifier: Any = Field(default=None, description="Module classifier for context-aware analysis")

    @computed_field
    @property
    def module_type(self) -> ModuleType:
        """Classify the current module type using the embedded classifier.

        This computed field demonstrates SDA: instead of having separate
        classification logic, the context model knows its own module type.
        """
        if self.classifier is None:
            return ModuleType.MIXED
        result = self.classifier.classify_module(self.current_file)
        return result if isinstance(result, ModuleType) else ModuleType.MIXED

    @computed_field
    @property
    def is_boundary_context(self) -> bool:
        """Determine if we're analyzing boundary/infrastructure code.

        Boundary contexts (infrastructure, tooling, framework integration)
        need different analysis rules - they may legitimately use patterns
        like hasattr() and try/except that would be anti-patterns in domain code.

        This is contextual intelligence encoded in the type system.
        """
        return self.module_type in [ModuleType.INFRASTRUCTURE, ModuleType.TOOLING, ModuleType.FRAMEWORK]

    @computed_field
    @property
    def is_type_checking_context(self) -> bool:
        """Detect if we're in a TYPE_CHECKING context.

        TYPE_CHECKING blocks are used for imports that are only needed
        for type hints, not runtime. This is a positive pattern.
        """
        return "TYPE_CHECKING" in self.current_file


class ArchitectureReport(BaseModel):
    """Comprehensive architecture analysis report."""

    model_config = ConfigDict(frozen=True)

    violations: dict[ViolationType, list[Finding]]
    patterns: dict[PositivePattern, list[Finding]]

    @computed_field
    @property
    def total_violations(self) -> int:
        """Total count of SDA violations found across all types."""
        return sum(len(findings) for findings in self.violations.values())

    @computed_field
    @property
    def total_patterns(self) -> int:
        """Total count of positive SDA patterns found across all types."""
        return sum(len(findings) for findings in self.patterns.values())

    @computed_field
    @property
    def files_analyzed(self) -> int:
        """Count of unique files analyzed - pure observation."""
        all_files: set[str] = set()
        for findings in self.violations.values():
            all_files.update(f.file_path for f in findings)
        for findings in self.patterns.values():
            all_files.update(f.file_path for f in findings)
        return len(all_files)

    @computed_field
    @property
    def pattern_distribution(self) -> dict[str, float]:
        """Observable distribution of patterns vs violations - pure observation."""
        total = self.total_patterns + self.total_violations
        if total == 0:
            return {"patterns": 0.0, "violations": 0.0}
        return {
            "patterns": self.total_patterns / total,
            "violations": self.total_violations / total,
        }

    @computed_field
    @property
    def module_type(self) -> ModuleType:
        """Classify what type of module this is."""
        return self._detect_module_type()

    def _detect_module_type(self) -> ModuleType:
        """Detect module type from analysis findings."""
        # Import here to avoid circular import
        from .services import ModuleClassifier

        # Check if any finding is from a classified file
        all_findings = []
        for finding_list in self.violations.values():
            all_findings.extend(finding_list)
        for finding_list in self.patterns.values():
            all_findings.extend(finding_list)

        if not all_findings:
            return ModuleType.MIXED

        # Use classifier on sample file
        sample_file = all_findings[0].file_path
        classifier = ModuleClassifier()
        result = classifier.classify_module(sample_file)
        return result if isinstance(result, ModuleType) else ModuleType.MIXED


class DisplayConfig(BaseModel):
    """Domain model for report display configuration."""

    model_config = ConfigDict(frozen=True)

    @computed_field
    @property
    def summary_item_limit(self) -> int:
        """How many items to show in summary before truncating."""
        return 2

    @computed_field
    @property
    def separator_length(self) -> int:
        """Length of separator lines."""
        return 70

    @computed_field
    @property
    def field_width(self) -> int:
        """Width for field name alignment."""
        return 25

    @computed_field
    @property
    def count_width(self) -> int:
        """Width for count alignment."""
        return 3


class ReportFormatter(BaseModel):
    """Domain model that handles report formatting logic."""

    model_config = ConfigDict(frozen=True)

    config: DisplayConfig = Field(default_factory=DisplayConfig)

    @computed_field
    @property
    def violation_status_indicator(self) -> dict[bool, str]:
        """Status indicators for violations (neutral observation)."""
        return {True: "⚪", False: "🔍"}

    @computed_field
    @property
    def pattern_status_indicator(self) -> dict[bool, str]:
        """Status indicators for patterns (neutral observation)."""
        return {True: "📊", False: "⚪"}

    def format_header(self, module_name: str) -> str:
        """Format report header."""
        title = f"🧠 SDA ARCHITECTURE ANALYSIS - {module_name.upper()}"
        separator = "=" * self.config.separator_length
        return f"{title}\n{separator}"

    def format_section_header(self, title: str) -> str:
        """Format section header."""
        return title

    def format_item_line(self, name: str, count: int, status: str) -> str:
        """Format individual item line."""
        return f"  {name:{self.config.field_width}} {count:{self.config.count_width}} {status}"

    def format_finding_detail(self, finding: Finding) -> str:
        """Format finding detail line."""
        return f"    → {finding.location} - {finding.description}"

    def format_overflow_message(self, remaining_count: int) -> str:
        """Format overflow message for truncated lists."""
        return f"    → ... and {remaining_count} more"

    def should_show_overflow(self, total_count: int) -> bool:
        """Determine if overflow message should be shown."""
        return total_count > self.config.summary_item_limit
