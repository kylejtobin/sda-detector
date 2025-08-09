"""Reporting domain models for SDA architecture detection - Presenting Intelligence.

PURPOSE:
This module defines how analysis results are aggregated, classified, and presented.
It demonstrates how reports can self-compute statistics without external services.

SDA PRINCIPLES DEMONSTRATED:
1. **Self-Computing Reports**: Reports calculate their own statistics
2. **Factory Methods**: Clean domain model creation from raw findings
3. **Computed Aggregations**: Derived metrics without manual calculation
4. **Type-Safe Collections**: Strongly typed dictionaries of findings
5. **Zero Division Safety**: Mathematical operations without conditionals

LEARNING GOALS:
- Understand how to aggregate data using computed fields
- Learn factory method patterns for complex model creation
- Master safe mathematical operations without try/except
- See how reports can be both data containers and calculators
- Recognize patterns for presenting complex analysis results

ARCHITECTURE NOTES:
The ArchitectureReport is the final output of analysis - it aggregates all
findings and computes statistics about them. By using computed fields for
all derived values, we ensure consistency and eliminate manual calculation
errors. The report knows how to present itself.

Teaching Example:
    >>> # Traditional approach (service calculates stats):
    >>> class ReportService:
    >>>     def calculate_totals(self, report):
    >>>         total = 0
    >>>         for findings in report.violations.values():
    >>>             total += len(findings)
    >>>         return total
    >>>     
    >>>     def calculate_percentage(self, report):
    >>>         total = self.calculate_totals(report)
    >>>         if total == 0:
    >>>             return 0.0
    >>>         return report.patterns / total * 100
    >>> 
    >>> # SDA approach (report calculates itself):
    >>> class ArchitectureReport(BaseModel):
    >>>     @computed_field
    >>>     @property
    >>>     def total_violations(self) -> int:
    >>>         return sum(len(f) for f in self.violations.values())
    >>>     
    >>>     @computed_field
    >>>     @property
    >>>     def violation_percentage(self) -> float:
    >>>         total = self.total_violations + self.total_patterns
    >>>         safe_total = total or 1  # Avoid division by zero
    >>>         return (self.total_violations / safe_total) * 100

Key Insight:
Reports aren't just data holders - they're intelligent aggregators that
understand how to compute their own statistics. This eliminates entire
classes of calculation bugs and keeps logic close to data.
"""

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .analysis_domain import Finding
from .core_types import ModuleType, PatternType, PositivePattern

if TYPE_CHECKING:
    pass  # config.py removed - using inline configuration


class ComplianceGrade(StrEnum):
    """Behavioral enum for compliance grading with self-describing presentation.
    
    This enum demonstrates pure SDA: Instead of if/else chains to determine
    grades, we use dictionary dispatch and behavioral methods that understand
    their own presentation logic.
    """
    
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"
    
    @classmethod
    def from_violation_count(cls, count: int) -> "ComplianceGrade":
        """Determine grade using boolean arithmetic - zero conditionals."""
        # Boolean range checks encode grade thresholds
        is_excellent = count == 0
        is_good = (count > 0) * (count <= 5)  # Between 1 and 5
        is_needs_improvement = (count > 5) * (count <= 15)  # Between 6 and 15
        # is_poor = count > 15 (implicit, when others are False)
        
        # Boolean arithmetic computes grade index
        # EXCELLENT = 3, GOOD = 2, NEEDS_IMPROVEMENT = 1, POOR = 0
        grade_index = (
            is_excellent * 3 +
            is_good * 2 +
            is_needs_improvement * 1
            # POOR = 0 (default when none of above)
        )
        
        # Pure list indexing - no conditionals
        grades = [cls.POOR, cls.NEEDS_IMPROVEMENT, cls.GOOD, cls.EXCELLENT]
        return grades[grade_index]
    
    def to_emoji(self) -> str:
        """Convert grade to emoji representation using dictionary dispatch."""
        emoji_map = {
            self.EXCELLENT: "✅",
            self.GOOD: "👍",
            self.NEEDS_IMPROVEMENT: "⚠️",
            self.POOR: "❌"
        }
        return emoji_map[self]
    
    def to_message(self) -> str:
        """Convert grade to descriptive message using dictionary dispatch."""
        message_map = {
            self.EXCELLENT: "🎉 PERFECT SDA COMPLIANCE DETECTED!",
            self.GOOD: "✨ Good SDA compliance with minor issues",
            self.NEEDS_IMPROVEMENT: "⚠️ Several SDA violations need attention",
            self.POOR: "❌ Significant SDA violations require refactoring"
        }
        return message_map[self]
    
    def to_letter_grade(self) -> str:
        """Convert to traditional letter grade using dictionary dispatch."""
        grade_map = {
            self.EXCELLENT: "A+",
            self.GOOD: "B",
            self.NEEDS_IMPROVEMENT: "C",
            self.POOR: "D"
        }
        return grade_map[self]
    
    def format_assessment(self) -> str:
        """Format compliance assessment with celebratory language using dictionary dispatch."""
        assessment_map = {
            self.EXCELLENT: "🏆 PERFECT COMPLIANCE - This module demonstrates mastery of SDA principles!",
            self.GOOD: "✨ Strong SDA compliance with minor opportunities for improvement",
            self.NEEDS_IMPROVEMENT: "⚠️ Several SDA violations detected - refactoring recommended",
            self.POOR: "❌ Significant architectural issues require immediate attention"
        }
        return assessment_map[self]


