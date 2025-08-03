"""Protocol interfaces for SDA detector components.

Protocols define "what we need from the outside world" - the interface contracts
that enable dependency injection and testability while maintaining type safety.

These are pure interface definitions with no implementation.
"""

import ast
from typing import Any, Protocol

from .models import ArchitectureReport, Finding, ModuleType, PositivePattern, ViolationType


class CodeAnalyzer(Protocol):
    """Protocol for analyzing Python code and detecting architectural patterns.

    This defines the interface that any AST-based code analyzer must implement.
    It enables us to swap out different analysis strategies while maintaining
    type safety and consistent interfaces.
    """

    def set_file(self, filename: str) -> None:
        """Set the current file being analyzed."""
        ...

    def visit(self, node: ast.AST) -> None:
        """Visit an AST node and analyze it for patterns."""
        ...

    @property
    def findings(self) -> dict[str, list[Finding]]:
        """Get all findings discovered during analysis."""
        ...


class ViolationDetector(Protocol):
    """Protocol for detecting specific types of SDA violations.

    This enables pluggable detection strategies for different violation types.
    Each detector can focus on a specific aspect of SDA compliance.
    """

    def detect_violations(self, node: ast.AST, context: dict[str, Any]) -> list[Finding]:
        """Detect violations in the given AST node."""
        ...

    def supported_violation_types(self) -> list[ViolationType]:
        """Return the violation types this detector can find."""
        ...


class ReportFormatter(Protocol):
    """Protocol for formatting analysis reports in different output formats.

    This enables multiple output formats (console, JSON, HTML, etc.)
    while maintaining the same analysis logic.
    """

    def format_report(self, report: ArchitectureReport, module_name: str) -> str:
        """Format the analysis report for display."""
        ...


class FileReader(Protocol):
    """Protocol for reading source files.

    This abstracts file system access and enables testing with
    in-memory files or different file sources.
    """

    def read_file(self, filepath: str) -> str:
        """Read the contents of a file."""
        ...

    def list_python_files(self, directory: str) -> list[str]:
        """List all Python files in a directory."""
        ...


class ModuleClassifier(Protocol):
    """Protocol for classifying modules by their architectural context.

    Different module types (domain, infrastructure, tooling) have different
    architectural expectations and tolerance for certain patterns.
    """

    def classify_module(self, file_path: str) -> ModuleType:
        """Classify a module based on its file path and contents."""
        ...

    @property
    def classification_rules(self) -> dict[ModuleType, list[str]]:
        """Get the rules used for module classification."""
        ...


class PatternDetector(Protocol):
    """Protocol for detecting positive SDA patterns.

    This enables specialized detectors for different types of positive
    patterns like Pydantic usage, type dispatch, computed fields, etc.
    """

    def detect_patterns(self, node: ast.AST, context: dict[str, Any]) -> list[Finding]:
        """Detect positive patterns in the given AST node."""
        ...

    def supported_pattern_types(self) -> list[PositivePattern]:
        """Return the pattern types this detector can find."""
        ...


class AnalysisReporter(Protocol):
    """Protocol for generating and outputting analysis reports.

    This abstracts the reporting mechanism and enables different
    output destinations (console, file, web service, etc.).
    """

    def generate_report(self, findings: dict[str, list[Finding]]) -> ArchitectureReport:
        """Generate a comprehensive report from findings."""
        ...

    def output_report(self, report: ArchitectureReport, destination: str) -> None:
        """Output the report to the specified destination."""
        ...
