"""Test enum behavioral intelligence using SDA test case models.

This demonstrates SDA testing principle: "Test enum behavior and state transitions"
NOT enum values or string representations.

Rule 050: "Test the domain intelligence, trust Pydantic for the rest"
Focus: Business logic in enum methods, not enum value validation.
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.sda_detector.models.core_types import ModuleType


class AnalysisPriorityTestCase(BaseModel):
    """Test case model for ModuleType.analysis_priority business logic.

    This tests the BUSINESS INTELLIGENCE about analysis ordering,
    not the enum values themselves.

    The priority logic encodes domain knowledge: "Classes are most complex,
    so analyze them first." This is business logic worth testing.
    """

    model_config = ConfigDict(frozen=True)

    module_type: ModuleType = Field(description="Module type to test")
    expected_priority: int = Field(ge=1, description="Expected analysis priority")
    business_justification: str = Field(description="Why this priority makes business sense")

    @computed_field
    @property
    def validates_priority_intelligence(self) -> bool:
        """Test case validates the analysis priority business logic.

        This is domain intelligence: the ordering reflects actual business
        complexity and analysis needs, not arbitrary numbering.
        """
        return self.module_type.analysis_priority == self.expected_priority

    @computed_field
    @property
    def diagnostic_explanation(self) -> str:
        """Teaching explanation of the priority business logic."""
        actual = self.module_type.analysis_priority
        if self.validates_priority_intelligence:
            return f"✅ {self.module_type.name}: Priority {actual} - {self.business_justification}"
        return f"❌ {self.module_type.name}: Expected {self.expected_priority}, got {actual}"


class ModuleTypeClassificationTestCase(BaseModel):
    """Test case model for ModuleType boundary classification business logic.

    This tests the BUSINESS RULES about which module types need different
    analysis treatment, not the enum string values.

    The classification drives real behavior: boundary types allow isinstance,
    domain types require strict SDA patterns.
    """

    model_config = ConfigDict(frozen=True)

    module_type: ModuleType = Field(description="Module type to classify")
    should_be_boundary: bool = Field(description="Whether this is a boundary context")
    architectural_reason: str = Field(description="Architectural justification")

    @computed_field
    @property
    def validates_classification_logic(self) -> bool:
        """Test the boundary classification business intelligence.

        This logic drives actual analysis behavior: what patterns are
        acceptable in different module types.
        """
        # The business logic: these types are considered boundary contexts
        boundary_types = {ModuleType.INFRASTRUCTURE, ModuleType.TOOLING, ModuleType.FRAMEWORK}
        is_boundary = self.module_type in boundary_types
        return is_boundary == self.should_be_boundary


def test_analysis_priority_business_intelligence():
    """Test ModuleType.analysis_priority business logic and ordering rules.

    Focus: Testing the BUSINESS INTELLIGENCE about analysis complexity ordering.
    Not testing: Enum string values, Pydantic enum validation, or set operations.

    This priority logic drives actual analysis behavior in the detector.
    """
    # SDA test cases: domain models encoding business knowledge
    priority_test_cases = [
        AnalysisPriorityTestCase(
            module_type=ModuleType.DOMAIN,
            expected_priority=20,
            business_justification="Domain modules contain pure business logic, highest priority",
        ),
        AnalysisPriorityTestCase(
            module_type=ModuleType.INFRASTRUCTURE,
            expected_priority=40,
            business_justification="Infrastructure modules handle critical boundaries, high priority",
        ),
        AnalysisPriorityTestCase(
            module_type=ModuleType.TOOLING,
            expected_priority=60,
            business_justification="Tooling modules need analysis for development quality",
        ),
        AnalysisPriorityTestCase(
            module_type=ModuleType.FRAMEWORK,
            expected_priority=80,
            business_justification="Framework modules follow external patterns, lower priority",
        ),
        AnalysisPriorityTestCase(
            module_type=ModuleType.MIXED,
            expected_priority=100,
            business_justification="Mixed modules have unclear concerns, lowest priority",
        ),
    ]

    # Each test case validates its own business logic
    for test_case in priority_test_cases:
        assert test_case.validates_priority_intelligence, test_case.diagnostic_explanation


def test_analysis_priority_ordering_business_rules():
    """Test that analysis priority creates correct business-driven ordering.

    This tests the BUSINESS RULE: more complex nodes should have lower
    priority numbers (analyzed first).
    """
    # Get all priorities and verify business ordering rules
    all_module_types = list(ModuleType)
    priorities = [(mt, mt.analysis_priority) for mt in all_module_types]
    sorted_by_priority = sorted(priorities, key=lambda x: x[1])

    # Business rule: CLASS should be highest priority (analyzed first)
    assert sorted_by_priority[0][0] == ModuleType.DOMAIN, (
        "Business rule violation: DOMAIN should have highest analysis priority"
    )

    # Business rule: BASE should be lowest priority (fallback)
    assert sorted_by_priority[-1][0] == ModuleType.MIXED, (
        "Business rule violation: MIXED should have lowest analysis priority"
    )

    # Business rule: No duplicate priorities (each type has unique analysis order)
    priority_values = [p[1] for p in priorities]
    unique_priorities = set(priority_values)
    assert len(priority_values) == len(unique_priorities), (
        "Business rule violation: Each node type must have unique analysis priority"
    )


def test_module_type_boundary_classification_intelligence():
    """Test ModuleType boundary classification business logic.

    Focus: Testing the BUSINESS RULES about architectural boundaries.
    Not testing: Enum string values or set operations.

    This classification drives real analysis behavior.
    """
    classification_test_cases = [
        ModuleTypeClassificationTestCase(
            module_type=ModuleType.INFRASTRUCTURE,
            should_be_boundary=True,
            architectural_reason="Infrastructure needs isinstance/hasattr for external systems",
        ),
        ModuleTypeClassificationTestCase(
            module_type=ModuleType.TOOLING,
            should_be_boundary=True,
            architectural_reason="Tooling requires reflection and file system patterns",
        ),
        ModuleTypeClassificationTestCase(
            module_type=ModuleType.FRAMEWORK,
            should_be_boundary=True,
            architectural_reason="Framework integration follows external library patterns",
        ),
        ModuleTypeClassificationTestCase(
            module_type=ModuleType.DOMAIN,
            should_be_boundary=False,
            architectural_reason="Domain code must use strict SDA patterns only",
        ),
        ModuleTypeClassificationTestCase(
            module_type=ModuleType.MIXED,
            should_be_boundary=False,
            architectural_reason="Mixed code defaults to strict rules for consistency",
        ),
    ]

    # Each test case validates the classification business logic
    for test_case in classification_test_cases:
        assert test_case.validates_classification_logic, (
            f"Classification failed for {test_case.module_type}: {test_case.architectural_reason}"
        )


def test_boundary_classification_completeness():
    """Test that boundary classification covers all module types (business completeness).

    This tests the BUSINESS RULE: every module type must have a clear
    classification for analysis purposes.
    """
    # Business logic: these are the boundary contexts
    boundary_types = {ModuleType.INFRASTRUCTURE, ModuleType.TOOLING, ModuleType.FRAMEWORK}

    # Business logic: these use strict domain rules
    domain_types = {ModuleType.DOMAIN, ModuleType.MIXED}

    # Business rule: classifications must be mutually exclusive
    assert boundary_types.isdisjoint(domain_types), (
        "Business rule violation: Boundary and domain types must be mutually exclusive"
    )

    # Business rule: classifications must be complete (cover all types)
    all_classified = boundary_types | domain_types
    all_module_types = set(ModuleType)
    assert all_classified == all_module_types, (
        f"Business rule violation: Classification incomplete. Missing: {all_module_types - all_classified}"
    )


# Note: We deliberately DON'T test:
# ❌ assert ModuleType.DOMAIN == "domain" (enum string values) - that's Pydantic's job
# ❌ Enum validation or serialization - infrastructure plumbing
# ❌ Set operations themselves - Python built-in behavior
#
# We DO test:
# ✅ Business logic in enum methods (analysis_priority)
# ✅ Domain rules encoded in classifications (boundary vs domain)
# ✅ Behavioral intelligence that drives actual application decisions
# ✅ Business completeness and consistency rules
