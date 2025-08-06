"""Test Finding domain intelligence using SDA test case models.

This demonstrates SDA testing philosophy: "Test cases as domain models that validate themselves"

We dogfood our own principles by creating test cases as Pydantic models with
@computed_field validation logic, rather than traditional procedural tests.
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.sda_detector.models.analysis_domain import Finding


class FindingLocationTestCase(BaseModel):
    """Test case model that knows how to validate Finding.location computed field.

    This demonstrates SDA testing: instead of external test functions,
    the test case itself is a domain model with validation intelligence.

    Rule 050: "Test cases as domain models that validate themselves"
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Descriptive name for this test case")
    file_path: str = Field(description="File path to test")
    line_number: int = Field(ge=0, description="Line number to test")
    expected_location: str = Field(description="Expected formatted location string")

    @computed_field
    @property
    def is_valid_test_case(self) -> bool:
        """Test case validates itself - pure SDA pattern.

        This is domain intelligence: the test case knows whether it passes.
        No external test runner logic needed - the data drives the behavior.
        """
        # Create the Finding using our test data
        finding = Finding(file_path=self.file_path, line_number=self.line_number, description="test case validation")

        # Test the actual domain intelligence (computed field)
        return finding.location == self.expected_location

    @computed_field
    @property
    def failure_reason(self) -> str:
        """Diagnostic information when test case fails - teaching intelligence."""
        if self.is_valid_test_case:
            return "Test case passed"

        # Provide detailed failure analysis
        finding = Finding(self.file_path, self.line_number, "diagnostic")
        actual = finding.location
        return f"Expected '{self.expected_location}', got '{actual}'"


def test_finding_location_computed_field_intelligence():
    """Test Finding.location computed field using SDA test case models.

    This follows Rule 050: "Test the domain intelligence, trust Pydantic for the rest"
    We test the BUSINESS LOGIC in the computed field, not Pydantic's plumbing.
    """
    # SDA test cases as domain models - they validate themselves!
    test_cases = [
        FindingLocationTestCase(
            name="Standard file path formatting",
            file_path="src/models/user.py",
            line_number=42,
            expected_location="src/models/user.py:42",
        ),
        FindingLocationTestCase(
            name="Root level file", file_path="main.py", line_number=1, expected_location="main.py:1"
        ),
        FindingLocationTestCase(
            name="Deep nested path",
            file_path="src/domain/models/complex/business_logic.py",
            line_number=999,
            expected_location="src/domain/models/complex/business_logic.py:999",
        ),
        FindingLocationTestCase(
            name="Edge case - line zero", file_path="test.py", line_number=0, expected_location="test.py:0"
        ),
    ]

    # Each test case validates itself - no external assertion logic!
    for test_case in test_cases:
        assert test_case.is_valid_test_case, f"Test case '{test_case.name}' failed: {test_case.failure_reason}"


def test_finding_location_business_logic_edge_cases():
    """Test edge cases in Finding.location business logic.

    Focus: Testing the DOMAIN INTELLIGENCE in the computed field formatting.
    Not testing: Pydantic validation, field constraints, or serialization.
    """
    edge_cases = [
        FindingLocationTestCase(
            name="Very long file path",
            file_path="a" * 200 + ".py",  # 203 characters
            line_number=1,
            expected_location="a" * 200 + ".py:1",
        ),
        FindingLocationTestCase(
            name="File with no extension", file_path="Makefile", line_number=5, expected_location="Makefile:5"
        ),
        FindingLocationTestCase(
            name="Large line number",
            file_path="big_file.py",
            line_number=999999,
            expected_location="big_file.py:999999",
        ),
    ]

    # SDA pattern: test cases know how to validate themselves
    for case in edge_cases:
        assert case.is_valid_test_case, case.failure_reason


# Note: We DON'T test immutability here because:
# Rule 050: "DON'T Test: State management (trust immutability)"
# That's Pydantic's responsibility, not our domain intelligence!