class CelebrationLevel(StrEnum):
    """Behavioral enum for determining celebration level of clean code.
    
    Pure SDA pattern: The enum knows how to present different levels of
    celebration without external conditionals.
    """
    
    EXCEPTIONAL = "exceptional"  # Zero violations with rich patterns
    CLEAN = "clean"  # Zero violations
    MIXED = "mixed"  # Has both patterns and violations
    PROBLEMATIC = "problematic"  # More violations than patterns
    
    @classmethod
    def from_metrics(cls, violations: int, patterns: int) -> "CelebrationLevel":
        """Determine celebration level using boolean arithmetic - zero conditionals."""
        # Boolean flags encode business rules
        is_zero_violations = violations == 0
        is_rich_patterns = patterns > 10
        is_more_patterns = patterns > violations
        
        # Boolean arithmetic computes classification score
        # EXCEPTIONAL = 3, CLEAN = 2, MIXED = 1, PROBLEMATIC = 0
        level_score = (
            is_zero_violations * is_rich_patterns * 3 +  # EXCEPTIONAL when zero violations AND rich patterns
            is_zero_violations * (not is_rich_patterns) * 2 +  # CLEAN when zero violations but not rich
            (not is_zero_violations) * is_more_patterns * 1  # MIXED when has violations but more patterns
            # PROBLEMATIC = 0 (default when none of above)
        )
        
        # Pure list indexing - no conditionals
        levels = [cls.PROBLEMATIC, cls.MIXED, cls.CLEAN, cls.EXCEPTIONAL]
        return levels[min(level_score, 3)]  # min() ensures valid index
    
    def format_header(self) -> str:
        """Format the report header based on celebration level."""
        header_map = {
            self.EXCEPTIONAL: "🧠 SDA ARCHITECTURE ANALYSIS - EXCELLENT ✅",
            self.CLEAN: "🧠 SDA ARCHITECTURE ANALYSIS - CLEAN ✨",
            self.MIXED: "🧠 SDA ARCHITECTURE ANALYSIS - MIXED",
            self.PROBLEMATIC: "🧠 SDA ARCHITECTURE ANALYSIS - NEEDS WORK ⚠️"
        }
        return header_map[self]


