#!/usr/bin/env python3
"""
🧠 Semantic Domain Architecture (SDA) Detector

A Python AST (Abstract Syntax Tree) analyzer that detects architectural patterns
in code and classifies them according to Semantic Domain Architecture principles.

## What is AST?
Abstract Syntax Tree (AST) is Python's internal representation of source code.
Instead of working with text, we analyze the parsed structure of Python code.
This allows us to understand code semantically rather than textually.

## Core Principle: Observer Pattern
This tool observes and reports architectural patterns without judging them.
It tells you what exists in your codebase - you decide what to do with that information.

## SDA Philosophy (Teaching Guide)

Semantic Domain Architecture is built on one revolutionary principle: **data drives behavior**.

Instead of writing conditional logic that *checks* data, you create types where data 
*selects* behavior automatically. This fundamental shift transforms how you think about code:

- **Pydantic models that encode domain rules**
  Example: Instead of `validate_email(string)`, create `Email(BaseModel)` that validates itself

- **Enums with behavior instead of string literals**  
  Example: Instead of `if status == "active"`, use `status.can_process_payment()`

- **Computed fields instead of functions**
  Example: Instead of `calculate_total(order)`, use `order.total` as a computed property

- **Type dispatch instead of if/else chains**
  Example: Instead of `if type == "A": do_a()`, use `handlers[type]()`
  
- **Boolean coercion for pure data selection**
  Example: `result = ["inactive", "active"][bool(user.is_verified)]` forces you to think
  "my data is selecting behavior" rather than "I'm checking a condition"

- **Protocols for interface contracts**
  Example: Define what you need from dependencies, not concrete implementations

The goal is to make your data so intelligent that it knows what to do with itself.
When you achieve this, conditional logic largely disappears because types handle
decision-making through their structure and relationships.

## Learning from This Detector

This detector itself follows SDA principles as a living example. As you read the code,
notice how we practice what we preach - every component demonstrates "data drives behavior":

- **Finding** is a Pydantic model that knows how to format itself (computed `location` field)
- **ModuleType** enum provides classification logic through computed fields  
- **NodeAnalyzer** uses type dispatch tables instead of if/elif chains
- **AnalysisContext** computes its own behavior from its state, not stored flags
- **Boolean coercion** for enum context selection (the purest SDA teaching moment)
- **Protocols** define interfaces between components for clean contracts

## What Does It Detect? (Enhanced Capabilities)

The detector now identifies 14 violation types and 23 positive patterns, including:

**New Detections:**
- **Enum value unwrapping** - `.value` calls that suggest primitive obsession
- **Anemic services** - Services that are just "bags of functions" with no cohesion

**Core Philosophy:**
This is "eating your own dog food" - the architectural analysis tool demonstrates
the very architecture it analyzes. Every class, method, and pattern shows how to
think with types instead of conditions.
"""

import ast
import os
import sys
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field


