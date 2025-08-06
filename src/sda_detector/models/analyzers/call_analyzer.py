"""Function call analyzer following SDA architecture patterns - Detecting Method Invocations.

PURPOSE:
This analyzer detects and classifies function calls to identify both SDA violations
(isinstance, manual JSON) and positive patterns (Pydantic operations, computed fields).

SDA PRINCIPLES DEMONSTRATED:
1. **Multi-Level Type Dispatch**: Handles both None and AST node types
2. **Exhaustive Boolean Mapping**: All 8 combinations explicitly handled
3. **Cascading Extractors**: Function name extraction through type dispatch
4. **Priority-Based Classification**: Overlapping cases handled by priority
5. **Boundary Isolation**: getattr() only at AST boundaries

LEARNING GOALS:
- Understand how to analyze function calls in AST
- Learn to handle complex AST node structures (Name vs Attribute)
- Master exhaustive boolean dispatch with priorities
- See how to extract information from nested AST nodes
- Recognize patterns in function naming conventions

ARCHITECTURE NOTES:
This analyzer demonstrates sophisticated AST handling - function calls can have
different structures (direct name, attribute access, etc.) but we handle all
cases through pure type dispatch without conditionals.

Teaching Example:
    >>> # What we're analyzing:
    >>> isinstance(obj, MyClass)  # TYPE_CHECK - violation!
    >>> json.dumps(data)  # JSON_OPERATION - violation!
    >>> model.model_dump()  # PYDANTIC_OPERATION - good pattern!
    >>> 
    >>> # How we analyze it:
    >>> call = CallDomain.from_ast(call_node)
    >>> pattern = call.call_pattern  # Pure classification
    >>> finding = pattern.create_finding(...)  # Pattern knows its type

Key Insight:
Function calls are complex AST structures, but we can classify them through
pure type dispatch and behavioral enums, avoiding all conditionals.
"""

import ast
from collections.abc import Callable
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from ..analysis_domain import Finding
    from ..context_domain import RichAnalysisContext


class CallPattern(StrEnum):
    """Behavioral enum for function call pattern classification.

    WHAT: Classifies different types of function calls based on their purpose
    and alignment with SDA principles.
    
    WHY: Different function calls indicate different patterns - some are
    violations (isinstance, json.dumps) while others are good patterns
    (model_dump, computed_field).
    
    HOW: Each enum value maps to either a PatternType (violation) or
    PositivePattern (good practice) and creates appropriate findings.
    
    Teaching Categories:
        - TYPE_CHECK: Runtime type checking (isinstance, hasattr) - violation!
        - JSON_OPERATION: Manual JSON serialization - use Pydantic instead!
        - PYDANTIC_OPERATION: Pydantic methods - good pattern!
        - COMPUTED_FIELD: Computed/derived fields - excellent pattern!
    
    SDA Pattern Demonstrated:
        Smart Enums - Each value knows exactly what kind of finding it
        represents, eliminating external classification logic.
    """

    TYPE_CHECK = "type_check"
    JSON_OPERATION = "json_operation"
    PYDANTIC_OPERATION = "pydantic_operation"
    COMPUTED_FIELD = "computed_field"

    def create_finding(self, file_path: str, line_number: int, function_name: str) -> "Finding":
        """Each call pattern creates its appropriate finding type.

        SDA Principle: Enums encapsulate their own behavior instead of external logic.
        """
        from ..analysis_domain import Finding
        from ..core_types import PatternType, PositivePattern

        # Pure dictionary dispatch - each enum value knows its finding type
        finding_types = {
            CallPattern.TYPE_CHECK: PatternType.ISINSTANCE_USAGE,
            CallPattern.JSON_OPERATION: PatternType.MANUAL_JSON_SERIALIZATION,
            CallPattern.PYDANTIC_OPERATION: PositivePattern.PYDANTIC_SERIALIZATION,
            CallPattern.COMPUTED_FIELD: PositivePattern.COMPUTED_FIELDS,
        }

        finding_type = finding_types[self]
        return Finding(
            file_path=file_path,
            line_number=line_number,
            description=f"{finding_type}: {function_name}",
        )


