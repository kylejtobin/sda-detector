"""SDA Detector - Semantic Domain Architecture analysis tool.

This package provides tools for analyzing Python codebases to detect
architectural patterns that align with or violate SDA principles.

## Public API

For most users, these are the primary interfaces:

```python
# Command-line usage
from sda_detector import main

main()  # Uses sys.argv

# Programmatic usage
from sda_detector import analyze_module, print_report

report = analyze_module("path/to/code", "module_name")
print_report(report, "module_name")

# Custom analysis
from sda_detector import DetectionService, ReportingService

detection = DetectionService()
reporting = ReportingService()
report = detection.analyze_module("path", "name")
reporting.print_report(report, "name")
```

## Architecture

The package follows SDA principles in its own design:

- **Models** (`models.py`) - Domain objects with business logic
- **Protocols** (`protocols.py`) - Interface contracts
- **Services** (`services.py`) - Orchestration and infrastructure

The models contain ALL the business logic about what constitutes
violations, patterns, and how to analyze them. Services only
coordinate external resources (file system, AST parsing).
"""

# Core exports organized by module
from .models import (
    AnalysisConfig,
    AnalysisContext,
    ArchitectureReport,
    DisplayConfig,
    Finding,
    ModuleType,
    PositivePattern,
    ReportFormatter,
    ViolationType,
)
from .protocols import (
    AnalysisReporter,
    CodeAnalyzer,
    FileReader,
    PatternDetector,
    ViolationDetector,
)
from .protocols import (
    ModuleClassifier as ModuleClassifierProtocol,
)
from .protocols import (
    ReportFormatter as ReportFormatterProtocol,
)
from .services import (
    DetectionService,
    FileSystemService,
    ModuleClassifier,
    NodeAnalyzer,
    ReportingService,
    SDAArchitectureDetector,
    main,
)

# Version info
__version__ = "0.1.0"
__author__ = "SDA Architecture Team"
__description__ = "Semantic Domain Architecture pattern detector for Python"


# Convenience functions for programmatic usage
def analyze_module(module_path: str, module_name: str) -> ArchitectureReport:
    """Analyze a module for SDA compliance.

    Args:
        module_path: Path to the Python file or directory to analyze
        module_name: Display name for the module in reports

    Returns:
        ArchitectureReport containing all findings and metrics
    """
    service = DetectionService()
    return service.analyze_module(module_path, module_name)


def print_report(report: ArchitectureReport, module_name: str) -> None:
    """Print an analysis report to the console.

    Args:
        report: ArchitectureReport from analyze_module()
        module_name: Display name for the module
    """
    service = ReportingService()
    service.print_report(report, module_name)


# Public API for __all__
__all__ = [
    # Domain models
    "AnalysisConfig",
    "AnalysisContext",
    # Protocols (for dependency injection)
    "AnalysisReporter",
    "ArchitectureReport",
    "CodeAnalyzer",
    # Services
    "DetectionService",
    "DisplayConfig",
    "FileReader",
    # Implementations
    "FileSystemService",
    "Finding",
    "ModuleClassifier",
    "ModuleClassifierProtocol",
    "ModuleType",
    "NodeAnalyzer",
    "PatternDetector",
    "PositivePattern",
    "ReportFormatter",
    "ReportFormatterProtocol",
    "ReportingService",
    "SDAArchitectureDetector",
    "ViolationDetector",
    "ViolationType",
    # Metadata
    "__author__",
    "__description__",
    "__version__",
    # Main entry points
    "analyze_module",
    "main",
    "print_report",
]