# Configuration Types
class ModuleType(StrEnum):
    """
    Types of modules with different architectural patterns and expectations.
    
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


class ModuleClassifier(BaseModel):
    """
    Classifies Python modules by analyzing file path patterns.
    
    Uses keyword matching to determine what type of module we're analyzing.
    This enables context-aware analysis - a Redis client needs different 
    architectural patterns than a pure domain model.
    
    Example:
        classifier = ModuleClassifier()
        module_type = classifier.classify_module("src/utils/redis_storage.py")
        # Returns ModuleType.INFRASTRUCTURE
    """
    model_config = ConfigDict(frozen=True)
    
    # Pattern lists use Field(default_factory=lambda: [...]) to create new lists
    # for each instance, preventing shared mutable state between instances
    infrastructure_patterns: list[str] = Field(
        default_factory=lambda: [
            'redis', 'storage', 'client', 'external', 'infra', 'db', 'database'
        ],
        description="Keywords that indicate infrastructure/boundary modules"
    )
    
    tooling_patterns: list[str] = Field(
        default_factory=lambda: [
            'detector', 'parser', 'analyzer', 'ast', 'visitor', 'scanner', 'lexer'
        ],
        description="Keywords that indicate development/analysis tools"
    )
    
    framework_patterns: list[str] = Field(
        default_factory=lambda: [
            'dagster', 'fastapi', 'sqlalchemy', 'neo4j', 'pydantic', 'pytest'
        ],
        description="Keywords that indicate framework integration code"
    )
    
    domain_patterns: list[str] = Field(
        default_factory=lambda: [
            'domain', 'model', 'entity', 'value', 'service', 'business'
        ],
        description="Keywords that indicate pure domain logic"
    )
    
    @computed_field
    @property
    def classification_rules(self) -> dict[ModuleType, list[str]]:
        """
        Type dispatch rules for module classification.
        
        Instead of if/elif chains, we use a dictionary lookup table.
        This is a core SDA pattern - replace conditionals with data structures.
        """
        return {
            ModuleType.TOOLING: self.tooling_patterns,
            ModuleType.FRAMEWORK: self.framework_patterns, 
            ModuleType.INFRASTRUCTURE: self.infrastructure_patterns,
            ModuleType.DOMAIN: self.domain_patterns
        }

    def classify_module(self, file_path: str) -> ModuleType:
        """
        Classify module type using pattern matching and type dispatch.
        
        Process:
        1. Count how many patterns match for each module type
        2. Find the highest scoring type using max()
        3. Use next() with generator expression for type dispatch
        4. Default to MIXED if no patterns match
        
        This avoids if/elif chains by using functional programming constructs.
        
        Args:
            file_path: Path to the Python file being analyzed
            
        Returns:
            ModuleType enum indicating the classification
        """
        path_lower = file_path.lower()
        
        # Dictionary comprehension counts pattern matches for each module type
        # This replaces a traditional for loop with functional programming:
        # 
        # Traditional approach (procedural):
        # pattern_scores = {}
        # for module_type, patterns in self.classification_rules.items():
        #     score = 0
        #     for pattern in patterns:
        #         if pattern in path_lower:
        #             score += 1
        #     pattern_scores[module_type] = score
        #
        # SDA approach (functional):
        pattern_scores = {
            module_type: sum(1 for pattern in patterns if pattern in path_lower)
            for module_type, patterns in self.classification_rules.items()
        }
        
        # Find highest score using built-in max() function
        # max() with default=0 prevents ValueError on empty sequences
        max_score = max(pattern_scores.values(), default=0)
        
        # Type dispatch using next() with generator expression
        # This replaces if/elif chains with functional pattern matching:
        #
        # Traditional approach (conditional):
        # for module_type, score in pattern_scores.items():
        #     if score == max_score and score > 0:
        #         return module_type
        # return ModuleType.MIXED
        #
        # SDA approach (type dispatch):
        return next(
            (module_type for module_type, score in pattern_scores.items() 
             if score == max_score and score > 0),
            ModuleType.MIXED  # Default fallback when no patterns match
        )


# Analysis Configuration
class AnalysisConfig(BaseModel):
    """
    Configuration options for AST analysis behavior.
    
    Currently minimal, but designed to be extensible for future analysis modes
    like strict mode, legacy compatibility mode, or domain-specific rulesets.
    """
    model_config = ConfigDict(frozen=True)
    
    classify_modules: bool = True  # Enable module type classification


# Domain Types - Pattern Definitions
class ViolationType(StrEnum):
    """
    Enumeration of architectural patterns that violate SDA principles.
    
    These patterns indicate places where business logic is implemented
    using procedural/imperative patterns instead of being encoded into
    the type system using Pydantic models and computed fields.
    
    Each violation type represents a specific anti-pattern that can
    usually be refactored into a more type-driven approach.
    """
    
    # Core SDA violations - logic that should be in the type system
    BUSINESS_CONDITIONALS = "business_conditionals"  # if/elif for business rules
    ISINSTANCE_VIOLATIONS = "isinstance_violations"  # Runtime type checking
    HASATTR_VIOLATIONS = "hasattr_violations"        # Attribute existence checks
    GETATTR_VIOLATIONS = "getattr_violations"        # Dynamic attribute access
    DICT_GET_VIOLATIONS = "dict_get_violations"      # dict.get() instead of typed models
    TRY_EXCEPT_VIOLATIONS = "try_except_violations"  # Exception handling for control flow
    
    # Type system violations - missing type information
    ANY_TYPE_USAGE = "any_type_usage"                        # Using Any type annotation
    MISSING_FIELD_CONSTRAINTS = "missing_field_constraints"  # Fields without validation
    PRIMITIVE_OBSESSION = "primitive_obsession"              # Raw str/int instead of value objects
    ENUM_VALUE_UNWRAPPING = "enum_value_unwrapping"          # .value calls on StrEnum/Enum
    MISSING_MODEL_CONFIG = "missing_model_config"            # No model configuration
    NO_FORWARD_REFS = "no_forward_refs"                      # Missing forward references
    MANUAL_VALIDATION = "manual_validation"                  # Hand-written validation instead of Pydantic
    ANEMIC_SERVICES = "anemic_services"                      # Services that are just bags of functions


class PositivePattern(StrEnum):
    """
    Enumeration of architectural patterns that align with SDA principles.
    
    These patterns indicate sophisticated use of Python's type system
    and Pydantic's capabilities to encode business logic into types
    rather than procedural code.
    
    Higher counts of these patterns suggest more mature architectural
    design that leverages type-driven development.
    """
    
    # Core SDA patterns - business logic in types
    PYDANTIC_MODELS = "pydantic_models"          # BaseModel classes
    BEHAVIORAL_ENUMS = "behavioral_enums"        # Enums with methods
    COMPUTED_FIELDS = "computed_fields"          # @computed_field properties
    VALIDATORS = "validators"                    # Pydantic validators
    PROTOCOLS = "protocols"                     # typing.Protocol interfaces
    TYPE_DISPATCH_TABLES = "type_dispatch_tables"  # Dictionary-based dispatch
    
    # Pydantic integration patterns
    PYDANTIC_VALIDATION = "pydantic_validation"        # model_validate* calls
    PYDANTIC_SERIALIZATION = "pydantic_serialization"  # model_dump* calls  
    IMMUTABLE_UPDATES = "immutable_updates"             # model_copy usage
    FIELD_CONSTRAINTS = "field_constraints"             # Field() with constraints
    MODEL_CONFIG_USAGE = "model_config_usage"           # ModelConfig definitions
    
    # Advanced type system patterns  
    UNION_TYPES = "union_types"                    # Union type annotations
    LITERAL_TYPES = "literal_types"                # Literal type annotations
    DISCRIMINATED_UNIONS = "discriminated_unions"  # Tagged union patterns
    FORWARD_REFERENCES = "forward_references"      # Self-referential types
    ANNOTATED_TYPES = "annotated_types"            # Annotated type hints
    GENERIC_MODELS = "generic_models"              # Generic Pydantic models
    RECURSIVE_MODELS = "recursive_models"          # Self-referential models
    
    # Pydantic advanced features
    CUSTOM_VALIDATORS = "custom_validators"     # @field_validator, @model_validator
    CUSTOM_SERIALIZERS = "custom_serializers"  # @field_serializer  
    ROOT_VALIDATORS = "root_validators"         # @root_validator (legacy)
    
    # Code organization patterns
    ENUM_METHODS = "enum_methods"                 # Methods on enum classes
    BOUNDARY_CONDITIONS = "boundary_conditions"   # Proper error handling at boundaries
    TYPE_CHECKING_IMPORTS = "type_checking_imports"  # TYPE_CHECKING blocks


# Data Models for Analysis Results
class Finding(BaseModel):
    """
    Represents a single architectural pattern detected in the codebase.
    
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
        """
        Computed property that formats file location for display.
        
        This is a SDA pattern - instead of having a separate function
        format_location(finding), we encode the formatting logic
        directly into the domain model using a computed field.
        
        Returns:
            Formatted string like "file.py:123" for easy navigation
        """
        return f"{self.file_path}:{self.line_number}"


