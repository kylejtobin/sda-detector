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

# Minimal public API - only what external users need
from .models import ArchitectureReport, ModuleType, PatternType, PositivePattern
from .service import analyze_module as service_analyze_module
from .service import main

# Version info
__version__ = "0.1.0"
__author__ = "SDA Architecture Team"
__description__ = "Semantic Domain Architecture pattern detector for Python"


# Convenience functions for programmatic usage
def analyze_module(module_path: str, module_name: str | None = None) -> ArchitectureReport:
    """Analyze a module for SDA compliance.

    Args:
        module_path: Path to the Python file or directory to analyze
        module_name: Optional display name for the module in reports

    Returns:
        ArchitectureReport containing all findings and metrics
    """
    return service_analyze_module(module_path, module_name)


def print_report(report: ArchitectureReport, module_name: str) -> None:
    """Print an analysis report to the console.

    Args:
        report: ArchitectureReport from analyze_module()
        module_name: Display name for the module
    """
    # Simple console output
    print(f"🧠 SDA ARCHITECTURE ANALYSIS - {report.module_type.upper()}")
    print("=" * 70)

    print("🔍 SDA VIOLATIONS DETECTED:")
    for violation_type, findings in report.violations.items():
        count = len(findings)
        status = "🔍" if count > 0 else "⚪"
        print(f"  {violation_type:30} {count:3} {status}")

    print("\n📊 ARCHITECTURAL FEATURES:")
    for pattern_type, findings in report.patterns.items():
        count = len(findings)
        status = "📊" if count > 0 else "⚪"
        print(f"  {pattern_type:30} {count:3} {status}")

    dist = report.pattern_distribution
    print(f"\nDISTRIBUTION: {dist['patterns']:.1%} patterns, {dist['violations']:.1%} violations")


# Minimal public API for external users
__all__ = [
    # Core domain models for type hints
    "ArchitectureReport",
    "ModuleType",
    "PatternType",
    "PositivePattern",
    # Metadata
    "__author__",
    "__description__",
    "__version__",
    # Main API functions
    "analyze_module",
    "main",
    "print_report",
]
