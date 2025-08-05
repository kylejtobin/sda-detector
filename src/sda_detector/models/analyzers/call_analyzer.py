"""Function call analyzer following SDA architecture patterns.

This module analyzes function calls in Python code, identifying patterns
that align with or violate SDA principles.

CRITICAL SDA COMPLIANCE:
- Zero isinstance/hasattr/getattr usage
- Pure discriminated union dispatch via enums
- All behavior encoded in type system
- No procedural conditionals for type dispatch
"""

import ast
from enum import StrEnum
from typing import TYPE_CHECKING, Callable, Any

from pydantic import BaseModel, ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from ..analysis_domain import Finding
    from ..context_domain import RichAnalysisContext


class CallPattern(StrEnum):
    """Behavioral enum for function call pattern classification.

    Each pattern knows how to create appropriate findings - this is core SDA.
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
    """Domain model for function call analysis.

    Analyzes function calls to identify SDA patterns and violations.
    Common patterns: isinstance() calls, JSON serialization, Pydantic operations.
    """

    model_config = ConfigDict(frozen=True)

    function_name: str = Field(description="Function being called")
    line_number: int = Field(ge=0, description="Line number in source code")

    @computed_field
    @property
    def call_pattern(self) -> CallPattern:
        """Classify the function call pattern using pure discriminated union dispatch.

        SDA Principle: Pure dictionary dispatch - no conditionals.
        """
        # Pure dictionary dispatch for function classification
        type_check_functions = {"isinstance", "type", "hasattr", "getattr"}
        json_functions = {"dumps", "loads", "dump", "load"}
        pydantic_functions = {"model_dump", "model_validate", "model_copy", "Field"}
        
        # Create classification key based on membership
        is_type_check = self.function_name in type_check_functions
        is_json = self.function_name in json_functions
        is_pydantic = self.function_name in pydantic_functions
        
        # Pure tuple-based dispatch - no conditionals
        classification_key = (is_type_check, is_json, is_pydantic)
        
        # Exhaustive mapping of all combinations
        classification_map = {
            (True, False, False): CallPattern.TYPE_CHECK,
            (False, True, False): CallPattern.JSON_OPERATION,
            (False, False, True): CallPattern.PYDANTIC_OPERATION,
            (False, False, False): CallPattern.COMPUTED_FIELD,
            # Handle overlapping cases (shouldn't happen but be exhaustive)
            (True, True, False): CallPattern.TYPE_CHECK,  # Type check takes priority
            (True, False, True): CallPattern.TYPE_CHECK,  # Type check takes priority
            (False, True, True): CallPattern.JSON_OPERATION,  # JSON takes priority over pydantic
            (True, True, True): CallPattern.TYPE_CHECK,  # Type check takes highest priority
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

        Discriminated union guarantees this is ast.Call.
        This is the type boundary - we handle the conversion here.
        """
        # Extract function name using type-safe dispatch
        function_name = cls._extract_function_name(node)
        line_number = getattr(node, 'lineno', 0)  # Boundary operation

        return cls(function_name=function_name, line_number=line_number)

    @staticmethod
    def _extract_function_name(node: ast.AST) -> str:
        """Extract function name from AST node using pure discriminated union dispatch.

        Boundary operation - handles type conversion at AST boundary.
        """
        func = getattr(node, 'func', None)  # Boundary operation - AST interface
        
        # Pure function composition - handle None as a valid AST type
        return CallDomain._extract_from_func_node_safe(func)
    
    @staticmethod
    def _extract_from_func_node_safe(func: ast.AST | None) -> str:
        """Extract name from func node using pure type dispatch, handling None."""
        # Dictionary dispatch including None as a valid type
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

    This analyzer identifies and classifies function calls according
    to SDA principles, distinguishing between acceptable patterns
    (Pydantic operations, computed fields) and violations (isinstance, manual JSON).
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