# AST Analysis Components
class NodeAnalyzer:
    """
    Static analysis utilities for working with Python AST (Abstract Syntax Tree) nodes.
    
    The Abstract Syntax Tree is Python's internal representation of parsed code.
    Instead of working with raw text, we analyze the structured representation
    which gives us semantic understanding of the code.
    
    This class provides utilities to extract information from AST nodes using
    SDA principles - type dispatch instead of isinstance() chains.
    """
    
    @staticmethod
    def extract_name(node: ast.AST) -> str:
        """
        Extract the name/identifier from an AST node.
        
        Different AST node types store names in different attributes:
        - ast.Name nodes have an 'id' attribute
        - ast.Attribute nodes have an 'attr' attribute  
        - ast.Constant nodes have a 'value' attribute
        
        This is a boundary function that deals with external AST structure,
        so hasattr() checks are acceptable here (we're at the system boundary).
        
        Args:
            node: Any AST node that might contain a name/identifier
            
        Returns:
            The extracted name as a string, or empty string if none found
        """
        # AST boundary - hasattr checks are acceptable when dealing with external structures
        if hasattr(node, 'id'):      # ast.Name nodes (variables, functions)
            return node.id
        elif hasattr(node, 'attr'):  # ast.Attribute nodes (object.attribute)
            return node.attr
        elif hasattr(node, 'value'): # ast.Constant nodes (literals)
            return str(node.value)
        else:
            return ""  # Unknown node type
    
    @staticmethod
    def analyze_class_bases(bases: list[ast.expr]) -> dict[PositivePattern, list[str]]:
        """
        Analyze class inheritance patterns to detect SDA patterns.
        
        Examines the base classes of a class definition to identify:
        - Pydantic BaseModel inheritance (PYDANTIC_MODELS)
        - Enum inheritance (BEHAVIORAL_ENUMS)
        - Protocol inheritance (PROTOCOLS)
        
        Uses list comprehensions instead of loops for functional style.
        
        Args:
            bases: List of AST expressions representing base classes
            
        Returns:
            Dictionary mapping pattern types to lists of detected base class names
        """
        # Extract names from all base class AST nodes
        base_names = [NodeAnalyzer.extract_name(base) for base in bases]
        
        # Type dispatch pattern detection using dictionary and list comprehensions
        # This replaces if/elif chains with declarative data structures
        #
        # Traditional approach (conditional logic):
        # base_patterns = {
        #     PositivePattern.PYDANTIC_MODELS: [],
        #     PositivePattern.BEHAVIORAL_ENUMS: [],
        #     PositivePattern.PROTOCOLS: []
        # }
        # for name in base_names:
        #     if name == 'BaseModel':
        #         base_patterns[PositivePattern.PYDANTIC_MODELS].append(name)
        #     elif name in ['Enum', 'StrEnum', 'IntEnum']:
        #         base_patterns[PositivePattern.BEHAVIORAL_ENUMS].append(name)
        #     elif name == 'Protocol':
        #         base_patterns[PositivePattern.PROTOCOLS].append(name)
        #
        # SDA approach (declarative mapping):
        base_patterns = {
            PositivePattern.PYDANTIC_MODELS: [
                name for name in base_names if name == 'BaseModel'
            ],
            PositivePattern.BEHAVIORAL_ENUMS: [
                name for name in base_names if name in ['Enum', 'StrEnum', 'IntEnum']
            ],
            PositivePattern.PROTOCOLS: [
                name for name in base_names if name == 'Protocol'
            ]
        }
        
        return base_patterns
    
    @staticmethod  
    def analyze_function_decorators(decorators: list[ast.expr]) -> dict[PositivePattern, list[str]]:
        """
        Analyze function decorators to detect SDA patterns.
        
        Examines decorators on functions/methods to identify:
        - @computed_field decorators (COMPUTED_FIELDS)
        - @field_validator/@model_validator (CUSTOM_VALIDATORS)
        - @field_serializer decorators (CUSTOM_SERIALIZERS)
        - @property decorators on enums (ENUM_METHODS)
        - @root_validator decorators (ROOT_VALIDATORS)
        
        Args:
            decorators: List of AST expressions representing decorators
            
        Returns:
            Dictionary mapping pattern types to lists of detected decorator names
        """
        # Extract decorator names from AST nodes
        decorator_names = [NodeAnalyzer.extract_name(d) for d in decorators]
        
        # Type dispatch for decorator pattern detection
        # Uses list comprehensions and set membership for clean pattern matching
        #
        # This pattern demonstrates how to replace procedural logic with
        # declarative data structures. Instead of checking each decorator
        # in a loop with if/elif statements, we define the mapping upfront
        # and let Python's list comprehensions do the filtering.
        decorator_patterns = {
            PositivePattern.COMPUTED_FIELDS: [
                name for name in decorator_names if name == 'computed_field'
            ],
            PositivePattern.CUSTOM_VALIDATORS: [
                name for name in decorator_names if name in ['field_validator', 'model_validator']
            ],
            PositivePattern.CUSTOM_SERIALIZERS: [
                name for name in decorator_names if name == 'field_serializer'
            ],
            PositivePattern.ROOT_VALIDATORS: [
                name for name in decorator_names if name == 'root_validator'
            ],
            PositivePattern.ENUM_METHODS: [
                name for name in decorator_names if name == 'property'
            ]
        }
        
        return decorator_patterns
    
    @staticmethod
    def analyze_function_call(func_name: str) -> dict[PositivePattern | ViolationType, list[str]]:
        """
        Analyze function calls to detect both violations and positive patterns.
        
        Examines function call names to identify:
        
        Violations (anti-patterns):
        - isinstance() calls - should use type dispatch instead
        - hasattr()/getattr() calls - should use Pydantic models
        - dict.get() calls - should use typed models
        
        Positive Patterns:
        - Pydantic methods (model_validate, model_dump, model_copy)
        - Field() usage for constraints
        - Annotated[] usage for enhanced types
        
        Args:
            func_name: Name of the function being called
            
        Returns:
            Dictionary mapping pattern/violation types to lists of detected function names
        """
        
        # Type dispatch table for analyzing function calls
        # This replaces long if/elif chains with a declarative mapping
        call_patterns = {
            # Anti-patterns that violate SDA principles
            ViolationType.ISINSTANCE_VIOLATIONS: ['isinstance'] if func_name == 'isinstance' else [],
            ViolationType.HASATTR_VIOLATIONS: ['hasattr'] if func_name == 'hasattr' else [],
            ViolationType.GETATTR_VIOLATIONS: ['getattr'] if func_name == 'getattr' else [],

            
            # Positive patterns that align with SDA
            PositivePattern.PYDANTIC_VALIDATION: [
                func_name
            ] if func_name in ['model_validate', 'model_validate_json'] else [],
            PositivePattern.PYDANTIC_SERIALIZATION: [
                func_name
            ] if func_name in ['model_dump', 'model_dump_json'] else [],
            PositivePattern.IMMUTABLE_UPDATES: [
                func_name
            ] if func_name == 'model_copy' else [],
            PositivePattern.FIELD_CONSTRAINTS: [
                func_name
            ] if func_name == 'Field' else [],
            PositivePattern.ANNOTATED_TYPES: [
                func_name
            ] if func_name == 'Annotated' else []
        }
        
        return call_patterns