class CallDomain(BaseModel):
    """Domain model for function call analysis - Understanding Method Invocations.

    WHAT: Represents a function call with extracted name and classification logic
    to determine what pattern it represents.
    
    WHY: Function calls reveal how code makes decisions - isinstance shows
    runtime type checking, json.dumps shows manual serialization, while
    model_dump shows proper Pydantic usage.
    
    HOW: Extracts function name from complex AST structures, then uses
    exhaustive boolean dispatch to classify the call pattern.
    
    Teaching Example:
        >>> # From AST node for: isinstance(user, PremiumUser)
        >>> call = CallDomain(function_name="isinstance", line_number=42)
        >>> print(call.call_pattern)  # CallPattern.TYPE_CHECK
        >>> 
        >>> # From AST node for: order.model_dump()
        >>> call = CallDomain(function_name="model_dump", line_number=50)
        >>> print(call.call_pattern)  # CallPattern.PYDANTIC_OPERATION
    
    SDA Pattern Demonstrated:
        Classification through Sets - Using set membership for initial
        classification, then boolean tuple dispatch for final pattern.
    """

    model_config = ConfigDict(frozen=True)

    function_name: str = Field(description="Function being called")
    line_number: int = Field(ge=0, description="Line number in source code")

    @computed_field
    @property
    def call_pattern(self) -> CallPattern:
        """Classify the function call pattern using pure discriminated union dispatch.

        Teaching Note: EXHAUSTIVE 8-CASE DISPATCH WITH PRIORITIES
        
        This method shows advanced classification:
        1. Define sets of function names by category
        2. Check membership to create booleans (3 booleans = 8 cases)
        3. Map ALL 8 cases explicitly
        4. Handle overlaps with priority rules
        
        Why explicit overlap handling?
        - Makes priorities visible in code
        - Prevents silent bugs from unexpected overlaps
        - Documents decision logic clearly
        
        The priority order: TYPE_CHECK > JSON > PYDANTIC
        This reflects severity - type checking is worst violation.
        """
        # Pure dictionary dispatch for function classification
        type_check_functions = {"isinstance", "type", "hasattr", "getattr", "cast", "Any"}
        json_functions = {"dumps", "loads", "dump", "load"}
        pydantic_functions = {"model_dump", "model_validate", "model_copy", "Field"}
        
        # Create classification key based on membership
        is_type_check = self.function_name in type_check_functions
        is_json = self.function_name in json_functions
        is_pydantic = self.function_name in pydantic_functions
        
        # Pure tuple-based dispatch - no conditionals
        classification_key = (is_type_check, is_json, is_pydantic)
        
        # Teaching: Exhaustive mapping of all 8 combinations (2^3)
        # First 4 are the "pure" cases - only one boolean is True
        classification_map = {
            (True, False, False): CallPattern.TYPE_CHECK,
            (False, True, False): CallPattern.JSON_OPERATION,
            (False, False, True): CallPattern.PYDANTIC_OPERATION,
            (False, False, False): CallPattern.COMPUTED_FIELD,
            # Teaching: Handle overlapping cases - shouldn't happen but be exhaustive!
            # These 4 cases handle if a function name appears in multiple sets
            (True, True, False): CallPattern.TYPE_CHECK,  # Both type & JSON - type wins
            (True, False, True): CallPattern.TYPE_CHECK,  # Both type & Pydantic - type wins
            (False, True, True): CallPattern.JSON_OPERATION,  # Both JSON & Pydantic - JSON wins
            (True, True, True): CallPattern.TYPE_CHECK,  # All three?! - type wins
        }
        
        return classification_map[classification_key]

    def analyze(self, context: "RichAnalysisContext") -> list["Finding"]:
        """Self-analyzing domain model using enum behavioral method.

        SDA Principle: Domain models delegate to behavioral enums that know their own logic.
        """
        finding = self.call_pattern.create_finding(
            file_path=context.current_file, line_number=self.line_number, function_name=self.function_name
        )
        return [finding]

    @classmethod
    def from_ast(cls, node: ast.AST) -> "CallDomain":
        """Create CallDomain from AST node using pure SDA patterns.

        Teaching Note: AST BOUNDARY WITH DELEGATION
        
        This method is minimal - it delegates the complex work of
        extracting function names to helper methods. This separation:
        1. Keeps each method focused (Single Responsibility)
        2. Makes the extraction logic testable
        3. Handles the boundary cleanly
        
        The discriminated union guarantees this is ast.Call, so we
        know 'func' and 'lineno' attributes exist.
        """
        # Extract function name using type-safe dispatch
        function_name = cls._extract_function_name(node)
        line_number = getattr(node, 'lineno', 0)  # Boundary operation

        return cls(function_name=function_name, line_number=line_number)

    @staticmethod
    def _extract_function_name(node: ast.AST) -> str:
        """Extract function name from AST node using pure discriminated union dispatch.

        Teaching Note: SAFE EXTRACTION PATTERN
        
        AST call nodes have a 'func' attribute that can be:
        - ast.Name: Direct function call like isinstance()
        - ast.Attribute: Method call like obj.method()
        - None: Shouldn't happen but we handle it
        - Other: Complex expressions we default to "unknown"
        
        We use getattr() here because we're at the AST boundary.
        After extraction, everything is pure strings.
        """
        func = getattr(node, 'func', None)  # Boundary operation - AST interface
        
        # Pure function composition - handle None as a valid AST type
        return CallDomain._extract_from_func_node_safe(func)
    
    @staticmethod
    def _extract_from_func_node_safe(func: ast.AST | None) -> str:
        """Extract name from func node using pure type dispatch, handling None.
        
        Teaching Note: TYPE DISPATCH INCLUDING NONE
        
        This shows how to handle optional values in type dispatch:
        1. Include type(None) as a valid key
        2. Map it to appropriate default behavior
        3. Use type() not isinstance() for exact matching
        
        The dictionary includes lambdas that extract the name
        differently based on node type:
        - Name nodes: Get the 'id' attribute
        - Attribute nodes: Get the 'attr' attribute
        - None: Return default string
        """
        # Teaching: Dictionary dispatch including None as a valid type
        # This elegantly handles the optional without if statements!
        type_extractors: dict[type, Callable[[Any], str]] = {
            type(None): lambda f: "unknown_function",
            ast.Name: lambda f: getattr(f, 'id', 'unknown'),  # Boundary operation
            ast.Attribute: lambda f: getattr(f, 'attr', 'unknown'),  # Boundary operation
        }
        
        func_type = type(func)
        extractor = type_extractors.get(func_type, lambda f: "unknown_function")
        return extractor(func)
    
    @staticmethod
    def _extract_from_func_node(func: ast.AST) -> str:
        """Extract name from func node using pure type dispatch."""
        func_type = type(func)
        
        # Pure dictionary dispatch for func type
        type_extractors: dict[type, Callable[[Any], str]] = {
            ast.Name: lambda f: getattr(f, 'id', 'unknown'),  # Boundary operation
            ast.Attribute: lambda f: getattr(f, 'attr', 'unknown'),  # Boundary operation
        }
        
        extractor = type_extractors.get(func_type, lambda f: "unknown_function")
        return extractor(func)


class CallAnalyzer:
    """Analyzer for function call patterns in Python code.

    WHAT: Entry point for analyzing function call AST nodes, delegating
    to CallDomain for classification and finding creation.
    
    WHY: Provides clean interface for the AST dispatch system while
    keeping all intelligence in the domain model.
    
    HOW: Creates CallDomain from AST node and delegates analysis,
    following the pattern of minimal analyzers and smart models.
    
    Teaching Note:
        Like ConditionalAnalyzer, this is intentionally minimal.
        The analyzer doesn't analyze - it coordinates. All the
        intelligence lives in CallDomain. This inverts traditional
        service-oriented architecture where services are smart and
        models are dumb.
    
    SDA Pattern Demonstrated:
        Thin Analyzers, Thick Models - Analyzers just coordinate,
        models contain all the intelligence and behavior.
    """

    @classmethod
    def analyze_node(cls, node: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze an AST node for function call patterns.

        Trust discriminated union - delegate to domain model.
        The domain model's from_ast handles the type boundary perfectly.
        """
        # Domain model handles the type boundary - sophisticated simplicity!
        call_domain = CallDomain.from_ast(node)

        # Let the domain model analyze itself
        return call_domain.analyze(context)
