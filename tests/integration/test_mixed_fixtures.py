"""Integration tests for mixed fixtures - boundary vs domain code analysis.

Following SDA testing philosophy: Test realistic scenarios with mixed concerns.
"""

from src.sda_detector import analyze_module
from src.sda_detector.models import PositivePattern, PatternType


def test_mixed_fixtures_balanced_analysis():
    """Test that mixed fixtures show realistic balance of patterns vs violations."""
    report = analyze_module("tests/fixtures/mixed", "Mixed Fixture Test")

    total_violations = sum(len(findings) for findings in report.violations.values())
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    total_findings = total_violations + total_patterns

    # Mixed fixtures should have both patterns and violations
    assert total_violations > 0, "Mixed fixtures should have some violations (boundary code)"
    assert total_patterns > 0, "Mixed fixtures should have some patterns (domain code)"
    assert total_findings > 10, "Mixed fixtures should be substantial"

    # Neither should completely dominate (realistic mixed code)
    violation_ratio = total_violations / total_findings if total_findings > 0 else 0
    assert 0.2 < violation_ratio < 0.8, f"Mixed code should be balanced, got {violation_ratio:.1%} violations"


def test_boundary_conditions_detected_in_mixed():
    """Test that mixed fixtures contain both patterns and violations."""
    report = analyze_module("tests/fixtures/mixed", "Mixed Balance Test")

    # Mixed fixtures should have substantial patterns (we saw 74 total)
    total_patterns = sum(len(findings) for findings in report.patterns.values())
    assert total_patterns > 50, f"Mixed fixtures should have many patterns. Found: {total_patterns}"
    
    # Should have computed fields specifically (we saw 66)
    computed_patterns = report.patterns.get(PositivePattern.COMPUTED_FIELDS, [])
    assert len(computed_patterns) > 50, f"Should have many computed fields. Found: {len(computed_patterns)}"
    
    # Should also have violations (we saw 62 total)
    total_violations = sum(len(findings) for findings in report.violations.values())
    assert total_violations > 40, f"Mixed fixtures should have violations too. Found: {total_violations}"


def test_domain_patterns_detected_in_mixed():
    """Test that pure domain patterns are detected in mixed fixtures."""
    report = analyze_module("tests/fixtures/mixed", "Domain Pattern Test")

    # Should find domain patterns
    computed_patterns = report.patterns[PositivePattern.COMPUTED_FIELDS]
    if computed_patterns:
        domain_files = {p.file_path for p in computed_patterns}
        assert any("domain_code.py" in path for path in domain_files)


def test_infrastructure_violations_expected():
    """Test that infrastructure code legitimately has certain 'violations'."""
    report = analyze_module("tests/fixtures/mixed", "Infrastructure Test")

    # Infrastructure code may have isinstance (legitimate boundary pattern)
    isinstance_violations = report.violations[PatternType.ISINSTANCE_USAGE]
    if isinstance_violations:
        infra_files = {v.file_path for v in isinstance_violations}
        # These should be in boundary/infrastructure files, not domain files
        assert any("redis_client.py" in path or "boundary_code.py" in path for path in infra_files)


def test_mixed_demonstrates_sda_principles():
    """Test that mixed fixtures demonstrate proper SDA separation."""
    report = analyze_module("tests/fixtures/mixed", "SDA Principle Test")

    # Should show clear separation between domain and infrastructure concerns
    total_violations = sum(len(findings) for findings in report.violations.values())
    total_patterns = sum(len(findings) for findings in report.patterns.values())

    # The mix should be meaningful (not random)
    assert total_violations >= 20, "Should have substantial boundary/infrastructure code"
    assert total_patterns >= 20, "Should have substantial domain patterns"

    # Should demonstrate the value of SDA classification
    assert report.module_type in ["tooling", "mixed"], "Mixed fixtures should be classified appropriately"
