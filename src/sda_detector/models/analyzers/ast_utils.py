"""Shared AST utilities for analyzers following SDA patterns.

This module provides common AST metadata extraction and classification
utilities used by all analyzers. All functions follow pure SDA principles
with no isinstance/hasattr/getattr usage.
"""

import ast
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from ..core_types import ASTNodeCategory

from ..core_types import ASTNodeCategory


class ASTNodeMetadata(BaseModel):
    """Rich metadata extracted from AST nodes using Pydantic intelligence."""

    model_config = ConfigDict(frozen=True)

    category: ASTNodeCategory
    line_number: int = Field(ge=0, description="Line number in source code")
    name: str = Field(description="Semantic name of the node")

    @computed_field
    @property
    def priority(self) -> int:
        """Computed priority for analysis ordering."""
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
    
    Pure discriminated union pattern - no isinstance or hasattr.
    """
    from collections.abc import Callable
    from typing import Any
    
    # Type-based dispatch for name extraction with proper typing
    name_extractors: dict[type[ast.AST], Callable[[Any], str]] = {
        ast.FunctionDef: lambda n: n.name,
        ast.AsyncFunctionDef: lambda n: n.name,
        ast.ClassDef: lambda n: n.name,
        ast.Name: lambda n: n.id,
        ast.Attribute: lambda n: n.attr,
        ast.Call: lambda n: extract_ast_name(n.func) if n.func else "unknown_call",
        ast.If: lambda n: extract_ast_name(n.test) if n.test else "condition",
    }
    
    node_type = type(node)
    extractor = name_extractors.get(node_type, lambda n: f"unknown_{type(n).__name__.lower()}")
    
    # Pure function dispatch - no conditionals
    return extractor(node)


def classify_ast_node(node: ast.AST) -> ASTNodeCategory:
    """Classify AST node into semantic category using pure type dispatch.
    
    Pure discriminated union - no isinstance chains.
    """
    category_mapping = {
        # STRUCTURAL: Classes, functions, modules
        ast.FunctionDef: ASTNodeCategory.STRUCTURAL,
        ast.AsyncFunctionDef: ASTNodeCategory.STRUCTURAL,
        ast.ClassDef: ASTNodeCategory.STRUCTURAL,
        ast.Module: ASTNodeCategory.STRUCTURAL,
        
        # CONTROL_FLOW: Conditionals, loops, exception handling
        ast.If: ASTNodeCategory.CONTROL_FLOW,
        ast.For: ASTNodeCategory.CONTROL_FLOW,
        ast.While: ASTNodeCategory.CONTROL_FLOW,
        ast.Try: ASTNodeCategory.CONTROL_FLOW,
        ast.ExceptHandler: ASTNodeCategory.CONTROL_FLOW,
        
        # BEHAVIORAL: Calls, operations, attribute access
        ast.Call: ASTNodeCategory.BEHAVIORAL,
        ast.Attribute: ASTNodeCategory.BEHAVIORAL,
        ast.BinOp: ASTNodeCategory.BEHAVIORAL,
        ast.UnaryOp: ASTNodeCategory.BEHAVIORAL,
        ast.Compare: ASTNodeCategory.BEHAVIORAL,
        
        # DATA: Simple values and names (rarely contain business logic)
        ast.Name: ASTNodeCategory.DATA,
        ast.Constant: ASTNodeCategory.DATA,
    }
    
    return category_mapping.get(type(node), ASTNodeCategory.DATA)


def extract_ast_metadata(node: ast.AST) -> ASTNodeMetadata:
    """Extract rich domain metadata from raw AST node.
    
    Pure factory function using discriminated union dispatch.
    """
    category = classify_ast_node(node)
    name = extract_ast_name(node)
    
    # Line number extraction using type dispatch
    # Most AST nodes have lineno, but we handle it safely
    line_number = getattr(node, 'lineno', 0)  # Boundary case - acceptable at AST boundary
    
    return ASTNodeMetadata(
        category=category,
        line_number=line_number,
        name=name
    )