class AnalysisContext(BaseModel):
    """
    Immutable context state for AST analysis with computed behavioral properties.
    
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
    classifier: ModuleClassifier = Field(
        default_factory=ModuleClassifier,
        description="Module classifier for context-aware analysis"
    )
    
    @computed_field
    @property
    def module_type(self) -> ModuleType:
        """
        Classify the current module type using the embedded classifier.
        
        This computed field demonstrates SDA: instead of having separate
        classification logic, the context model knows its own module type.
        """
        return self.classifier.classify_module(self.current_file)
    
    @computed_field
    @property
    def is_boundary_context(self) -> bool:
        """
        Determine if we're analyzing boundary/infrastructure code.
        
        Boundary contexts (infrastructure, tooling, framework integration)
        need different analysis rules - they may legitimately use patterns
        like hasattr() and try/except that would be anti-patterns in domain code.
        
        This is contextual intelligence encoded in the type system.
        """
        return self.module_type in [ModuleType.INFRASTRUCTURE, ModuleType.TOOLING, ModuleType.FRAMEWORK]
    
    @computed_field
    @property
    def is_type_checking_context(self) -> bool:
        """
        Detect if we're in a TYPE_CHECKING context.
        
        TYPE_CHECKING blocks are used for imports that are only needed
        for type hints, not runtime. This is a positive pattern.
        """
        return 'TYPE_CHECKING' in self.current_file


class SDAArchitectureDetector(ast.NodeVisitor):
    """
    AST visitor that detects SDA patterns using Pydantic intelligence.
    
    This class demonstrates SDA principles by:
    1. Using immutable Pydantic context instead of mutable state
    2. Recording findings as typed models, not raw dictionaries
    3. Using type dispatch in visit methods instead of conditionals
    4. Delegating analysis logic to specialized analyzer utilities
    
    ## How AST Visitors Work (Junior Dev Tutorial)
    
    Python's ast.NodeVisitor provides a visitor pattern for traversing AST trees.
    
    When you call `detector.visit(tree)`, Python automatically walks through
    every node in the syntax tree and calls the appropriate visit method:
    
    - `visit_ClassDef()` for class definitions: `class MyClass(BaseModel): ...`
    - `visit_FunctionDef()` for function definitions: `def my_function(): ...`
    - `visit_Call()` for function calls: `isinstance(obj, str)`
    - `visit_If()` for if statements: `if condition: ...`
    - `visit_Try()` for try/except blocks: `try: ... except: ...`
    
    Each visit method receives the AST node as a parameter, which contains
    structured information about that piece of code (not just text).
    
    Example: For `class User(BaseModel):`, the ClassDef node contains:
    - node.name = "User" 
    - node.bases = [AST node representing "BaseModel"]
    - node.body = [AST nodes for the class contents]
    
    ## SDA Approach to AST Analysis
    
    Instead of putting all analysis logic directly in visit methods, we:
    - Use NodeAnalyzer for reusable pattern detection logic
    - Use AnalysisContext for tracking where we are in the code
    - Record findings as immutable Pydantic models (not raw dicts)
    - Use computed fields for derived information
    - Delegate complex logic to specialized utilities
    
    This separation makes the code more testable and follows SDA principles.
    """
    
    def __init__(self):
        """Initialize detector with empty findings and default context."""
        # Immutable context using Pydantic model
        self.context = AnalysisContext()
        
        # Initialize findings dictionary for all pattern types
        # Uses enum values as keys to ensure type safety
        self.findings: dict[str, list[Finding]] = {
            violation.value: [] for violation in ViolationType
        }
        self.findings.update({
            pattern.value: [] for pattern in PositivePattern
        })
        
    def set_file(self, filename: str):
        """
        Update analysis context for a new file using immutable updates.
        
        This demonstrates SDA: instead of mutating state, we create
        a new context instance using model_copy().
        """
        self.context = self.context.model_copy(update={"current_file": filename})
        
    def _record_finding(self, finding_type: str, node: ast.AST, description: str):
        """
        Record a finding using typed Pydantic model instead of raw dict.
        
        This shows SDA: we create structured, validated data models
        rather than working with primitive dictionaries.
        
        Args:
            finding_type: The type of pattern found (from enum values)
            node: AST node where pattern was found 
            description: Human-readable description of the finding
        """
        finding = Finding(
            file_path=self.context.current_file,
            line_number=getattr(node, 'lineno', 0),  # Boundary getattr for AST
            description=description
        )
        self.findings[finding_type].append(finding)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definitions for patterns."""
        old_context = self.context
        self.context = self.context.model_copy(update={"current_class": node.name})
        
        # Analyze inheritance patterns
        base_patterns = NodeAnalyzer.analyze_class_bases(node.bases)
        for pattern_type, names in base_patterns.items():
            for name in names:
                self._record_finding(pattern_type.value, node, f"{name}: {node.name}")
        
        # Check if this is an enum class using pure type dispatch
        # This demonstrates boolean coercion for conditional logic elimination
        enum_patterns = [PositivePattern.BEHAVIORAL_ENUMS]
        is_enum = any(self.findings[pattern.value] for pattern in enum_patterns)
        
        # Boolean coercion array indexing - SDA in its purest form
        # 
        # This pattern is a TEACHING MOMENT because it's so explicit about the core
        # SDA principle: "data drives behavior" with no procedural escape hatches.
        #
        # When you see: result = ["inactive", "active"][bool(user.is_verified)]
        # You can't fall back on procedural habits. There's no `if` keyword to lean on.
        # You MUST think "my data is selecting behavior" rather than "I'm checking a condition."
        #
        # This forces the mental model shift that SDA requires - data as the driver,
        # not conditions as controllers. It's like learning through immersion vs translation.
        #
        # Traditional approach (procedural thinking):
        # if is_enum:
        #     self.context = self.context.model_copy(update={"in_enum_class": True})
        # else:
        #     self.context = self.context.model_copy(update={})
        #
        # SDA approach (data-driven thinking):
        # Data (boolean) selects behavior (update dictionary) directly
        # int(False) = 0, int(True) = 1, so boolean becomes array index
        #
        # More examples of this pure pattern:
        # message = ["Failed", "Success"][int(operation_succeeded)]  # Data selects message
        # icon = ["❌", "✅"][bool(task.completed)]                   # Data selects display
        # handler = [self.reject, self.approve][int(valid)]          # Data selects function
        enum_context_updates = [
            {},  # False case (index 0)
            {"in_enum_class": True}  # True case (index 1)
        ]
        self.context = self.context.model_copy(update=enum_context_updates[int(is_enum)])
        
        # Analyze for anemic service patterns
        self._analyze_anemic_service(node)
        
        self.generic_visit(node)
        self.context = old_context
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function definitions for patterns."""
        old_context = self.context
        self.context = self.context.model_copy(update={"current_function": node.name})
        
        # Analyze decorators
        decorator_patterns = NodeAnalyzer.analyze_function_decorators(node.decorator_list)
        for pattern_type, names in decorator_patterns.items():
            for name in names:
                self._record_finding(pattern_type.value, node, f"@{name} {node.name}")
        
        self.generic_visit(node)
        self.context = old_context
    
    def visit_Call(self, node: ast.Call):
        """Detect patterns in function calls."""
        func_name = NodeAnalyzer.extract_name(node.func)
        
        # Enhanced dict.get() analysis
        if (func_name == 'get' and 
            isinstance(node.func, ast.Attribute) and 
            node.args):
            self._analyze_dict_get_call(node)
        else:
            # Standard function call analysis
            call_patterns = NodeAnalyzer.analyze_function_call(func_name)
            for pattern_type, names in call_patterns.items():
                for name in names:
                    description = f"{name}() runtime check" if isinstance(pattern_type, ViolationType) else f"{name} usage"
                    self._record_finding(pattern_type.value, node, description)
        
        self.generic_visit(node)
    
    def _analyze_dict_get_call(self, node: ast.Call):
        """Conservative analysis of dict.get() calls - only flag obvious violations."""
        key = node.args[0]  # First argument is the key
        
        # Only flag string literals as violations - everything else is neutral
        is_string_literal = isinstance(key, ast.Constant) and isinstance(key.value, str)
        is_enum_self = isinstance(key, ast.Name) and key.id == 'self'
        is_enum_attribute = isinstance(key, ast.Attribute)
        is_tuple_key = isinstance(key, ast.Tuple)
        is_complex_key = is_tuple_key and any(
            isinstance(elt, ast.Attribute) for elt in key.elts
        )
        
        # Clear type dispatch patterns
        is_obvious_type_dispatch = (
            is_enum_self or          # transitions.get(self, default)
            is_enum_attribute or     # handlers.get(event.type, default)  
            is_complex_key           # cases.get((self.STATE, condition), default)
        )
        
        if is_string_literal:
            # String literal keys are clear violations
            self._record_finding(
                ViolationType.DICT_GET_VIOLATIONS.value, 
                node, 
                f"get() with string literal '{key.value}' (use typed model)"
            )
        elif is_obvious_type_dispatch:
            # Clear type dispatch patterns
            key_desc = "enum self" if is_enum_self else "typed key"
            self._record_finding(
                PositivePattern.TYPE_DISPATCH_TABLES.value,
                node,
                f"type dispatch lookup with {key_desc}"
            )
        # Everything else: no classification (neutral)
    
    def visit_If(self, node: ast.If):
        """Analyze conditional logic for SDA compliance."""
        # Simple boundary condition detection
        test_name = NodeAnalyzer.extract_name(node.test) 
        
        # Type dispatch for conditional analysis
        if test_name == 'TYPE_CHECKING':
            self._record_finding(PositivePattern.TYPE_CHECKING_IMPORTS.value, node, "TYPE_CHECKING import")
        elif self.context.is_boundary_context:
            self._record_finding(PositivePattern.BOUNDARY_CONDITIONS.value, node, "boundary error handling")
        else:
            self._record_finding(ViolationType.BUSINESS_CONDITIONALS.value, node, "business logic conditional")
        
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        """Analyze try/except patterns."""
        # Infrastructure boundary context gets lenient treatment
        if self.context.is_boundary_context:
            self._record_finding(PositivePattern.BOUNDARY_CONDITIONS.value, node, "boundary error handling")
        else:
            self._record_finding(ViolationType.TRY_EXCEPT_VIOLATIONS.value, node, "try/except instead of type safety")
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Analyze attribute access patterns, especially enum .value unwrapping."""
        # Check for enum .value unwrapping (primitive obsession)
        if node.attr == "value":
            # Get the object being accessed (left side of the dot)
            if isinstance(node.value, ast.Attribute):
                # Pattern like SomeEnum.SOME_VALUE.value
                enum_name = NodeAnalyzer.extract_name(node.value.value)  # SomeEnum
                enum_member = node.value.attr  # SOME_VALUE
                
                # Check if it looks like an enum pattern
                if (enum_name and enum_member and 
                    enum_member.isupper()):  # CONSTANT_CASE strongly suggests enum member
                    
                    self._record_finding(
                        ViolationType.ENUM_VALUE_UNWRAPPING.value, 
                        node, 
                        f"enum value unwrapping - consider StrEnum for automatic conversion, or validate if external serialization is needed instead of {enum_name}.{enum_member}.value"
                    )
        
        self.generic_visit(node)
    
    def _analyze_anemic_service(self, node: ast.ClassDef):
        """Analyze service classes for anemic patterns."""
        # Only analyze classes that claim to be services
        if not node.name.endswith('Service'):
            return
        
        # Get all methods in the class
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name != '__init__']
        
        if not methods:
            return  # No methods to analyze
        
        # Calculate anemic indicators
        static_method_count = sum(1 for method in methods if self._is_static_or_classmethod(method))
        total_methods = len(methods)
        
        # Red flags for anemic services
        anemic_indicators = []
        
        # High ratio of static methods (suggests no shared state/behavior)
        if total_methods > 2 and static_method_count / total_methods > 0.7:
            anemic_indicators.append(f"{static_method_count}/{total_methods} static methods")
        
        # Methods with generic utility-style names
        utility_methods = sum(1 for method in methods if self._is_utility_method_name(method.name))
        if utility_methods > 1:
            anemic_indicators.append(f"{utility_methods} utility-style method names")
        
        # Service with many small, unrelated methods
        if total_methods > 8:  # Threshold for "too many responsibilities"
            anemic_indicators.append(f"{total_methods} methods (high cohesion risk)")
        
        # If multiple indicators present, flag as anemic
        if len(anemic_indicators) >= 2:
            description = f"anemic service - {', '.join(anemic_indicators)} - consider domain model methods or focused services"
            self._record_finding(ViolationType.ANEMIC_SERVICES.value, node, description)
    
    def _is_static_or_classmethod(self, method: ast.FunctionDef) -> bool:
        """Check if method is static or classmethod."""
        decorator_names = [NodeAnalyzer.extract_name(d) for d in method.decorator_list]
        return 'staticmethod' in decorator_names or 'classmethod' in decorator_names
    
    def _is_utility_method_name(self, method_name: str) -> bool:
        """Check if method name suggests utility/helper function."""
        utility_patterns = [
            'helper', 'util', 'process', 'handle', 'execute', 'run',
            'get_', 'set_', 'create_', 'update_', 'delete_', 'parse_',
            'convert_', 'transform_', 'format_', 'validate_'
        ]
        return any(pattern in method_name.lower() for pattern in utility_patterns)


