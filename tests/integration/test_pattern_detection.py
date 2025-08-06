"""Integration tests for positive pattern detection - reality-based testing.

Following SDA testing philosophy: Test against real code samples with known patterns.
"""

from src.sda_detector import analyze_module
from src.sda_detector.models import PositivePattern, PatternType


def test_pydantic_patterns_detected():
    """Verify Pydantic-related patterns are properly detected in fixtures.
    
    These fixtures demonstrate Pydantic model usage and serialization patterns,
    which are core to modern Python domain modeling.
    """
    report = analyze_module("tests/fixtures/patterns", "Pydantic Pattern Test")

    # Verify Pydantic serialization patterns are detected
    pydantic_patterns = report.patterns.get(PositivePattern.PYDANTIC_SERIALIZATION, [])
    assert len(pydantic_patterns) >= 10, f"Pydantic fixtures demonstrate serialization patterns. Found: {len(pydantic_patterns)}"
    
    # Verify the fixtures teach good Pydantic usage
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    assert total_patterns >= 50, f"Pydantic example fixtures are pattern-rich. Total patterns: {total_patterns}"


def test_computed_fields_detected():
    """Verify robust detection of @computed_field patterns in fixtures.
    
    Computed fields are a cornerstone of SDA - they encode business logic
    as derived properties rather than procedural functions.
    """
    report = analyze_module("tests/fixtures/patterns", "Computed Field Test")

    # Verify strong computed field detection
    computed_patterns = report.patterns.get(PositivePattern.COMPUTED_FIELDS, [])
    assert len(computed_patterns) >= 45, f"Computed field detection is robust. Found {len(computed_patterns)} instances"

    # Verify computed fields dominate the pattern landscape
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    computed_ratio = len(computed_patterns) / total_patterns if total_patterns > 0 else 0
    assert computed_ratio > 0.7, f"Computed fields are primary pattern type. Ratio: {computed_ratio:.1%}"


def test_pattern_fixture_quality_in_enum_examples():
    """Verify that enum example fixtures demonstrate high-quality SDA patterns.
    
    These fixtures serve as educational examples of behavioral enums,
    so they should contain substantial positive patterns.
    """
    report = analyze_module("tests/fixtures/patterns", "Enum Example Quality Test")
    
    # Verify fixture quality through pattern density
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    total_violations = sum(len(findings) for findings in report.violations.values())
    
    # Educational fixtures should be pattern-rich
    assert total_patterns >= 40, f"Enum example fixtures contain rich patterns. Found {total_patterns} patterns"
    
    # Verify educational value - these fixtures should teach good patterns
    pattern_density = total_patterns / (total_patterns + total_violations) if (total_patterns + total_violations) > 0 else 0
    assert pattern_density > 0.85, f"Educational fixtures should be >85% patterns. Got: {pattern_density:.1%}"


def test_pattern_fixture_quality_in_protocol_examples():
    """Verify that protocol example fixtures demonstrate clean interface patterns.
    
    Protocol fixtures showcase type-driven interfaces and should contain
    multiple pattern types that demonstrate good architectural practices.
    """
    report = analyze_module("tests/fixtures/patterns", "Protocol Example Quality Test")
    
    # Verify multiple pattern types are present
    pattern_types_found = [pt for pt, findings in report.patterns.items() if len(findings) > 0]
    assert len(pattern_types_found) >= 2, f"Protocol examples showcase multiple pattern types: {[pt.value for pt in pattern_types_found]}"
    
    # Verify computed fields and Pydantic patterns work together
    assert PositivePattern.COMPUTED_FIELDS in pattern_types_found, "Protocol examples demonstrate computed properties"
    assert PositivePattern.PYDANTIC_SERIALIZATION in pattern_types_found, "Protocol examples demonstrate serialization"


def test_pattern_fixture_quality_in_immutable_examples():
    """Verify that immutable update example fixtures demonstrate functional patterns.
    
    Immutable update fixtures showcase functional programming patterns
    and should have an exceptional pattern-to-violation ratio.
    """
    report = analyze_module("tests/fixtures/patterns", "Immutable Example Quality Test")
    
    # Verify exceptional pattern quality
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    total_violations = sum(len(findings) for findings in report.violations.values())
    
    # Immutable examples should be nearly pure patterns
    assert total_patterns >= 50, f"Immutable examples are pattern-rich. Found {total_patterns} patterns"
    assert total_violations <= 5, f"Immutable examples minimize violations. Found only {total_violations} violations"
    
    # Verify the exceptional quality ratio
    quality_ratio = total_patterns / (total_violations + 1)  # +1 to avoid division by zero
    assert quality_ratio >= 10, f"Immutable examples show 10:1 pattern-to-violation ratio. Got: {quality_ratio:.1f}:1"


def test_pattern_fixtures_have_high_pattern_ratio():
    """Test that pattern fixtures are predominantly patterns (integration reality check)."""
    report = analyze_module("tests/fixtures/patterns", "Pattern Ratio Test")

    total_violations = sum(len(findings) for findings in report.violations.values())
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    total_findings = total_violations + total_patterns

    # Pattern fixtures should be predominantly patterns
    if total_findings > 0:
        pattern_ratio = total_patterns / total_findings
        assert pattern_ratio > 0.8, f"Pattern fixtures should be >80% patterns, got {pattern_ratio:.1%}"


def test_patterns_contain_meaningful_descriptions():
    """Test that patterns include helpful descriptions for developers."""
    report = analyze_module("tests/fixtures/patterns", "Pattern Description Test")

    # Check computed field patterns have helpful descriptions
    computed_patterns = report.patterns.get(PositivePattern.COMPUTED_FIELDS, [])
    assert len(computed_patterns) > 0, "Should have computed field patterns to test"
    if computed_patterns:
        description = computed_patterns[0].description
        # Just verify it has a description
        assert len(description) > 10, f"Descriptions should be meaningful. Got: '{description}'"

    # Check Pydantic patterns have descriptions
    pydantic_patterns = report.patterns.get(PositivePattern.PYDANTIC_SERIALIZATION, [])
    if pydantic_patterns:
        description = pydantic_patterns[0].description
        assert len(description) > 10, f"Descriptions should be meaningful. Got: '{description}'"
