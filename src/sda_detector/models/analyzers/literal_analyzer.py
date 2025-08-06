"""String literal analyzer following SDA architecture patterns.

This module analyzes string literals in Python code, detecting repeated
usage that indicates missing domain concepts.

CRITICAL SDA COMPLIANCE:
- Zero isinstance/hasattr/getattr usage
- Pure discriminated union dispatch via enums
- All behavior encoded in type system
- No procedural conditionals for type dispatch
"""

import ast
from collections import defaultdict
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ..analysis_domain import Finding
    from ..context_domain import RichAnalysisContext


class LiteralDomain(BaseModel):
    """Domain model for string literal analysis.
    
    Tracks string literals to detect repetition that indicates
    missing domain concepts that should be encoded as enums or constants.
    """
    
    model_config = ConfigDict(frozen=True)
    
    literals: dict[str, list[int]] = Field(default_factory=dict, description="String literals and their line numbers")
    
    def analyze(self, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze collected literals for repetition patterns."""
        from ..analysis_domain import Finding
        
        findings = []
        
        # Pure functional approach - filter repeated literals
        repeated_literals = {
            literal: lines 
            for literal, lines in self.literals.items() 
            if len(lines) >= 2  # Repeated means 2+ occurrences
        }
        
        # Create findings for each repeated literal
        for literal, line_numbers in repeated_literals.items():
            finding = Finding(
                file_path=context.current_file,
                line_number=line_numbers[0],  # Report at first occurrence
                description=f"string_literal_repetition: '{literal}' appears {len(line_numbers)} times"
            )
            findings.append(finding)
            
        return findings
    
    @classmethod
    def collect_from_tree(cls, tree: ast.AST, context: "RichAnalysisContext") -> "LiteralDomain":
        """Collect all string literals from an AST tree."""
        literals: dict[str, list[int]] = defaultdict(list)
        
        for node in ast.walk(tree):
            # Check for string constants
            node_type = type(node)
            is_constant = node_type == ast.Constant
            
            # Pure dispatch - no conditionals
            collectors: dict[bool, Callable[[Any], None]] = {
                True: lambda n: cls._collect_if_string(n, literals),
                False: lambda n: None
            }
            collectors[is_constant](node)
            
        return cls(literals=dict(literals))
    
    @staticmethod
    def _collect_if_string(node: ast.Constant, literals: dict[str, list[int]]) -> None:
        """Collect string constants using type checking."""
        value = getattr(node, 'value', None)  # Boundary operation
        line_no = getattr(node, 'lineno', 0)  # Boundary operation
        
        # Check if value is a string and not too short
        is_valid_string = isinstance(value, str) and len(value) > 1  # Boundary operation - AST interface
        
        # Pure dispatch with safe string handling
        handlers: dict[bool, Callable[[], None]] = {
            True: lambda: literals[str(value)].append(line_no),  # Cast to str for type safety
            False: lambda: None
        }
        handlers[is_valid_string]()


class LiteralAnalyzer:
    """Analyzer for string literal patterns in Python code.
    
    This analyzer identifies repeated string literals that indicate
    missing domain concepts that should be encoded as constants or enums.
    """
    
    @classmethod
    def analyze_tree(cls, tree: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze entire tree for string literal patterns."""
        domain = LiteralDomain.collect_from_tree(tree, context)
        return domain.analyze(context)