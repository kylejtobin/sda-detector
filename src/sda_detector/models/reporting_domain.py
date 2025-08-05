"""Reporting domain models for SDA architecture detection.

These models handle how we present analysis results: what goes in reports,
how we format output, and how we configure display preferences.

These models contain the business logic about HOW to present findings.
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .analysis_domain import Finding
from .core_types import ModuleType, PatternType, PositivePattern

if TYPE_CHECKING:
    pass  # config.py removed - using inline configuration


class ArchitectureReport(BaseModel):
    """Comprehensive architecture analysis report."""

    model_config = ConfigDict(frozen=True)

    violations: dict[PatternType, list[Finding]]
    patterns: dict[PositivePattern, list[Finding]]
    module_type: ModuleType = Field(default=ModuleType.MIXED, description="Type of module analyzed")

    @classmethod
    def from_findings(
        cls, findings: list[Finding], module_name: str, module_type: ModuleType, files: list[str]
    ) -> "ArchitectureReport":
        """Factory method for creating architecture reports from findings.

        This classmethod provides clean, type-safe report creation following
        SDA patterns. It encapsulates the classification logic and ensures
        consistent report generation.

        Args:
            findings: List of analysis findings to classify
            module_name: Name of the analyzed module
            module_type: Semantic classification of the module
            files: List of files that were analyzed

        Returns:
            New ArchitectureReport with classified findings

        SDA Principle: Factory methods provide clean domain model creation
        """
        from collections import defaultdict

        # Pure discriminated union classification - no conditionals
        violations: dict[PatternType, list[Finding]] = defaultdict(list)
        patterns: dict[PositivePattern, list[Finding]] = defaultdict(list)

        for finding in findings:
            # Check for violations (PatternType)
            if finding.pattern_category:
                violations[finding.pattern_category].append(finding)
            
            # Check for positive patterns (PositivePattern)
            if finding.pattern_type:
                patterns[finding.pattern_type].append(finding)

        return cls(violations=dict(violations), patterns=dict(patterns), module_type=module_type)

    @computed_field
    @property
    def total_violations(self) -> int:
        """Total count of SDA violations found across all types."""
        return sum(len(findings) for findings in self.violations.values())

    @computed_field
    @property
    def total_patterns(self) -> int:
        """Total count of positive SDA patterns found across all types."""
        return sum(len(findings) for findings in self.patterns.values())

    @computed_field
    @property
    def files_analyzed(self) -> int:
        """Count of unique files analyzed - pure observation."""
        all_files: set[str] = set()
        for findings in self.violations.values():
            all_files.update(f.file_path for f in findings)
        for findings in self.patterns.values():
            all_files.update(f.file_path for f in findings)
        return len(all_files)

    @computed_field
    @property
    def pattern_distribution(self) -> dict[str, float]:
        """Observable distribution of patterns vs violations using pure type system.

        Rule 020: "Transform conditionals into type intelligence"
        Rule 070: "Use Pydantic intelligence over procedural checks"
        """
        total = self.total_patterns + self.total_violations

        # SDA: Boolean coercion eliminates conditionals - Pydantic division safety
        safe_total = total or 1  # Type system handles division by zero

        # Pure type system calculation - zero conditionals
        return {
            "patterns": (self.total_patterns / safe_total) * bool(total),
            "violations": (self.total_violations / safe_total) * bool(total),
        }
