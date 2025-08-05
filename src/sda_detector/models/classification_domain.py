"""Module classification domain intelligence.

SDA Core: Data drives behavior. Classifiers know how to analyze themselves.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .core_types import ModuleType


class ModuleClassifier(BaseModel):
    """Domain intelligence for module classification operations.

    Self-analyzing model that determines module types and provides path operations.
    Classifiers know their own capabilities through computed properties.
    """

    model_config = ConfigDict(frozen=True)

    path: str = Field(description="Path string for analysis")

    @computed_field
    @property
    def classified_type(self) -> ModuleType:
        """Domain intelligence: classify module type based on path patterns."""
        path_lower = self.path.lower()

        # Use set intersection for sophisticated simplicity
        classification_patterns = {
            ModuleType.DOMAIN: {"model", "domain", "entity", "business"},
            ModuleType.INFRASTRUCTURE: {
                "redis",
                "postgres",
                "mysql",
                "database",
                "db",
                "storage",
                "cache",
                "client",
                "external",
                "api",
                "gateway",
                "adapter",
                "repository",
            },
            ModuleType.TOOLING: {"test", "tool", "script", "cli", "util", "helper"},
            ModuleType.FRAMEWORK: {"framework", "lib", "core", "base"},
        }

        for module_type, patterns in classification_patterns.items():
            if any(pattern in path_lower for pattern in patterns):
                return module_type

        return ModuleType.MIXED

    @computed_field
    @property
    def path_obj(self) -> Path:
        """Domain intelligence: convert to Path object for operations."""
        return Path(self.path)

    @computed_field
    @property
    def is_file(self) -> bool:
        """Domain intelligence: determine if this is a file."""
        return self.path_obj.is_file()

    @computed_field
    @property
    def is_directory(self) -> bool:
        """Domain intelligence: determine if this is a directory."""
        return self.path_obj.is_dir()

    @computed_field
    @property
    def python_files(self) -> list[str]:
        """Domain intelligence: get Python files based on path type.

        Uses boolean coercion to eliminate explicit conditionals.
        Files take precedence over directories in the resolution.
        """
        # SDA: Boolean coercion eliminates conditionals
        file_result = [str(self.path_obj)] if self.is_file else []
        directory_result = [str(f) for f in self.path_obj.glob("*.py")] if self.is_directory else []

        # Domain intelligence: files take precedence over directories
        return file_result or directory_result

    @computed_field
    @property
    def stem(self) -> str:
        """Domain intelligence: get the path stem for naming."""
        return self.path_obj.stem

    def create_relative_path(self, target_path: str, module_name: str) -> str:
        """Domain intelligence: create relative path based on context.

        Determines package path structure based on target path characteristics.
        """
        target = Path(target_path)

        # SDA: Boolean coercion instead of conditionals
        package_path = str(target.parent / module_name) if target.suffix else str(target / module_name)

        # Domain intelligence: paths know how to be relative
        return str(Path(package_path).relative_to(Path.cwd()))