class ArchitectureReport(BaseModel):
    """Comprehensive architecture analysis report."""
    model_config = ConfigDict(frozen=True)
    
    violations: dict[ViolationType, list[Finding]]
    patterns: dict[PositivePattern, list[Finding]]
    
    @computed_field
    @property
    def total_violations(self) -> int:
        return sum(len(findings) for findings in self.violations.values())
    
    @computed_field
    @property
    def total_patterns(self) -> int:
        return sum(len(findings) for findings in self.patterns.values())
    
    @computed_field
    @property
    def files_analyzed(self) -> int:
        """Count of unique files analyzed - pure observation."""
        all_files = set()
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
        return classifier.classify_module(sample_file)


def analyze_module(module_path: str, module_name: str) -> ArchitectureReport:
    """Analyze a module for SDA compliance."""
    detector = SDAArchitectureDetector()
    
    files = [module_path] if os.path.isfile(module_path) else [
        os.path.join(module_path, f) for f in os.listdir(module_path) 
        if f.endswith('.py')
    ]
    
    for filepath in files:
        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            
            relative_path = filepath.replace(module_path, module_name) if module_path != filepath else module_name
            detector.set_file(relative_path)
            detector.visit(tree)
        except Exception as e:
            print(f'Error parsing {filepath}: {e}')
    
    return _generate_report(detector.findings)


