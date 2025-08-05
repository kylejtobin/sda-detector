"""Analysis domain models for SDA architecture detection.

These models handle the core analysis logic: what we find during analysis,
how we configure analysis behavior, and what context we maintain while
traversing the AST.

These models contain the business logic about HOW analysis works.
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .core_types import PatternType, PositivePattern


class Finding(BaseModel):
    """Represents a single architectural pattern detected in the codebase.

    A Finding is an immutable record of something we observed - a specific
    architectural pattern detected in the code for neutral analysis.

    This is pure data with computed properties, following SDA principles.
    The model teaches us what constitutes a finding and how to display it.

    Attributes:
        file_path: Which file the pattern was found in
        line_number: Which line in the file (for navigation)
        description: Human-readable description of what was found
    """

    model_config = ConfigDict(frozen=True)

    file_path: str = Field(description="Path to the file containing this finding")
    line_number: int = Field(ge=0, description="Line number where pattern was found")
    description: str = Field(min_length=1, description="Description of the pattern found")

    @computed_field
    @property
    def location(self) -> str:
        """Computed property that formats file location for display.

        This is a SDA pattern - instead of having a separate function
        format_location(finding), we encode the formatting logic
        directly into the domain model using a computed field.

        Returns:
            Formatted string like "file.py:123" for easy navigation
        """
        return f"{self.file_path}:{self.line_number}"

    @computed_field
    @property
    def classification(self) -> str | None:
        """Domain intelligence: finding classifies itself.

        This removes conditional classification logic from services.
        The finding knows its own type based on its description.

        Rule 070: "Use Pydantic intelligence over procedural checks"
        """
        # Simple classification for backward compatibility
        return self.description.lower()

    @computed_field
    @property
    def pattern_category(self) -> PatternType | None:
        """Self-classifying domain intelligence - neutral pattern detection."""
        description_lower = self.description.lower()

        pattern_indicators = {
            PatternType.ISINSTANCE_USAGE: {"isinstance_usage"},
            PatternType.MANUAL_JSON_SERIALIZATION: {"manual_json_serialization"},
            PatternType.ENUM_VALUE_ACCESS: {"enum_value_unwrapping", "enum_value_access"},
            PatternType.BUSINESS_CONDITIONALS: {"business_conditionals"},
        }

        for pattern_type, indicators in pattern_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return pattern_type
        return None

    @computed_field
    @property
    def pattern_type(self) -> PositivePattern | None:
        """Self-classifying domain intelligence for positive patterns."""
        description_lower = self.description.lower()

        pattern_indicators = {
            PositivePattern.COMPUTED_FIELDS: {"computed_fields"},
            PositivePattern.PYDANTIC_SERIALIZATION: {"pydantic_serialization"},
        }

        for pattern_type, indicators in pattern_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return pattern_type
        return None
