"""Analysis domain models for SDA architecture detection - The Core of Pattern Discovery.

PURPOSE:
This module defines the fundamental analysis concepts: what constitutes a finding,
how findings classify themselves, and how domain intelligence eliminates service logic.

SDA PRINCIPLES DEMONSTRATED:
1. **Self-Classifying Models**: Findings know their own pattern types
2. **Computed Intelligence**: Derived properties replace external functions
3. **Immutable Records**: Findings are frozen, ensuring data integrity
4. **No Naked Strings**: All classifications use typed enums
5. **Domain Logic in Models**: Classification logic lives with the data

LEARNING GOALS:
- Understand how Pydantic computed fields eliminate external logic
- Learn to encode classification rules directly in domain models
- Master the pattern of self-describing, self-classifying data
- See how immutability prevents entire categories of bugs
- Recognize how domain models can be both data AND behavior

ARCHITECTURE NOTES:
The Finding model is the atomic unit of analysis - everything we discover
becomes a Finding. By making findings self-classifying through computed
fields, we eliminate the need for external classification services.
This is "intelligence in the model" - a core SDA principle.

Teaching Example:
    >>> # Traditional approach (anemic model + service):
    >>> class Finding:
    >>>     def __init__(self, file, line, desc):
    >>>         self.file = file
    >>>         self.line = line
    >>>         self.desc = desc
    >>> 
    >>> def classify_finding(finding):  # External service function
    >>>     if 'isinstance' in finding.desc:
    >>>         return 'violation'
    >>>     elif 'pydantic' in finding.desc:
    >>>         return 'pattern'
    >>>     return 'unknown'
    >>> 
    >>> # SDA approach (intelligent model):
    >>> class Finding(BaseModel):
    >>>     file_path: str
    >>>     line_number: int
    >>>     description: str
    >>>     
    >>>     @computed_field
    >>>     @property
    >>>     def classification(self) -> str:
    >>>         # Model classifies itself!
    >>>         return self._determine_classification()

Key Insight:
This module shows that domain models aren't just data containers - they're
intelligent entities that understand their own semantics. This eliminates
the "anemic domain model" anti-pattern completely.
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .core_types import PatternType, PositivePattern


class Finding(BaseModel):
    """Represents a single architectural pattern detected in the codebase.

    WHAT: An immutable record of a detected pattern - either a violation of SDA
    principles or a positive pattern that aligns with them.
    
    WHY: Findings are the atomic unit of analysis. Instead of returning strings
    or tuples, we return strongly-typed Finding objects that carry semantic
    meaning and can classify themselves.
    
    HOW: Uses Pydantic's BaseModel with frozen=True for immutability, Field()
    for validation, and @computed_field for derived intelligence.
    
    Teaching Example:
        >>> # Create a finding (immutable once created):
        >>> finding = Finding(
        >>>     file_path="order.py",
        >>>     line_number=42,
        >>>     description="isinstance_usage: Checking if order is PremiumOrder"
        >>> )
        >>> 
        >>> # Model computes its own properties:
        >>> print(finding.location)  # "order.py:42" - computed field
        >>> print(finding.pattern_category)  # PatternType.ISINSTANCE_USAGE - self-classified
        >>> 
        >>> # Immutability prevents bugs:
        >>> finding.line_number = 50  # Raises error - can't modify frozen model
    
    SDA Patterns Demonstrated:
        1. **Immutable Domain Objects**: frozen=True prevents modification bugs
        2. **Self-Classifying Intelligence**: Computed fields derive pattern types
        3. **Rich Domain Models**: Data + behavior in one cohesive unit
        4. **Type-Safe Descriptions**: Even strings follow patterns
    
    Architecture Note:
        This model eliminates the need for separate FindingClassifier,
        FindingFormatter, or FindingValidator services. All that logic
        lives IN the model itself. This is the opposite of anemic models.
    """

    model_config = ConfigDict(frozen=True)  # Teaching: Immutability prevents state mutation bugs

    # Teaching: Every field has constraints - no naked primitives!
    file_path: str = Field(
        description="Path to the file containing this finding",
        # Teaching: Even paths could be validated with regex or Path type
    )
    line_number: int = Field(
        ge=0,  # Teaching: Greater-or-equal constraint - line numbers start at 0
        description="Line number where pattern was found"
    )
    description: str = Field(
        min_length=1,  # Teaching: No empty descriptions allowed
        description="Description of the pattern found",
        # Teaching: Description follows pattern "<type>: <details>"
    )

    @computed_field
    @property
    def location(self) -> str:
        """Computed property that formats file location for display.

        Teaching Note: COMPUTED FIELDS VS METHODS VS PROPERTIES
        
        Why @computed_field instead of a regular @property or method?
        
        1. @computed_field: Cached, included in model_dump(), part of schema
        2. @property: Not cached, not in model_dump(), not in schema  
        3. def method(): Requires calling with (), not Pythonic for getters
        
        Since location is derived data we want in serialization, we use
        @computed_field. This makes it act like a real field but computed.
        
        SDA Pattern:
            Instead of format_location(finding) in a service, the model
            knows how to format itself. Data and its representation together.
        
        Returns:
            Formatted string like "file.py:123" for easy IDE navigation
        """
        return f"{self.file_path}:{self.line_number}"

    @computed_field
    @property
    def classification(self) -> str | None:
        """Domain intelligence: finding classifies itself.

        Teaching Note: SELF-CLASSIFICATION PATTERN
        
        This computed field eliminates the need for external classification.
        Instead of:
            classifier_service.classify(finding)
        
        We have:
            finding.classification  # Model knows its own type!
        
        This is a simple classification for backward compatibility.
        The real intelligence is in pattern_category and pattern_type below.
        
        Philosophy:
            "Objects should know about themselves" - this is the essence
            of object-oriented design taken to its logical conclusion.
        """
        # Simple classification for backward compatibility
        return self.description.lower()

    @computed_field
    @property
    def pattern_category(self) -> PatternType | None:
        """Self-classifying domain intelligence - neutral pattern detection.
        
        Teaching Note: PATTERN MATCHING WITH DATA STRUCTURES
        
        This method shows how to do pattern matching without conditionals:
        
        1. Define patterns as data (dictionary of sets)
        2. Iterate and check membership
        3. Return first match or None
        
        The pattern_indicators dictionary is like a mini rule engine.
        Each key is a pattern type, each value is a set of indicators.
        
        Why sets instead of lists?
        - O(1) membership testing with 'in'
        - Automatically deduplicated
        - Communicates "unique values" intent
        
        Advanced Note:
            This uses a for loop, which might seem like a violation.
            But it's iterating over DATA, not making business decisions.
            The actual classification is data-driven via the dictionary.
        """
        description_lower = self.description.lower()

        # Teaching: Rule engine as data structure
        pattern_indicators = {
            PatternType.ISINSTANCE_USAGE: {"isinstance_usage"},
            PatternType.MANUAL_JSON_SERIALIZATION: {"manual_json_serialization"},
            PatternType.ENUM_VALUE_ACCESS: {"enum_value_unwrapping", "enum_value_access"},
            PatternType.BUSINESS_CONDITIONALS: {"business_conditionals"},
        }

        # Teaching: Data-driven pattern matching
        for pattern_type, indicators in pattern_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return pattern_type
        return None

    @computed_field
    @property
    def pattern_type(self) -> PositivePattern | None:
        """Self-classifying domain intelligence for positive patterns.
        
        Teaching Note: DUAL CLASSIFICATION SYSTEM
        
        Why separate pattern_category and pattern_type?
        
        - pattern_category: Violations/anti-patterns (what to avoid)
        - pattern_type: Positive patterns (what to embrace)
        
        A finding could theoretically have both (edge case handling at
        a boundary might use try/except but also use Pydantic models).
        
        By separating them, we:
        1. Allow nuanced classification
        2. Avoid forcing binary good/bad judgments
        3. Enable richer reporting and analysis
        
        Implementation Note:
            Same pattern as pattern_category but checking for positive
            indicators. This consistency makes the code predictable.
        """
        description_lower = self.description.lower()

        # Teaching: Positive patterns we want to encourage
        pattern_indicators = {
            PositivePattern.COMPUTED_FIELDS: {"computed_fields"},
            PositivePattern.PYDANTIC_SERIALIZATION: {"pydantic_serialization"},
        }

        for pattern_type, indicators in pattern_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return pattern_type
        return None
