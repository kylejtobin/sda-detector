"""String literal analyzer following SDA architecture patterns - Finding Hidden Domain Concepts.

PURPOSE:
This analyzer detects repeated string literals that indicate missing domain
concepts - strings that should be constants, enums, or domain types.

SDA PRINCIPLES DEMONSTRATED:
1. **Tree-Wide Analysis**: Analyzes entire file, not individual nodes
2. **Collection Pattern**: Gathers data then analyzes in batch
3. **Dictionary Dispatch with Lambdas**: Even simple checks use dispatch
4. **Boundary isinstance**: Shows acceptable isinstance at AST boundary
5. **Threshold-Based Detection**: Repetition >= 2 indicates pattern

LEARNING GOALS:
- Understand tree-wide vs node-by-node analysis patterns
- Learn to detect primitive obsession through repetition
- Master collection-then-analysis patterns
- See how to handle AST constants safely
- Recognize when strings should become domain types

ARCHITECTURE NOTES:
Unlike other analyzers that process nodes individually, this one collects
all literals first, then analyzes patterns. This shows a different analysis
strategy - batch processing for cross-cutting concerns.

Teaching Example:
    >>> # What we're detecting:
    >>> status = "pending"  # First occurrence
    >>> if order.state == "pending":  # Second occurrence - pattern!
    >>>     # Should be: if order.state == OrderStatus.PENDING
    >>> 
    >>> # How we detect it:
    >>> literals = {"pending": [10, 25]}  # Line numbers
    >>> # Creates finding: "string_literal_repetition: 'pending' appears 2 times"

Key Insight:
Repeated strings often indicate missing domain concepts. They should be
replaced with enums, constants, or domain types for type safety.
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
    """Domain model for string literal analysis - Detecting Primitive Obsession.
    
    WHAT: Collects and analyzes string literals to find repetition patterns
    that indicate missing domain abstractions.
    
    WHY: Repeated strings are a code smell - they often represent domain
    concepts that should be encoded as types (enums, constants, value objects).
    
    HOW: Collects all string literals with their locations, then identifies
    those that appear multiple times as candidates for extraction.
    
    Teaching Example:
        >>> domain = LiteralDomain(literals={
        >>>     "active": [10, 25, 30],  # Appears 3 times - should be enum!
        >>>     "user_id": [15],  # Only once - probably OK
        >>>     "error": [20, 45],  # Twice - maybe should be constant
        >>> })
        >>> findings = domain.analyze(context)
        >>> # Returns findings for "active" and "error", not "user_id"
    
    SDA Pattern Demonstrated:
        Collection-Analysis Separation - First collect all data, then
        analyze patterns. This enables cross-cutting concern detection.
    """
    
    model_config = ConfigDict(frozen=True)
    
    literals: dict[str, list[int]] = Field(default_factory=dict, description="String literals and their line numbers")
    
    def analyze(self, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze collected literals for repetition patterns.
        
        Teaching Note: FUNCTIONAL FILTERING PATTERN
        
        This uses dictionary comprehension with filtering - a pure
        functional approach to find repeated items:
        1. Iterate over all literals
        2. Keep only those with 2+ occurrences
        3. Create findings for each
        
        The threshold of 2 is domain knowledge - single use is OK,
        repeated use suggests a missing abstraction.
        """
        from ..analysis_domain import Finding
        
        findings = []
        
        # Teaching: Pure functional filtering - no mutations
        repeated_literals = {
            literal: lines 
            for literal, lines in self.literals.items() 
            if len(lines) >= 2  # Teaching: 2+ means repeated - domain concept!
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
        """Collect all string literals from an AST tree.
        
        Teaching Note: TREE-WIDE COLLECTION PATTERN
        
        This method walks the ENTIRE tree once, collecting all literals.
        This is different from node-by-node analysis:
        
        Node-by-node: Process each node individually
        Tree-wide: Collect everything, then analyze patterns
        
        ast.walk() does depth-first traversal of all nodes.
        """
        literals: dict[str, list[int]] = defaultdict(list)  # Teaching: Auto-creates lists
        
        for node in ast.walk(tree):
            # Check for string constants
            node_type = type(node)
            is_constant = node_type == ast.Constant
            
            # Teaching: Pure dispatch even for simple checks!
            # This replaces: if is_constant: collect(node)
            collectors: dict[bool, Callable[[Any], None]] = {
                True: lambda n: cls._collect_if_string(n, literals),
                False: lambda n: None  # Do nothing for non-constants
            }
            collectors[is_constant](node)  # Dispatch based on node type
            
        return cls(literals=dict(literals))
    
    @staticmethod
    def _collect_if_string(node: ast.Constant, literals: dict[str, list[int]]) -> None:
        """Collect string constants using type checking.
        
        Teaching Note: ACCEPTABLE isinstance() USAGE!
        
        This shows the ONLY acceptable use of isinstance in SDA:
        at boundaries with external systems (here, Python's AST).
        
        We use isinstance(value, str) because:
        1. ast.Constant can hold any type (str, int, None, etc.)
        2. We're at the AST boundary
        3. After this check, we work with typed strings
        
        The len > 1 check filters out single characters which
        are unlikely to be domain concepts.
        """
        value = getattr(node, 'value', None)  # Teaching: Boundary operation - AST access
        line_no = getattr(node, 'lineno', 0)  # Teaching: Safe default for line number
        
        # Teaching: BOUNDARY isinstance - this is acceptable!
        # We're checking type of data from external system (AST)
        is_valid_string = isinstance(value, str) and len(value) > 1
        
        # Teaching: Even after isinstance, we use dispatch!
        # The str(value) cast is redundant but shows type discipline
        handlers: dict[bool, Callable[[], None]] = {
            True: lambda: literals[str(value)].append(line_no),  # Collect the literal
            False: lambda: None  # Ignore non-strings or short strings
        }
        handlers[is_valid_string]()  # Execute selected handler


class LiteralAnalyzer:
    """Analyzer for string literal patterns in Python code.
    
    WHAT: Orchestrates tree-wide analysis of string literals to find
    repetition patterns indicating missing domain abstractions.
    
    WHY: Unlike node-by-node analyzers, this needs to see the whole
    tree to detect patterns across the file.
    
    HOW: Delegates to LiteralDomain to collect all literals, then
    analyze them for repetition patterns.
    
    Teaching Note:
        This analyzer is called differently - analyze_tree() instead
        of analyze_node(). This signals that it needs the entire AST,
        not individual nodes. This is a different analysis strategy
        for cross-cutting concerns.
    
    SDA Pattern Demonstrated:
        Batch Analysis - Some patterns can only be detected by looking
        at the whole, not the parts. This requires different architecture.
    """
    
    @classmethod
    def analyze_tree(cls, tree: ast.AST, context: "RichAnalysisContext") -> list["Finding"]:
        """Analyze entire tree for string literal patterns.
        
        Teaching: Two-phase analysis:
        1. Collection phase: Gather all literals
        2. Analysis phase: Find patterns
        
        This separation allows for complex pattern detection that
        wouldn't be possible with single-pass node analysis.
        """
        domain = LiteralDomain.collect_from_tree(tree, context)
        return domain.analyze(context)