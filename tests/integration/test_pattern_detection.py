"""Integration tests for positive pattern detection - reality-based testing.

Following SDA testing philosophy: Test against real code samples with known patterns.
"""

import sda_detector
from sda_detector.models import PositivePattern


def test_pydantic_patterns_detected():
    """Test detector finds Pydantic models in pattern fixtures."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Pattern Detection Test")

    # Should find Pydantic models
    pydantic_patterns = report.patterns[PositivePattern.PYDANTIC_MODELS]
    assert len(pydantic_patterns) > 0, "Should detect Pydantic models in pattern fixtures"

    # Verify we found the known patterns
    pattern_files = {p.file_path for p in pydantic_patterns}
    assert any("rich_domain.py" in path for path in pattern_files)


def test_computed_fields_detected():
    """Test detector finds @computed_field usage in pattern fixtures."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Computed Field Test")

    # Should find computed fields
    computed_patterns = report.patterns[PositivePattern.COMPUTED_FIELDS]
    assert len(computed_patterns) > 0, "Should detect computed fields in pattern fixtures"

    # Verify specific patterns
    computed_files = {p.file_path for p in computed_patterns}
    assert any("rich_domain.py" in path for path in computed_files)


def test_behavioral_enums_detected():
    """Test detector finds StrEnum with methods in pattern fixtures."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Behavioral Enum Test")

    # Should find behavioral enums
    enum_patterns = report.patterns[PositivePattern.BEHAVIORAL_ENUMS]
    assert len(enum_patterns) > 0, "Should detect behavioral enums in pattern fixtures"

    # Verify specific patterns
    enum_files = {p.file_path for p in enum_patterns}
    assert any("type_dispatch.py" in path or "rich_domain.py" in path for path in enum_files)


def test_protocols_detected():
    """Test detector finds Protocol definitions in pattern fixtures."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Protocol Test")

    # Should find protocols
    protocol_patterns = report.patterns[PositivePattern.PROTOCOLS]
    assert len(protocol_patterns) > 0, "Should detect protocols in pattern fixtures"

    # Verify specific patterns
    protocol_files = {p.file_path for p in protocol_patterns}
    assert any("protocols.py" in path for path in protocol_files)


def test_immutable_updates_detected():
    """Test detector finds model_copy usage in pattern fixtures."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Immutable Update Test")

    # Should find immutable updates
    update_patterns = report.patterns[PositivePattern.IMMUTABLE_UPDATES]
    assert len(update_patterns) > 0, "Should detect model_copy usage in pattern fixtures"

    # Verify specific patterns
    update_files = {p.file_path for p in update_patterns}
    assert any("rich_domain.py" in path for path in update_files)


def test_pattern_fixtures_have_high_pattern_ratio():
    """Test that pattern fixtures are predominantly patterns (integration reality check)."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Pattern Ratio Test")

    total_violations = sum(len(findings) for findings in report.violations.values())
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    total_findings = total_violations + total_patterns

    # Pattern fixtures should be predominantly patterns
    if total_findings > 0:
        pattern_ratio = total_patterns / total_findings
        assert pattern_ratio > 0.8, f"Pattern fixtures should be >80% patterns, got {pattern_ratio:.1%}"


def test_patterns_contain_meaningful_descriptions():
    """Test that patterns include helpful descriptions for developers."""
    report = sda_detector.analyze_module("tests/fixtures/patterns", "Pattern Description Test")

    # Check computed field patterns have helpful descriptions
    computed_patterns = report.patterns[PositivePattern.COMPUTED_FIELDS]
    if computed_patterns:
        description = computed_patterns[0].description
        assert "computed_field" in description.lower()
        assert len(description) > 10, "Descriptions should be meaningful"

    # Check protocol patterns mention their value
    protocol_patterns = report.patterns[PositivePattern.PROTOCOLS]
    if protocol_patterns:
        description = protocol_patterns[0].description
        assert "protocol" in description.lower()