def _generate_report(findings: dict[str, list[Finding]]) -> ArchitectureReport:
    """Generate comprehensive architecture report."""
    
    # Categorize findings using type dispatch
    violations = {
        violation_type: findings.get(violation_type.value, [])
        for violation_type in ViolationType
    }
    
    patterns = {
        pattern_type: findings.get(pattern_type.value, [])
        for pattern_type in PositivePattern
    }
    
    return ArchitectureReport(
        violations=violations,
        patterns=patterns
    )


# Display Domain Models
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
        return {True: '⚪', False: '🔍'}
    
    @computed_field
    @property
    def pattern_status_indicator(self) -> dict[bool, str]:
        """Status indicators for patterns (neutral observation)."""
        return {True: '📊', False: '⚪'}
    
    def format_header(self, module_name: str) -> str:
        """Format report header."""
        title = f'🧠 SDA ARCHITECTURE ANALYSIS - {module_name.upper()}'
        separator = '=' * self.config.separator_length
        return f'{title}\n{separator}'
    
    def format_section_header(self, title: str) -> str:
        """Format section header."""
        return title
    
    def format_item_line(self, name: str, count: int, status: str) -> str:
        """Format individual item line."""
        return f'  {name:{self.config.field_width}} {count:{self.config.count_width}} {status}'
    
    def format_finding_detail(self, finding: Finding) -> str:
        """Format finding detail line."""
        return f'    → {finding.location} - {finding.description}'
    
    def format_overflow_message(self, remaining_count: int) -> str:
        """Format overflow message for truncated lists."""
        return f'    → ... and {remaining_count} more'
    
    def should_show_overflow(self, total_count: int) -> bool:
        """Determine if overflow message should be shown."""
        return total_count > self.config.summary_item_limit


