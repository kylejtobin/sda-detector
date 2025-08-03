"""Service layer for SDA detector - orchestration only, no business decisions.

Services coordinate external resources and infrastructure. They don't make
business decisions - models do. Services handle the "when" and "where",
while models handle the "what" and "why".
"""

import ast
import os
import sys
from typing import TYPE_CHECKING

from .models import (
    AnalysisContext,
    ArchitectureReport,
    Finding,
    ModuleType,
    PositivePattern,
    ReportFormatter,
    ViolationType,
)

if TYPE_CHECKING:
    pass


class ModuleClassifier:
    """Concrete implementation of module classification using configuration.

    Now uses the Pydantic configuration model instead of hard-coded patterns.
    This demonstrates SDA: configuration as intelligent domain models.
    """

    def __init__(self) -> None:
        """Initialize with configuration-driven classification."""
        from .config import config

        self.config = config

    @property
    def classification_rules(self) -> dict["ModuleType", list[str]]:
        """Type dispatch rules from configuration model."""
        return self.config.classification_rules.all_patterns

    def classify_module(self, file_path: str) -> "ModuleType":
        """Classify module using configuration model."""
        return self.config.classification_rules.classify_by_path(file_path)


class NodeAnalyzer:
    """Static analysis utilities for working with Python AST nodes.

    The Abstract Syntax Tree is Python's internal representation of parsed code.
    Instead of working with raw text, we analyze the structured representation
    which gives us semantic understanding of the code.

    This class provides utilities to extract information from AST nodes using
    SDA principles - type dispatch instead of isinstance() chains.
    """

    @staticmethod
    def extract_name(node: ast.AST) -> str:
        """Extract the name/identifier from an AST node.

        Different AST node types store names in different attributes:
        - ast.Name nodes have an 'id' attribute
        - ast.Attribute nodes have an 'attr' attribute
        - ast.Constant nodes have a 'value' attribute

        This is a boundary function that deals with external AST structure,
        so hasattr() checks are acceptable here (we're at the system boundary).
        """
        # AST boundary - hasattr checks are acceptable when dealing with external structures
        if hasattr(node, "id"):  # ast.Name nodes (variables, functions)
            return str(node.id)
        elif hasattr(node, "attr"):  # ast.Attribute nodes (object.attribute)
            return str(node.attr)
        elif hasattr(node, "value"):  # ast.Constant nodes (literals)
            return str(node.value)
        else:
            return ""  # Unknown node type

    @staticmethod
    def analyze_class_bases(bases: list[ast.expr]) -> dict[PositivePattern, list[str]]:
        """Analyze class inheritance patterns to detect SDA patterns."""
        # Extract names from all base class AST nodes
        base_names = [NodeAnalyzer.extract_name(base) for base in bases]

        # Type dispatch pattern detection using dictionary and list comprehensions
        base_patterns = {
            PositivePattern.PYDANTIC_MODELS: [name for name in base_names if name == "BaseModel"],
            PositivePattern.BEHAVIORAL_ENUMS: [name for name in base_names if name in ["Enum", "StrEnum", "IntEnum"]],
            PositivePattern.PROTOCOLS: [name for name in base_names if name == "Protocol"],
        }

        return base_patterns

    @staticmethod
    def analyze_function_decorators(decorators: list[ast.expr]) -> dict[PositivePattern, list[str]]:
        """Analyze function decorators to detect SDA patterns."""
        # Extract decorator names from AST nodes
        decorator_names = [NodeAnalyzer.extract_name(d) for d in decorators]

        # Type dispatch for decorator pattern detection
        decorator_patterns = {
            PositivePattern.COMPUTED_FIELDS: [name for name in decorator_names if name == "computed_field"],
            PositivePattern.CUSTOM_VALIDATORS: [
                name for name in decorator_names if name in ["field_validator", "model_validator"]
            ],
            PositivePattern.CUSTOM_SERIALIZERS: [name for name in decorator_names if name == "field_serializer"],
            PositivePattern.ROOT_VALIDATORS: [name for name in decorator_names if name == "root_validator"],
            PositivePattern.ENUM_METHODS: [name for name in decorator_names if name == "property"],
        }

        return decorator_patterns

    @staticmethod
    def analyze_function_call(func_name: str) -> dict[str, list[str]]:
        """Analyze function calls to detect both violations and positive patterns."""
        # Type dispatch table for analyzing function calls
        call_patterns: dict[str, list[str]] = {
            # Anti-patterns that violate SDA principles
            ViolationType.ISINSTANCE_VIOLATIONS: ["isinstance"] if func_name == "isinstance" else [],
            ViolationType.HASATTR_VIOLATIONS: ["hasattr"] if func_name == "hasattr" else [],
            ViolationType.GETATTR_VIOLATIONS: ["getattr"] if func_name == "getattr" else [],
            ViolationType.MANUAL_JSON_SERIALIZATION: [func_name]
            if func_name in ["json.dumps", "json.loads", "dumps", "loads"]
            else [],
            # Positive patterns that align with SDA
            PositivePattern.PYDANTIC_VALIDATION: [func_name]
            if func_name in ["model_validate", "model_validate_json"]
            else [],
            PositivePattern.PYDANTIC_SERIALIZATION: [func_name]
            if func_name in ["model_dump", "model_dump_json"]
            else [],
            PositivePattern.IMMUTABLE_UPDATES: [func_name] if func_name == "model_copy" else [],
            PositivePattern.FIELD_CONSTRAINTS: [func_name] if func_name == "Field" else [],
            PositivePattern.ANNOTATED_TYPES: [func_name] if func_name == "Annotated" else [],
        }

        return call_patterns


