"""Test AnalysisContext domain intelligence using SDA test case models.

This demonstrates proper SDA testing: test cases as self-validating domain models
that focus on BUSINESS INTELLIGENCE, not Pydantic plumbing.

Rule 050: "Test the domain intelligence, trust Pydantic for the rest"
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.sda_detector.models.context_domain import RichAnalysisContext
from src.sda_detector.models.core_types import ModuleType


class BoundaryContextTestCase(BaseModel):
    """Test case model for AnalysisContext.is_boundary_context business logic.

    This embodies SDA testing philosophy: the test case is a domain model
    that contains the intelligence to validate itself against the business rules.

    We're testing the BUSINESS DECISION about what constitutes boundary code,
    not testing Pydantic's computed field mechanism.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Human-readable test case description")
    module_type: ModuleType = Field(description="Module type to test")
    should_be_boundary: bool = Field(description="Expected boundary context result")
    business_rationale: str = Field(description="Why this should/shouldn't be boundary")

    @computed_field
    @property
    def validates_business_logic(self) -> bool:
        """Test case validates the boundary detection business intelligence.

        This is pure SDA: the test case knows the business rules and
        validates them against the actual domain model behavior.

        Focus: Testing the DECISION LOGIC in is_boundary_context computed field.
        """
        # Create context with our test module type
        context = RichAnalysisContext(current_file=f"test_{self.module_type.value}.py", module_type=self.module_type)

        # Test the actual business intelligence (computed field logic)
        actual_result = context.in_boundary_context
        return actual_result == self.should_be_boundary

    @computed_field
    @property
    def diagnostic_message(self) -> str:
        """Provide teaching information about boundary context business rules."""
        if self.validates_business_logic:
            return f"✅ {self.name}: {self.business_rationale}"

        context = RichAnalysisContext(current_file="test.py", module_type=self.module_type)
        actual = context.in_boundary_context
        return (
            f"❌ {self.name}: Expected {self.should_be_boundary}, got {actual}. "
            f"Business rule: {self.business_rationale}"
        )


class TypeCheckingDetectionTestCase(BaseModel):
    """Test case model for AnalysisContext.is_type_checking_context intelligence.

    This tests the PATTERN RECOGNITION logic in the computed field,
    not the string matching implementation details.
    """

    model_config = ConfigDict(frozen=True)

    scenario: str = Field(description="What scenario we're testing")
    current_file: str = Field(description="File name/path to analyze")
    should_detect_type_checking: bool = Field(description="Expected detection result")

    @computed_field
    @property
    def validates_pattern_recognition(self) -> bool:
        """Test the TYPE_CHECKING pattern recognition business logic."""
        context = RichAnalysisContext(current_file=self.current_file, module_type=ModuleType.MIXED)
        return context.in_type_checking_context == self.should_detect_type_checking


def test_boundary_context_business_intelligence():
    """Test AnalysisContext.is_boundary_context computed field business logic.

    Focus: Testing the BUSINESS RULES about what constitutes boundary code.
    Not testing: Pydantic computed field mechanism or set membership operations.

    This embodies Rule 050: "Test where actual business intelligence lives"
    """
    # SDA test cases: domain models that validate business logic
    boundary_test_cases = [
        BoundaryContextTestCase(
            name="Infrastructure modules are boundary contexts",
            module_type=ModuleType.INFRASTRUCTURE,
            should_be_boundary=True,
            business_rationale="Infrastructure handles external systems, needs isinstance/hasattr",
        ),
        BoundaryContextTestCase(
            name="Tooling modules are NOT boundary contexts",
            module_type=ModuleType.TOOLING,
            should_be_boundary=False,
            business_rationale="Tooling uses standard patterns, not boundary-specific ones",
        ),
        BoundaryContextTestCase(
            name="Framework modules are boundary contexts",
            module_type=ModuleType.FRAMEWORK,
            should_be_boundary=True,
            business_rationale="Framework integration requires external library patterns",
        ),
        BoundaryContextTestCase(
            name="Domain modules are NOT boundary contexts",
            module_type=ModuleType.DOMAIN,
            should_be_boundary=False,
            business_rationale="Pure domain logic should use strict SDA patterns only",
        ),
        BoundaryContextTestCase(
            name="Mixed modules are NOT boundary contexts",
            module_type=ModuleType.MIXED,
            should_be_boundary=False,
            business_rationale="Mixed code defaults to strict rules for domain portions",
        ),
    ]

    # Each test case validates its own business logic - pure SDA!
    for test_case in boundary_test_cases:
        assert test_case.validates_business_logic, test_case.diagnostic_message


def test_type_checking_pattern_recognition():
    """Test AnalysisContext.is_type_checking_context pattern detection logic.

    Focus: Testing the PATTERN RECOGNITION intelligence, not string operations.
    """
    type_checking_cases = [
        TypeCheckingDetectionTestCase(
            scenario="No TYPE_CHECKING scope active",
            current_file="models.py",
            should_detect_type_checking=False,
        ),
        TypeCheckingDetectionTestCase(
            scenario="Normal file without TYPE_CHECKING scope",
            current_file="domain.py",
            should_detect_type_checking=False,
        ),
        TypeCheckingDetectionTestCase(
            scenario="File without TYPE_CHECKING scope",
            current_file="business_logic.py",
            should_detect_type_checking=False,  # RichAnalysisContext looks at scope stack, not filename
        ),
    ]

    # SDA pattern: test cases validate themselves
    for case in type_checking_cases:
        assert case.validates_pattern_recognition, (
            f"Pattern recognition failed for {case.scenario}: "
            f"file='{case.current_file}', expected={case.should_detect_type_checking}"
        )


# Note: We deliberately DON'T test:
# ❌ context.current_file = "changed.py" (immutability) - that's Pydantic's job
# ❌ Field validation or defaults - trust Pydantic
# ❌ Serialization/deserialization - infrastructure plumbing
#
# We DO test:
# ✅ Business logic in computed fields (is_boundary_context, is_type_checking_context)
# ✅ Domain decisions encoded in the type system
# ✅ Behavioral intelligence that drives actual application logic