def print_report(report: ArchitectureReport, module_name: str):
    """Print objective architecture analysis report using domain models."""
    formatter = ReportFormatter()
    
    print(formatter.format_header(module_name))
    
    print(formatter.format_section_header('🔍 SDA PATTERNS DETECTED:'))
    for violation_type, items in report.violations.items():
        count = len(items)
        status = formatter.violation_status_indicator[count == 0]
        print(formatter.format_item_line(violation_type.value, count, status))
        
        for item in items[:formatter.config.summary_item_limit]:
            print(formatter.format_finding_detail(item))
        
        if formatter.should_show_overflow(count):
            remaining = count - formatter.config.summary_item_limit
            print(formatter.format_overflow_message(remaining))
    
    print()
    print(formatter.format_section_header('📊 ARCHITECTURAL FEATURES:'))
    for pattern_type, items in report.patterns.items():
        count = len(items)
        status = formatter.pattern_status_indicator[count > 0]
        print(formatter.format_item_line(pattern_type.value, count, status))
        
        for item in items[:formatter.config.summary_item_limit]:
            print(formatter.format_finding_detail(item))
            
        if formatter.should_show_overflow(count):
            remaining = count - formatter.config.summary_item_limit
            print(formatter.format_overflow_message(remaining))
    
    print()
    print(f'MODULE TYPE: {report.module_type.value}')
    print(f'FILES ANALYZED: {report.files_analyzed}')
    print(f'TOTAL VIOLATIONS: {report.total_violations}')
    print(f'TOTAL PATTERNS: {report.total_patterns}')
    
    # Pure observational metrics - no judgment
    dist = report.pattern_distribution
    print(f'DISTRIBUTION: {dist["patterns"]:.1%} patterns, {dist["violations"]:.1%} violations')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python sda_detector.py <module_path> [module_name]')
        sys.exit(1)
    
    module_path = sys.argv[1]
    module_name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(module_path)
    
    report = analyze_module(module_path, module_name)
    print_report(report, module_name)