class SDAArchitectureDetector(ast.NodeVisitor):
    """AST visitor that detects SDA patterns using Pydantic intelligence.

    This class demonstrates SDA principles by:
    1. Using immutable Pydantic context instead of mutable state
    2. Recording findings as typed models, not raw dictionaries
    3. Using type dispatch in visit methods instead of conditionals
    4. Delegating analysis logic to specialized analyzer utilities
    """

    def __init__(self) -> None:
        """Initialize detector with empty findings and default context."""
        # Immutable context using Pydantic model - classifier will be set later
        self.context = AnalysisContext()

        # Initialize findings dictionary for all pattern types
        self.findings: dict[str, list[Finding]] = {violation: [] for violation in ViolationType}
        self.findings.update({pattern: [] for pattern in PositivePattern})

    def set_file(self, filename: str) -> None:
        """Update analysis context for a new file using immutable updates."""
        # Initialize classifier if not already set
        if self.context.classifier is None:
            classifier = ModuleClassifier()
            self.context = self.context.model_copy(update={"current_file": filename, "classifier": classifier})
        else:
            self.context = self.context.model_copy(update={"current_file": filename})

    def _record_finding(self, finding_type: str, node: ast.AST, description: str) -> None:
        """Record a finding using typed Pydantic model instead of raw dict."""
        finding = Finding(
            file_path=self.context.current_file,
            line_number=getattr(node, "lineno", 0),  # Boundary getattr for AST
            description=description,
        )
        self.findings[finding_type].append(finding)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyze class definitions for patterns."""
        old_context = self.context
        self.context = self.context.model_copy(update={"current_class": node.name})

        # Analyze inheritance patterns
        base_patterns = NodeAnalyzer.analyze_class_bases(node.bases)
        for pattern_type, names in base_patterns.items():
            for name in names:
                self._record_finding(pattern_type, node, f"{name}: {node.name}")

        # Check if this is an enum class using pure type dispatch
        enum_patterns = [PositivePattern.BEHAVIORAL_ENUMS]
        is_enum = any(self.findings[pattern] for pattern in enum_patterns)

        # Boolean coercion array indexing - SDA teaching moment
        enum_context_updates = [
            {},  # False case (index 0)
            {"in_enum_class": True},  # True case (index 1)
        ]
        self.context = self.context.model_copy(update=enum_context_updates[int(is_enum)])

        # Analyze for anemic service patterns
        self._analyze_anemic_service(node)

        self.generic_visit(node)
        self.context = old_context

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function definitions for patterns."""
        old_context = self.context
        self.context = self.context.model_copy(update={"current_function": node.name})

        # Analyze decorators
        decorator_patterns = NodeAnalyzer.analyze_function_decorators(node.decorator_list)
        for pattern_type, names in decorator_patterns.items():
            for name in names:
                self._record_finding(pattern_type, node, f"@{name} {node.name}")

        self.generic_visit(node)
        self.context = old_context

    def visit_Call(self, node: ast.Call) -> None:
        """Detect patterns in function calls."""
        func_name = NodeAnalyzer.extract_name(node.func)

        # Check for json.dumps/loads specifically
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "json"
            and func_name in ["dumps", "loads"]
        ):
            self._record_finding(
                ViolationType.MANUAL_JSON_SERIALIZATION, node, f"json.{func_name}() manual serialization"
            )

        # Enhanced dict.get() analysis
        elif func_name == "get" and isinstance(node.func, ast.Attribute) and node.args:
            self._analyze_dict_get_call(node)
        else:
            # Standard function call analysis
            call_patterns = NodeAnalyzer.analyze_function_call(func_name)
            for pattern_type, names in call_patterns.items():
                for name in names:
                    description = f"{name}() runtime check" if pattern_type in ViolationType else f"{name} usage"
                    self._record_finding(pattern_type, node, description)

        self.generic_visit(node)

    def _analyze_dict_get_call(self, node: ast.Call) -> None:
        """Conservative analysis of dict.get() calls - only flag obvious violations."""
        key = node.args[0]  # First argument is the key

        # Only flag string literals as violations - everything else is neutral
        is_string_literal = isinstance(key, ast.Constant) and isinstance(key.value, str)
        is_enum_self = isinstance(key, ast.Name) and key.id == "self"
        is_enum_attribute = isinstance(key, ast.Attribute)
        is_tuple_key = isinstance(key, ast.Tuple)
        is_complex_key = (
            is_tuple_key and isinstance(key, ast.Tuple) and any(isinstance(elt, ast.Attribute) for elt in key.elts)
        )

        # Clear type dispatch patterns
        is_obvious_type_dispatch = (
            is_enum_self  # transitions.get(self, default)
            or is_enum_attribute  # handlers.get(event.type, default)
            or is_complex_key  # cases.get((self.STATE, condition), default)
        )

        if is_string_literal:
            # String literal keys are clear violations
            key_value = key.value if isinstance(key, ast.Constant) and isinstance(key.value, str) else repr(key)
            self._record_finding(
                ViolationType.DICT_GET_VIOLATIONS, node, f"get() with string literal '{key_value}' (use typed model)"
            )
        elif is_obvious_type_dispatch:
            # Clear type dispatch patterns
            key_desc = "enum self" if is_enum_self else "typed key"
            self._record_finding(PositivePattern.TYPE_DISPATCH_TABLES, node, f"type dispatch lookup with {key_desc}")
        # Everything else: no classification (neutral)

    def visit_If(self, node: ast.If) -> None:
        """Analyze conditional logic for SDA compliance."""
        # Simple boundary condition detection
        test_name = NodeAnalyzer.extract_name(node.test)

        # Type dispatch for conditional analysis
        if test_name == "TYPE_CHECKING":
            self._record_finding(PositivePattern.TYPE_CHECKING_IMPORTS, node, "TYPE_CHECKING import")
        elif self.context.is_boundary_context:
            self._record_finding(PositivePattern.BOUNDARY_CONDITIONS, node, "boundary error handling")
        else:
            self._record_finding(ViolationType.BUSINESS_CONDITIONALS, node, "business logic conditional")

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Analyze try/except patterns."""
        # Infrastructure boundary context gets lenient treatment
        if self.context.is_boundary_context:
            self._record_finding(PositivePattern.BOUNDARY_CONDITIONS, node, "boundary error handling")
        else:
            self._record_finding(ViolationType.TRY_EXCEPT_VIOLATIONS, node, "try/except instead of type safety")

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Analyze attribute access patterns, especially enum .value unwrapping."""
        # Check for enum .value unwrapping (primitive obsession)
        if node.attr == "value" and isinstance(node.value, ast.Attribute):
            # Pattern like SomeEnum.SOME_VALUE.value
            enum_name = NodeAnalyzer.extract_name(node.value.value)  # SomeEnum
            enum_member = node.value.attr  # SOME_VALUE

            # Check if it looks like an enum pattern
            if enum_name and enum_member and enum_member.isupper():  # CONSTANT_CASE strongly suggests enum member
                self._record_finding(
                    ViolationType.ENUM_VALUE_UNWRAPPING,
                    node,
                    f"enum value unwrapping - consider StrEnum for automatic conversion, or validate if external serialization is needed instead of {enum_name}.{enum_member}.value",
                )

        self.generic_visit(node)

    def _analyze_anemic_service(self, node: ast.ClassDef) -> None:
        """Analyze service classes for anemic patterns."""
        # Only analyze classes that claim to be services
        if not node.name.endswith("Service"):
            return

        # Get all methods in the class
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name != "__init__"]

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
            description = (
                f"anemic service - {', '.join(anemic_indicators)} - consider domain model methods or focused services"
            )
            self._record_finding(ViolationType.ANEMIC_SERVICES, node, description)

    def _is_static_or_classmethod(self, method: ast.FunctionDef) -> bool:
        """Check if method is static or classmethod."""
        decorator_names = [NodeAnalyzer.extract_name(d) for d in method.decorator_list]
        return "staticmethod" in decorator_names or "classmethod" in decorator_names

    def _is_utility_method_name(self, method_name: str) -> bool:
        """Check if method name suggests utility/helper function."""
        utility_patterns = [
            "helper",
            "util",
            "process",
            "handle",
            "execute",
            "run",
            "get_",
            "set_",
            "create_",
            "update_",
            "delete_",
            "parse_",
            "convert_",
            "transform_",
            "format_",
            "validate_",
        ]
        return any(pattern in method_name.lower() for pattern in utility_patterns)


