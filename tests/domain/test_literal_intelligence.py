"""Test domain intelligence in literal analyzer - repetition detection only.

Following SDA testing philosophy:
- Test the domain logic for detecting repetition
- Trust Pydantic for data validation
- One focused test for the core intelligence
"""

from src.sda_detector.models.analyzers.literal_analyzer import LiteralDomain
from src.sda_detector.models.context_domain import RichAnalysisContext
from src.sda_detector.models.core_types import ModuleType


class TestLiteralDomainIntelligence:
    """Test the business logic in LiteralDomain repetition detection."""
    
    def test_literal_repetition_detection(self):
        """Test that LiteralDomain detects repeated string literals.
        This is the core domain intelligence - identifying repetition."""
        
        # Create domain with repeated literals
        literals_data = {
            "processing": [10, 25, 42],  # Repeated 3 times
            "error": [15, 30],  # Repeated 2 times  
            "unique": [20],  # Only once - should not be flagged
            "production": [35, 50, 65, 80],  # Repeated 4 times
        }
        
        domain = LiteralDomain(literals=literals_data)
        
        # Create context for analysis
        context = RichAnalysisContext(
            current_file="test.py",
            module_type=ModuleType.MIXED,
            scope_stack=[]
        )
        
        # Test the intelligence: repetition detection
        findings = domain.analyze(context)
        
        # Should detect 3 repeated literals (not "unique")
        assert len(findings) == 3
        
        # Check that repeated literals are detected
        descriptions = [f.description for f in findings]
        assert any("processing" in d and "3 times" in d for d in descriptions)
        assert any("error" in d and "2 times" in d for d in descriptions)
        assert any("production" in d and "4 times" in d for d in descriptions)
        
        # Ensure unique literal is not flagged
        assert not any("unique" in d for d in descriptions)