class ScanMetrics(BaseModel):
    """Rich domain model for scan metrics with computed intelligence.
    
    This model demonstrates how to compute architectural richness metrics
    without external calculation logic.
    """
    
    model_config = ConfigDict(frozen=True)
    
    files_scanned: int
    models_analyzed: int = 0
    frozen_models: int = 0
    behavioral_enums: int = 0
    computed_fields_count: int = 0
    protocol_boundaries: int = 0
    
    @computed_field
    @property
    def architectural_richness(self) -> float:
        """Compute architectural richness score from metrics."""
        # Weight different architectural patterns
        weights = {
            'frozen': self.frozen_models * 3,
            'behavioral': self.behavioral_enums * 4,
            'computed': self.computed_fields_count * 2,
            'protocols': self.protocol_boundaries * 5
        }
        
        total_score = sum(weights.values())
        max_possible = self.models_analyzed * 14  # Sum of all weights
        
        # Safe division with or-pattern
        safe_max = max_possible or 1
        return (total_score / safe_max) * 100
    
    @computed_field
    @property
    def excellence_summary(self) -> list[str]:
        """Generate excellence points for zero-violation modules."""
        points = []
        
        # Use multiplication to conditionally add items (zero becomes empty)
        points.extend([f"{self.frozen_models} frozen domain models with intelligence"] * bool(self.frozen_models))
        points.extend([f"{self.behavioral_enums} behavioral enums with methods"] * bool(self.behavioral_enums))
        points.extend([f"{self.computed_fields_count} computed fields for derived state"] * bool(self.computed_fields_count))
        points.extend([f"{self.protocol_boundaries} clean protocol boundaries maintained"] * bool(self.protocol_boundaries))
        
        return points or ["Clean module structure maintained"]
    
    def format_summary(self) -> str:
        """Format scan metrics summary with celebratory language."""
        summary_lines = [
            "📊 SCAN METRICS:",
            f"  Files Scanned: {self.files_scanned}",
            f"  Models Analyzed: {self.models_analyzed}",
            f"  SDA Patterns Found: {self.computed_fields_count + self.frozen_models + self.behavioral_enums}",
        ]
        
        # Add architectural richness score for exceptional modules
        richness = self.architectural_richness
        richness_display = f"  Architectural Richness: {richness:.1f}%" * bool(richness > 0)
        summary_lines.extend([richness_display] * bool(richness_display))
        
        return "\n".join(summary_lines)