class FileSystemService:
    """Service for file system operations."""

    @staticmethod
    def read_file(filepath: str) -> str:
        """Read file contents."""
        with open(filepath, encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def list_python_files(path: str) -> list[str]:
        """List Python files in a directory or return single file."""
        if os.path.isfile(path):
            return [path]
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".py")]


class DetectionService:
    """Main service that orchestrates the SDA detection process.

    This service coordinates file reading, AST parsing, and analysis.
    It makes no business decisions - those are handled by the domain models.
    """

    def __init__(self, detector: SDAArchitectureDetector | None = None) -> None:
        """Initialize with optional custom detector."""
        self.detector = detector or SDAArchitectureDetector()
        self.file_service = FileSystemService()

    def analyze_module(self, module_path: str, module_name: str) -> ArchitectureReport:
        """Analyze a module for SDA compliance."""
        files = self.file_service.list_python_files(module_path)

        for filepath in files:
            try:
                content = self.file_service.read_file(filepath)
                tree = ast.parse(content)

                relative_path = filepath.replace(module_path, module_name) if module_path != filepath else module_name
                self.detector.set_file(relative_path)
                self.detector.visit(tree)
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

        return self._generate_report(self.detector.findings)

    def _generate_report(self, findings: dict[str, list[Finding]]) -> ArchitectureReport:
        """Generate comprehensive architecture report."""
        # Categorize findings using type dispatch
        violations = {violation_type: findings.get(violation_type, []) for violation_type in ViolationType}
        patterns = {pattern_type: findings.get(pattern_type, []) for pattern_type in PositivePattern}

        return ArchitectureReport(violations=violations, patterns=patterns)


