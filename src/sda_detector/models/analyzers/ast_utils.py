"""Shared AST utilities for analyzers following SDA patterns - Common AST Operations.

PURPOSE:
This module provides shared utilities for AST analysis, demonstrating how to
extract information from Python's AST using pure type dispatch patterns.

SDA PRINCIPLES DEMONSTRATED:
1. **Type-Based Dispatch**: Maps Python types to extractors/classifiers
2. **Pure Functions**: All utilities are stateless and deterministic
3. **Rich Metadata**: Wraps raw AST data in semantic domain models
4. **Computed Properties**: Derived information calculated on demand
5. **Boundary Isolation**: getattr only used at AST boundaries

LEARNING GOALS:
- Understand how to extract information from AST nodes safely
- Learn type-based dispatch as alternative to isinstance chains
- Master the pattern of wrapping external data in domain models
- See how to classify nodes by semantic meaning
- Recognize patterns for handling recursive structures

ARCHITECTURE NOTES:
This module is the bridge between Python's dynamic AST and our typed domain.
Every function here converts untyped AST data into strongly-typed domain models
using pure dispatch patterns - no conditionals needed.

Teaching Example:
    >>> # From raw AST node:
    >>> node = ast.FunctionDef(name="calculate_total", ...)
    >>> 
    >>> # Extract typed metadata:
    >>> metadata = extract_ast_metadata(node)
    >>> print(metadata.category)  # ASTNodeCategory.STRUCTURAL
    >>> print(metadata.name)  # "calculate_total"
    >>> print(metadata.priority)  # 1 (computed from category)

Key Insight:
By centralizing AST operations here, we keep boundary operations isolated
and ensure all analyzers use consistent extraction patterns.
"""

import ast
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from ..core_types import ASTNodeCategory

from ..core_types import ASTNodeCategory


class ASTNodeMetadata(BaseModel):
    """Rich metadata extracted from AST nodes using Pydantic intelligence.
    
    WHAT: A typed wrapper around AST node information, providing semantic
    meaning to raw AST data.
    
    WHY: AST nodes have attributes scattered across different node types.
    This model provides a uniform interface with computed properties.
    
    HOW: Extracts core information (category, line, name) and computes
    derived properties (priority, structural checks) on demand.
    
    Teaching Note:
        This is the "wrapper pattern" - taking untyped external data
        and wrapping it in a typed domain model. After wrapping, all
        operations are type-safe and consistent.
    
    SDA Pattern Demonstrated:
        Rich Metadata Objects - Instead of passing around raw AST nodes,
        we extract and enrich the data we need into domain models.
    """

    model_config = ConfigDict(frozen=True)

    category: ASTNodeCategory
    line_number: int = Field(ge=0, description="Line number in source code")
    name: str = Field(description="Semantic name of the node")

    @computed_field
    @property
    def priority(self) -> int:
        """Computed priority for analysis ordering.
        
        Teaching: Delegation to enum - the category knows its priority,
        we just ask for it. This keeps priority logic centralized.
        """
        return self.category.analysis_priority

    @computed_field
    @property
    def is_structural(self) -> bool:
        """Is this a structural element (class/function)?"""
        return self.category == ASTNodeCategory.STRUCTURAL

    @computed_field
    @property
    def is_behavioral(self) -> bool:
        """Is this a behavioral element (call/attribute)?"""
        return self.category == ASTNodeCategory.BEHAVIORAL


