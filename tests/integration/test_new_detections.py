"""Integration tests for NEW pattern detections only.

Following SDA testing philosophy:
- Test that new patterns are detected in real fixtures
- Minimal assertions - just verify detection works
- No testing of framework features
"""

from pathlib import Path

from src.sda_detector.service import DetectionService


class TestNewPatternDetection:
    """Integration tests for the 5 new pattern detections."""

    def setup_method(self):
        """Initialize service for each test."""
        self.service = DetectionService()
        self.fixtures_path = Path("tests/fixtures/violations")

    def test_cast_detection_in_fixtures(self):
        """Verify cast() violations are detected in new fixture."""
        fixture = str(self.fixtures_path / "cast_usage.py")
        report = self.service.analyze_module(fixture)

        # Cast operations should be detected as isinstance_usage
        assert report.total_violations > 0
        assert any("isinstance_usage" in str(pattern) for pattern in report.violations)

        # Should detect multiple cast operations (we have 5+ in fixture)
        isinstance_findings = [f for findings in report.violations.values() for f in findings]
        assert len(isinstance_findings) >= 5

    def test_match_case_detection_in_fixtures(self):
        """Verify match/case violations are detected."""
        fixture = str(self.fixtures_path / "match_case.py")
        report = self.service.analyze_module(fixture)

        # Match/case should be detected as business_conditionals
        assert report.total_violations > 0
        assert any("business_conditionals" in str(pattern) for pattern in report.violations)

        # Should detect multiple match statements (we have 3 in fixture)
        conditional_findings = [
            f for findings in report.violations.values() for f in findings if "business_conditionals" in f.description
        ]
        assert len(conditional_findings) >= 3

    def test_any_type_detection_in_fixtures(self):
        """Verify Any type violations are detected."""
        fixture = str(self.fixtures_path / "any_type.py")
        report = self.service.analyze_module(fixture)

        # Any should be detected through function calls
        assert report.total_violations > 0

        # Check for isinstance_usage (Any is detected as type check)
        assert any("isinstance_usage" in str(pattern) for pattern in report.violations)

    def test_string_literal_detection_in_fixtures(self):
        """Verify repeated literals are detected."""
        fixture = str(self.fixtures_path / "string_literals.py")
        report = self.service.analyze_module(fixture)

        # String literals create business conditionals
        assert report.total_violations > 0

        # The repeated strings cause multiple conditionals
        assert any("business_conditionals" in str(pattern) for pattern in report.violations)

        # Should have many conditionals from string comparisons
        conditional_count = sum(
            len(findings) for pattern, findings in report.violations.items() if "business_conditionals" in str(pattern)
        )
        assert conditional_count >= 5  # We have many string comparisons

    def test_lazy_init_detection_in_fixtures(self):
        """Verify lazy initialization is detected."""
        fixture = str(self.fixtures_path / "lazy_init.py")
        report = self.service.analyze_module(fixture)

        # Lazy init patterns should be detected as business_conditionals
        assert report.total_violations > 0
        assert any("business_conditionals" in str(pattern) for pattern in report.violations)

        # Should detect at least 2 lazy init patterns
        # (We have multiple "if self._cache is None" patterns)
        conditional_count = sum(
            len(findings) for pattern, findings in report.violations.items() if "business_conditionals" in str(pattern)
        )
        assert conditional_count >= 2
