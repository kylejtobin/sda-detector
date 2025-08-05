"""SDA test case models - demonstrating test cases as self-validating domain models.

This module shows how to implement SDA testing philosophy:
"Test cases as domain models that validate themselves"

Instead of external test functions with assertions, we create test case models
that contain the intelligence to validate business logic.

Rule 050: "Dogfood SDA principles in test design"
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from sda_detector.models import ArchitectureReport, PositivePattern, ViolationType


class FixtureAnalysisTestCase(BaseModel):
    """Test case model for analyzing code fixtures with expected patterns.

    This demonstrates SDA testing: the test case is a domain model that
    knows what patterns it should find and can validate the results.

    This replaces procedural integration tests with domain intelligence.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Human-readable test case name")
    fixture_path: str = Field(description="Path to code fixture")
    expected_violations: list[ViolationType] = Field(description="Violations that should be found")
    expected_patterns: list[PositivePattern] = Field(description="Patterns that should be found")
    min_violation_count: int = Field(ge=0, default=1, description="Minimum violations expected")
    min_pattern_count: int = Field(ge=0, default=0, description="Minimum patterns expected")

    @computed_field
    @property
    def validates_against_report(self) -> bool:
        """Test case validates itself against an analysis report.

        This is pure SDA: the test case contains the business intelligence
        to determine if the analysis results match expectations.

        Note: This is a computed field that would be called with a report parameter
        in actual usage. For demonstration, we show the validation logic.
        """
        # In practice, this would take a report parameter:
        # def validates_against_report(self, report: ArchitectureReport) -> bool:
        return True  # Placeholder - shows the pattern

    def verify_analysis_results(self, report: ArchitectureReport) -> bool:
        """Validate analysis results against expected patterns and violations.

        This method demonstrates how test cases can contain sophisticated
        validation logic while remaining domain-focused.
        """
        # Check that expected violations were found
        for violation_type in self.expected_violations:
            violations_found = report.violations.get(violation_type, [])
            if len(violations_found) < self.min_violation_count:
                return False

        # Check that expected patterns were found
        for pattern_type in self.expected_patterns:
            patterns_found = report.patterns.get(pattern_type, [])
            if len(patterns_found) < self.min_pattern_count:
                return False

        return True

    @computed_field
    @property
    def diagnostic_description(self) -> str:
        """Provide human-readable description of what this test case validates."""
        violation_names = [v.replace("_", " ").title() for v in self.expected_violations]
        pattern_names = [p.replace("_", " ").title() for p in self.expected_patterns]

        parts = []
        if violation_names:
            parts.append(f"Violations: {', '.join(violation_names)}")
        if pattern_names:
            parts.append(f"Patterns: {', '.join(pattern_names)}")

        return f"{self.name} - {' | '.join(parts)}"


class ViolationRatioTestCase(BaseModel):
    """Test case model for validating violation vs pattern ratios in code samples.

    This demonstrates testing architectural quality metrics using domain models
    instead of procedural calculations.
    """

    model_config = ConfigDict(frozen=True)

    fixture_type: str = Field(description="Type of fixture (violations/patterns/mixed)")
    min_violation_ratio: float = Field(ge=0.0, le=1.0, description="Minimum expected violation ratio")
    max_violation_ratio: float = Field(ge=0.0, le=1.0, description="Maximum expected violation ratio")
    quality_expectation: str = Field(description="What this ratio tells us about code quality")

    def validates_quality_metrics(self, report: ArchitectureReport) -> bool:
        """Validate that code quality metrics match expectations.

        This encapsulates the business logic about what constitutes
        good vs problematic violation ratios.
        """
        total_violations = sum(len(findings) for findings in report.violations.values())
        total_patterns = sum(len(findings) for findings in report.patterns.values())
        total_findings = total_violations + total_patterns

        if total_findings == 0:
            return True  # No findings to validate

        violation_ratio = total_violations / total_findings
        return self.min_violation_ratio <= violation_ratio <= self.max_violation_ratio

    @computed_field
    @property
    def explains_quality_expectations(self) -> str:
        """Teaching explanation of what different ratios mean."""
        return (
            f"{self.fixture_type.title()} fixtures should have "
            f"{self.min_violation_ratio:.0%}-{self.max_violation_ratio:.0%} violations. "
            f"Reasoning: {self.quality_expectation}"
        )


class PatternDetectionTestCase(BaseModel):
    """Test case model for validating specific pattern detection accuracy.

    This shows how to test pattern recognition using domain intelligence
    rather than procedural file scanning.
    """

    model_config = ConfigDict(frozen=True)

    pattern_type: PositivePattern = Field(description="Type of pattern to detect")
    expected_file_patterns: list[str] = Field(description="File name patterns where this should be found")
    business_significance: str = Field(description="Why finding this pattern matters")

    def validates_pattern_detection(self, report: ArchitectureReport) -> bool:
        """Test that patterns are detected in expected locations.

        This contains the business logic about where certain patterns
        should appear in well-structured code.
        """
        patterns_found = report.patterns.get(self.pattern_type, [])

        if not patterns_found:
            return False

        # Check that patterns appear in expected file types
        found_files = {finding.file_path for finding in patterns_found}

        for expected_pattern in self.expected_file_patterns:
            if any(expected_pattern in file_path for file_path in found_files):
                return True

        return False

    @computed_field
    @property
    def detection_expectations(self) -> str:
        """Explain what successful detection means for code quality."""
        file_list = ", ".join(self.expected_file_patterns)
        return (
            f"{self.pattern_type.replace('_', ' ').title()} should appear in files like: {file_list}. "
            f"Business value: {self.business_significance}"
        )


# Example usage demonstrating SDA test case patterns:

VIOLATION_FIXTURE_TESTS = [
    FixtureAnalysisTestCase(
        name="isinstance Heavy Violations",
        fixture_path="tests/fixtures/violations/isinstance_heavy.py",
        expected_violations=[ViolationType.ISINSTANCE_VIOLATIONS, ViolationType.BUSINESS_CONDITIONALS],
        expected_patterns=[],
        min_violation_count=5,  # Expect substantial isinstance usage
    ),
    FixtureAnalysisTestCase(
        name="Manual JSON Serialization",
        fixture_path="tests/fixtures/violations/manual_json.py",
        expected_violations=[ViolationType.MANUAL_JSON_SERIALIZATION],
        expected_patterns=[],
        min_violation_count=3,  # Multiple json.dumps/loads calls
    ),
]

PATTERN_FIXTURE_TESTS = [
    FixtureAnalysisTestCase(
        name="Rich Domain Models",
        fixture_path="tests/fixtures/patterns/rich_domain.py",
        expected_violations=[],
        expected_patterns=[PositivePattern.PYDANTIC_MODELS, PositivePattern.COMPUTED_FIELDS],
        min_pattern_count=2,  # Multiple domain patterns
    )
]

QUALITY_RATIO_TESTS = [
    ViolationRatioTestCase(
        fixture_type="violations",
        min_violation_ratio=0.6,
        max_violation_ratio=1.0,
        quality_expectation="Anti-pattern examples should be predominantly violations",
    ),
    ViolationRatioTestCase(
        fixture_type="patterns",
        min_violation_ratio=0.0,
        max_violation_ratio=0.2,
        quality_expectation="Good SDA examples should be predominantly positive patterns",
    ),
    ViolationRatioTestCase(
        fixture_type="mixed",
        min_violation_ratio=0.3,
        max_violation_ratio=0.7,
        quality_expectation="Real-world code has mix of boundary violations and domain patterns",
    ),
]