def extract_ast_name(node: ast.AST) -> str:
    """Extract semantic name from AST node using pure type dispatch.
    
    Teaching Note: TYPE-BASED DISPATCH FOR NAME EXTRACTION
    
    Different AST nodes store their "name" in different attributes:
    - FunctionDef: node.name
    - Name: node.id
    - Attribute: node.attr
    - Call: recursive extraction from node.func
    
    Instead of if/elif checking types, we map each type to a
    lambda that knows how to extract its name. This is pure
    dispatch - no conditionals!
    
    The recursive case (Call) shows how dispatch can handle
    complex extraction logic.
    
    Pure discriminated union pattern - no isinstance or hasattr.
    """
    from collections.abc import Callable
    from typing import Any
    
    # Teaching: Type-based dispatch - each type knows how to extract its name
    # Using lambdas for inline extraction logic
    name_extractors: dict[type[ast.AST], Callable[[Any], str]] = {
        ast.FunctionDef: lambda n: n.name,
        ast.AsyncFunctionDef: lambda n: n.name,
        ast.ClassDef: lambda n: n.name,
        ast.Name: lambda n: n.id,
        ast.Attribute: lambda n: n.attr,
        ast.Call: lambda n: extract_ast_name(n.func) if n.func else "unknown_call",  # Teaching: Recursive!
        ast.If: lambda n: extract_ast_name(n.test) if n.test else "condition",
    }
    
    node_type = type(node)
    # Teaching: Default lambda creates descriptive name for unknown types
    extractor = name_extractors.get(node_type, lambda n: f"unknown_{type(n).__name__.lower()}")
    
    # Teaching: Pure function dispatch - no conditionals!
    return extractor(node)


def classify_ast_node(node: ast.AST) -> ASTNodeCategory:
    """Classify AST node into semantic category using pure type dispatch.
    
    Teaching Note: SEMANTIC CLASSIFICATION OF AST NODES
    
    This groups AST nodes by their semantic meaning:
    - STRUCTURAL: Define program structure (classes, functions)
    - CONTROL_FLOW: Affect execution flow (if, for, try)
    - BEHAVIORAL: Perform operations (calls, attribute access)
    - DATA: Hold values (constants, names)
    
    This classification helps prioritize analysis - structural
    elements are more important than data elements for architecture.
    
    Notice: No isinstance chains! Just a dictionary lookup.
    
    Pure discriminated union - no isinstance chains.
    """
    # Teaching: Exhaustive mapping of common AST node types
    category_mapping = {
        # STRUCTURAL: Define architecture - highest priority
        ast.FunctionDef: ASTNodeCategory.STRUCTURAL,
        ast.AsyncFunctionDef: ASTNodeCategory.STRUCTURAL,
        ast.ClassDef: ASTNodeCategory.STRUCTURAL,
        ast.Module: ASTNodeCategory.STRUCTURAL,
        
        # CONTROL_FLOW: Business logic often lives here
        ast.If: ASTNodeCategory.CONTROL_FLOW,
        ast.For: ASTNodeCategory.CONTROL_FLOW,
        ast.While: ASTNodeCategory.CONTROL_FLOW,
        ast.Try: ASTNodeCategory.CONTROL_FLOW,
        ast.ExceptHandler: ASTNodeCategory.CONTROL_FLOW,
        
        # BEHAVIORAL: How code interacts with other code
        ast.Call: ASTNodeCategory.BEHAVIORAL,
        ast.Attribute: ASTNodeCategory.BEHAVIORAL,
        ast.BinOp: ASTNodeCategory.BEHAVIORAL,
        ast.UnaryOp: ASTNodeCategory.BEHAVIORAL,
        ast.Compare: ASTNodeCategory.BEHAVIORAL,
        
        # DATA: Simple values - lowest analysis priority
        ast.Name: ASTNodeCategory.DATA,
        ast.Constant: ASTNodeCategory.DATA,
    }
    
    # Teaching: Default to DATA for unknown nodes (safest assumption)
    return category_mapping.get(type(node), ASTNodeCategory.DATA)


def extract_ast_metadata(node: ast.AST) -> ASTNodeMetadata:
    """Extract rich domain metadata from raw AST node.
    
    Teaching Note: FACTORY FUNCTION PATTERN
    
    This is the main entry point - it orchestrates the extraction:
    1. Classify the node type
    2. Extract the name
    3. Get the line number (boundary operation)
    4. Wrap in domain model
    
    After this function, no more AST access is needed - everything
    is in the typed ASTNodeMetadata model.
    
    Pure factory function using discriminated union dispatch.
    """
    category = classify_ast_node(node)
    name = extract_ast_name(node)
    
    # Teaching: Line number extraction - boundary operation
    # getattr is acceptable here because we're at the AST boundary
    # Most nodes have lineno, but we provide safe default (0)
    line_number = getattr(node, 'lineno', 0)  # BOUNDARY: AST attribute access
    
    return ASTNodeMetadata(
        category=category,
        line_number=line_number,
        name=name
    )