class ArchitectureReport(BaseModel):
    """Comprehensive architecture analysis report - Self-Computing Intelligence.
    
    WHAT: Aggregates all analysis findings and computes statistics about the
    codebase's architectural patterns and violations.
    
    WHY: Instead of scattering report generation logic across services, the
    report itself knows how to classify findings, compute statistics, and
    present results. This keeps all reporting logic in one cohesive place.
    
    HOW: Uses factory methods for creation, computed fields for statistics,
    and type-safe collections for organizing findings by pattern type.
    
    Teaching Example:
        >>> # Create report from findings:
        >>> findings = [finding1, finding2, finding3]
        >>> report = ArchitectureReport.from_findings(
        >>>     findings, "my_module", ModuleType.DOMAIN, ["file1.py", "file2.py"]
        >>> )
        >>> 
        >>> # Report computes its own statistics:
        >>> print(f"Violations: {report.total_violations}")
        >>> print(f"Patterns: {report.total_patterns}")
        >>> print(f"Pattern ratio: {report.pattern_distribution['patterns']:.1%}")
        >>> 
        >>> # Access organized findings:
        >>> for pattern_type, findings in report.violations.items():
        >>>     print(f"{pattern_type}: {len(findings)} occurrences")
    
    SDA Patterns Demonstrated:
        1. **Factory Method Pattern**: from_findings() creates complex reports
        2. **Computed Aggregations**: Statistics calculated on demand
        3. **Type-Safe Collections**: Dict[PatternType, List[Finding]]
        4. **Self-Describing Data**: Report knows how to present itself
    
    Architecture Note:
        This eliminates the need for separate ReportGenerator, ReportCalculator,
        or ReportFormatter services. All intelligence lives in the model.
    """

    model_config = ConfigDict(frozen=True)

    # Teaching: Type-safe collections - no raw dicts or lists!
    violations: dict[PatternType, list[Finding]]  # Violations grouped by type
    patterns: dict[PositivePattern, list[Finding]]  # Positive patterns grouped by type
    module_type: ModuleType = Field(
        default=ModuleType.MIXED,
        description="Type of module analyzed",
        # Teaching: Even enums get descriptions for self-documentation
    )

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

        # Teaching: Pure discriminated union classification - no conditionals
        # defaultdict eliminates KeyError and setdefault() calls
        violations: dict[PatternType, list[Finding]] = defaultdict(list)
        patterns: dict[PositivePattern, list[Finding]] = defaultdict(list)

        for finding in findings:
            # Teaching: Truthy checks are OK for optional fields
            # This isn't a business conditional - it's null-safety
            if finding.pattern_category:  # Has violation?
                violations[finding.pattern_category].append(finding)
            
            if finding.pattern_type:  # Has positive pattern?
                patterns[finding.pattern_type].append(finding)
            
            # Teaching: A finding could have both or neither - that's OK!

        # Teaching: Convert defaultdict back to regular dict for immutability
        return cls(violations=dict(violations), patterns=dict(patterns), module_type=module_type)

    @computed_field
    @property
    def total_violations(self) -> int:
        """Total count of SDA violations found across all types.
        
        Teaching Note: AGGREGATION WITH GENERATOR EXPRESSIONS
        
        This pattern (sum + generator) is idiomatic Python for aggregation:
        - Memory efficient (generator doesn't create intermediate list)
        - Readable (expresses intent clearly)
        - Type safe (sum() always returns int for int inputs)
        
        Alternative approaches and why we don't use them:
        - reduce(): Less readable, needs import
        - Manual loop: More verbose, mutable counter
        - List comprehension: Wastes memory creating list
        """
        return sum(len(findings) for findings in self.violations.values())

    @computed_field
    @property
    def total_patterns(self) -> int:
        """Total count of positive SDA patterns found across all types."""
        return sum(len(findings) for findings in self.patterns.values())

    @computed_field
    @property
    def files_analyzed(self) -> int:
        """Count of unique files analyzed - pure observation.
        
        Teaching Note: SET OPERATIONS FOR UNIQUENESS
        
        This shows how to collect unique values without conditionals:
        1. Create empty set (automatically deduplicates)
        2. Update with generator expressions
        3. Return length
        
        The set.update() method is perfect for adding multiple items
        and automatically handles duplicates. This is more efficient
        than repeated set.add() calls.
        
        Pattern: Use sets when you need unique values!
        """
        all_files: set[str] = set()
        # Teaching: Iterate over all findings collections
        for findings in self.violations.values():
            all_files.update(f.file_path for f in findings)
        for findings in self.patterns.values():
            all_files.update(f.file_path for f in findings)
        return len(all_files)

    @computed_field
    @property
    def pattern_distribution(self) -> dict[str, float]:
        """Observable distribution of patterns vs violations using pure type system.

        Teaching Note: SAFE DIVISION WITHOUT TRY/EXCEPT
        
        This method shows three techniques for safe math without conditionals:
        
        1. **Or-operator for defaults**: `total or 1` returns 1 if total is 0
        2. **Boolean multiplication**: `* bool(total)` returns 0 if total is 0
        3. **Type coercion**: bool(0) = False = 0 in multiplication
        
        Traditional approach:
            if total == 0:
                return {"patterns": 0.0, "violations": 0.0}
            return {
                "patterns": self.total_patterns / total,
                "violations": self.total_violations / total
            }
        
        SDA approach uses mathematical properties to avoid conditionals:
        - When total=0: safe_total=1, bool(total)=False=0, result=0
        - When total>0: safe_total=total, bool(total)=True=1, result=percentage
        
        This is "math as logic" - using mathematical properties to encode
        business rules without explicit conditionals.
        """
        total = self.total_patterns + self.total_violations

        # Teaching: Boolean coercion eliminates conditionals
        safe_total = total or 1  # Prevents ZeroDivisionError

        # Teaching: Pure calculation with boolean multiplication for safety
        return {
            "patterns": (self.total_patterns / safe_total) * bool(total),
            "violations": (self.total_violations / safe_total) * bool(total),
        }
    
    @computed_field
    @property
    def celebration_level(self) -> CelebrationLevel:
        """Compute celebration level from violation and pattern counts."""
        return CelebrationLevel.from_metrics(self.total_violations, self.total_patterns)
    
    @computed_field
    @property
    def compliance_grade(self) -> ComplianceGrade:
        """Compute compliance grade from violation count."""
        return ComplianceGrade.from_violation_count(self.total_violations)
    
    @computed_field
    @property
    def scan_metrics(self) -> ScanMetrics:
        """Compute scan metrics from analyzed data."""
        # Count specific pattern types
        computed_count = sum(len(findings) for pattern, findings in self.patterns.items() 
                            if pattern == PositivePattern.COMPUTED_FIELDS)
        
        return ScanMetrics(
            files_scanned=self.files_analyzed,
            models_analyzed=len(self.violations) + len(self.patterns),  # Approximation
            frozen_models=0,  # Would need deeper analysis
            behavioral_enums=0,  # Would need deeper analysis
            computed_fields_count=computed_count,
            protocol_boundaries=0  # Would need deeper analysis
        )
    
    @computed_field
    @property
    def celebration_header(self) -> str:
        """Generate celebratory header based on celebration level - pure delegation."""
        return self.celebration_level.format_header()
    
    @computed_field
    @property
    def scan_summary(self) -> str:
        """Generate scan metrics summary - pure delegation."""
        return self.scan_metrics.format_summary()
    
    @computed_field
    @property
    def compliance_assessment(self) -> str:
        """Generate compliance assessment message - pure delegation."""
        return self.compliance_grade.format_assessment()
