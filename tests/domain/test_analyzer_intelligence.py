"""Test domain intelligence in analyzers - classification logic only.

Following SDA testing philosophy:
- Test where intelligence lives (classification algorithms)
- Trust where types rule (Pydantic validation)
- Test domain decisions, not framework features
"""

from src.sda_detector.models.analyzers.ast_utils import ASTNodeMetadata
from src.sda_detector.models.analyzers.attribute_analyzer import AttributeDomain, AttributePattern
from src.sda_detector.models.analyzers.call_analyzer import CallDomain, CallPattern
from src.sda_detector.models.analyzers.conditional_analyzer import ConditionalDomain, ConditionalPattern
from src.sda_detector.models.core_types import ASTNodeCategory


class TestCallDomainIntelligence:
    """Test the business logic in CallDomain classification."""
    
    def test_call_pattern_classification_intelligence(self):
        """Test that CallDomain correctly classifies function patterns.
        This is BUSINESS LOGIC - the tuple dispatch classification."""
        
        # Test original type check classification
        isinstance_call = CallDomain(function_name="isinstance", line_number=10)
        assert isinstance_call.call_pattern == CallPattern.TYPE_CHECK
        
        # Test NEW cast detection
        cast_call = CallDomain(function_name="cast", line_number=20)
        assert cast_call.call_pattern == CallPattern.TYPE_CHECK
        
        # Test NEW Any detection
        any_call = CallDomain(function_name="Any", line_number=30)
        assert any_call.call_pattern == CallPattern.TYPE_CHECK
        
        # Test JSON classification remains correct
        dumps_call = CallDomain(function_name="dumps", line_number=40)
        assert dumps_call.call_pattern == CallPattern.JSON_OPERATION
        
        # Test Pydantic classification
        field_call = CallDomain(function_name="Field", line_number=50)
        assert field_call.call_pattern == CallPattern.PYDANTIC_OPERATION
    
    def test_call_pattern_priority_dispatch(self):
        """Test classification priority - tuple dispatch exhaustive mapping."""
        
        # Test that unknown functions get COMPUTED_FIELD classification
        unknown_call = CallDomain(function_name="unknown_func", line_number=60)
        assert unknown_call.call_pattern == CallPattern.COMPUTED_FIELD
        
        # Test that classification is deterministic
        # Same input always produces same output (pure function)
        call1 = CallDomain(function_name="type", line_number=70)
        call2 = CallDomain(function_name="type", line_number=80)
        assert call1.call_pattern == call2.call_pattern == CallPattern.TYPE_CHECK


class TestConditionalDomainIntelligence:
    """Test the business logic in ConditionalDomain classification."""
    
    def test_lazy_initialization_detection(self):
        """Test NEW lazy init pattern detection intelligence."""
        
        # Test cache pattern detection
        cache_cond = ConditionalDomain(
            test_expression="self._cache is None",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.CONTROL_FLOW,
                line_number=10,
                name="condition"
            ),
            parent_scope=None,
            nested_depth=0
        )
        assert cache_cond.is_lazy_initialization is True
        assert cache_cond.pattern_classification == ConditionalPattern.LAZY_INITIALIZATION
        
        # Test initialized pattern detection
        init_cond = ConditionalDomain(
            test_expression="not self._initialized",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.CONTROL_FLOW,
                line_number=20,
                name="condition"
            ),
            parent_scope=None,
            nested_depth=0
        )
        assert init_cond.is_lazy_initialization is True
        assert init_cond.pattern_classification == ConditionalPattern.LAZY_INITIALIZATION
        
        # Test that normal conditions are not lazy init
        normal_cond = ConditionalDomain(
            test_expression="x > 5",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.CONTROL_FLOW,
                line_number=30,
                name="condition"
            ),
            parent_scope=None,
            nested_depth=0
        )
        assert normal_cond.is_lazy_initialization is False
        assert normal_cond.pattern_classification == ConditionalPattern.BUSINESS_LOGIC
    
    def test_conditional_pattern_priority(self):
        """Test that pattern classification respects priority order."""
        
        # TYPE_CHECKING takes highest priority
        type_check = ConditionalDomain(
            test_expression="TYPE_CHECKING",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.CONTROL_FLOW,
                line_number=40,
                name="condition"
            ),
            parent_scope=None,
            nested_depth=0
        )
        assert type_check.pattern_classification == ConditionalPattern.TYPE_GUARD
        
        # Even if it's also lazy init pattern (hypothetically)
        # TYPE_CHECKING should still win due to priority
        assert type_check.is_type_checking is True


class TestAttributeDomainIntelligence:
    """Test the business logic in AttributeDomain classification."""
    
    def test_attribute_pattern_priority(self):
        """Test that enum unwrapping takes priority over computed field suggestion."""
        
        # Test enum value access gets correct pattern
        enum_attr = AttributeDomain(
            attribute_name="value",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.BEHAVIORAL,
                line_number=10,
                name="attribute"
            )
        )
        assert enum_attr.is_enum_unwrapping is True
        assert enum_attr.pattern_classification == AttributePattern.ENUM_UNWRAPPING
        
        # Test computed field suggestion
        computed_attr = AttributeDomain(
            attribute_name="total",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.BEHAVIORAL,
                line_number=20,
                name="attribute"
            )
        )
        assert computed_attr.suggests_computed_field is True
        assert computed_attr.pattern_classification == AttributePattern.COMPUTED_FIELD_CANDIDATE
        
        # Test that normal attributes get no pattern
        normal_attr = AttributeDomain(
            attribute_name="name",
            metadata=ASTNodeMetadata(
                category=ASTNodeCategory.BEHAVIORAL,
                line_number=30,
                name="attribute"
            )
        )
        assert normal_attr.is_enum_unwrapping is False
        assert normal_attr.suggests_computed_field is False
        assert normal_attr.pattern_classification == AttributePattern.NORMAL_ACCESS