class ReportingService:
    """Service for generating and displaying analysis reports."""

    def __init__(self, formatter: ReportFormatter | None = None) -> None:
        """Initialize with optional custom formatter."""
        self.formatter = formatter or ReportFormatter()

    def print_report(self, report: ArchitectureReport, module_name: str) -> None:
        """Print objective architecture analysis report using domain models."""
        print(self.formatter.format_header(module_name))

        print(self.formatter.format_section_header("🔍 SDA PATTERNS DETECTED:"))
        for violation_type, items in report.violations.items():
            count = len(items)
            status = self.formatter.violation_status_indicator[count == 0]
            print(self.formatter.format_item_line(violation_type, count, status))

            for item in items[: self.formatter.config.summary_item_limit]:
                print(self.formatter.format_finding_detail(item))

            if self.formatter.should_show_overflow(count):
                remaining = count - self.formatter.config.summary_item_limit
                print(self.formatter.format_overflow_message(remaining))

        print()
        print(self.formatter.format_section_header("📊 ARCHITECTURAL FEATURES:"))
        for pattern_type, items in report.patterns.items():
            count = len(items)
            status = self.formatter.pattern_status_indicator[count > 0]
            print(self.formatter.format_item_line(pattern_type, count, status))

            for item in items[: self.formatter.config.summary_item_limit]:
                print(self.formatter.format_finding_detail(item))

            if self.formatter.should_show_overflow(count):
                remaining = count - self.formatter.config.summary_item_limit
                print(self.formatter.format_overflow_message(remaining))

        print()
        print(f"MODULE TYPE: {report.module_type}")
        print(f"FILES ANALYZED: {report.files_analyzed}")
        print(f"TOTAL VIOLATIONS: {report.total_violations}")
        print(f"TOTAL PATTERNS: {report.total_patterns}")

        # Pure observational metrics - no judgment
        dist = report.pattern_distribution
        print(f"DISTRIBUTION: {dist['patterns']:.1%} patterns, {dist['violations']:.1%} violations")


def main() -> None:
    """CLI entry point for the SDA detector."""
    if len(sys.argv) < 2:
        print("Usage: python -m sda_detector <module_path> [module_name]")
        sys.exit(1)

    module_path = sys.argv[1]
    module_name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(module_path)

    # Service orchestration
    detection_service = DetectionService()
    reporting_service = ReportingService()

    # Execute analysis
    report = detection_service.analyze_module(module_path, module_name)
    reporting_service.print_report(report, module_name)


if __name__ == "__main__":
    main()
