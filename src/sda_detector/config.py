"""SDA Detector configuration using Pydantic Settings.

This demonstrates SDA best practice: configuration as a rich domain model
with validation, computed fields, and intelligent defaults.
"""

from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models import ModuleType


class ModuleClassificationRules(BaseModel):
    """Domain model for module classification patterns.

    This model encapsulates the business logic of how to classify
    different types of modules based on file path patterns.
    """

    model_config = {"frozen": True}

    # Infrastructure patterns (boundary/external systems)
    infrastructure_patterns: list[str] = Field(
        default_factory=lambda: [
            # Databases
            "redis",
            "postgres",
            "postgresql",
            "mongo",
            "mongodb",
            "mysql",
            "sqlite",
            "database",
            "db",
            "sql",
            "nosql",
            "orm",
            "sqlalchemy",
            "peewee",
            # Storage & Caching
            "storage",
            "cache",
            "s3",
            "blob",
            "file",
            "disk",
            # External APIs & Clients
            "client",
            "api",
            "http",
            "rest",
            "graphql",
            "grpc",
            "webhook",
            "external",
            "third_party",
            "integration",
            # Infrastructure services
            "infra",
            "infrastructure",
            "queue",
            "broker",
            "message",
            "event",
            "auth",
            "oauth",
            "jwt",
            "session",
            "security",
            # Cloud & DevOps
            "aws",
            "gcp",
            "azure",
            "docker",
            "k8s",
            "kubernetes",
            "terraform",
        ],
        description="Keywords that indicate infrastructure/boundary modules",
    )

    # Development tooling patterns
    tooling_patterns: list[str] = Field(
        default_factory=lambda: [
            # Code analysis
            "detector",
            "parser",
            "analyzer",
            "ast",
            "visitor",
            "scanner",
            "lexer",
            "linter",
            "formatter",
            "checker",
            "validator",
            "inspector",
            # Testing
            "test",
            "mock",
            "fixture",
            "factory",
            "builder",
            "generator",
            # Development utilities
            "cli",
            "command",
            "script",
            "tool",
            "util",
            "helper",
            "debug",
            "profile",
            "benchmark",
            "metrics",
            # Build & deployment
            "build",
            "deploy",
            "migration",
            "seed",
            "setup",
            "config",
        ],
        description="Keywords that indicate development/analysis tools",
    )

    # Framework integration patterns
    framework_patterns: list[str] = Field(
        default_factory=lambda: [
            # Web frameworks
            "fastapi",
            "flask",
            "django",
            "starlette",
            "uvicorn",
            "gunicorn",
            "tornado",
            "aiohttp",
            "quart",
            "sanic",
            # Data processing
            "dagster",
            "airflow",
            "celery",
            "rq",
            "dramatiq",
            "pandas",
            "numpy",
            # ML/AI frameworks
            "pytorch",
            "tensorflow",
            "sklearn",
            "huggingface",
            "transformers",
            # Type & validation libraries
            "pydantic",
            "marshmallow",
            "cerberus",
            "voluptuous",
            # Testing frameworks
            "pytest",
            "unittest",
            "nose",
            "hypothesis",
            "factory_boy",
            # Async frameworks
            "asyncio",
            "trio",
            "anyio",
            "twisted",
        ],
        description="Keywords that indicate framework integration code",
    )

    # Pure domain patterns
    domain_patterns: list[str] = Field(
        default_factory=lambda: [
            # Domain concepts
            "domain",
            "model",
            "entity",
            "aggregate",
            "value",
            "service",
            "business",
            "core",
            "logic",
            "rule",
            "policy",
            "strategy",
            # Domain-specific terms
            "user",
            "account",
            "order",
            "payment",
            "product",
            "inventory",
            "customer",
            "transaction",
            "billing",
            "subscription",
            "catalog",
        ],
        description="Keywords that indicate pure domain logic",
    )

    @computed_field
    @property
    def all_patterns(self) -> dict[ModuleType, list[str]]:
        """Type dispatch rules for module classification.

        This computed field demonstrates SDA: instead of hard-coding
        classification logic, the configuration model provides it.
        """
        return {
            ModuleType.INFRASTRUCTURE: self.infrastructure_patterns,
            ModuleType.TOOLING: self.tooling_patterns,
            ModuleType.FRAMEWORK: self.framework_patterns,
            ModuleType.DOMAIN: self.domain_patterns,
        }

    @computed_field
    @property
    def pattern_count(self) -> int:
        """Total number of classification patterns configured."""
        return sum(len(patterns) for patterns in self.all_patterns.values())

    def classify_by_path(self, file_path: str) -> ModuleType:
        """Classify a module based on its file path.

        This method encapsulates the classification business logic
        within the configuration domain model.
        """
        path_lower = file_path.lower()

        # Count pattern matches for each module type
        pattern_scores = {
            module_type: sum(1 for pattern in patterns if pattern in path_lower)
            for module_type, patterns in self.all_patterns.items()
        }

        # Find highest score
        max_score = max(pattern_scores.values(), default=0)

        # Return the module type with highest score, or MIXED if no matches
        return next(
            (module_type for module_type, score in pattern_scores.items() if score == max_score and score > 0),
            ModuleType.MIXED,
        )


class AnalysisSettings(BaseSettings):
    """SDA Detector configuration using Pydantic Settings.

    This follows SDA best practices:
    - Configuration as a rich domain model
    - Environment variable integration
    - Validation and computed fields
    - Intelligent defaults
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
    )

    # Analysis behavior configuration
    strict_mode: bool = Field(
        default=False, description="Enable strict analysis mode with zero tolerance for violations"
    )

    classify_modules: bool = Field(default=True, description="Enable module type classification")

    show_positive_patterns: bool = Field(default=True, description="Show positive SDA patterns in reports")

    max_findings_per_type: int = Field(
        default=2, ge=1, le=50, description="Maximum findings to show per violation/pattern type"
    )

    # Module classification rules
    classification_rules: ModuleClassificationRules = Field(
        default_factory=ModuleClassificationRules, description="Rules for classifying module types"
    )

    # Reporting configuration
    report_format: str = Field(
        default="console", pattern=r"^(console|json|markdown|html)$", description="Output format for analysis reports"
    )

    include_file_metrics: bool = Field(default=True, description="Include file-level metrics in reports")

    @computed_field
    @property
    def is_lenient_mode(self) -> bool:
        """Computed field for lenient analysis mode."""
        return not self.strict_mode

    @computed_field
    @property
    def analysis_mode_description(self) -> str:
        """Human-readable description of current analysis mode."""
        mode = "Strict" if self.strict_mode else "Lenient"
        classification = "with" if self.classify_modules else "without"
        return f"{mode} mode {classification} module classification"

    @computed_field
    @property
    def total_classification_patterns(self) -> int:
        """Total number of patterns available for classification."""
        return self.classification_rules.pattern_count


# Global configuration instance
# This can be overridden by environment variables or .env file
config = AnalysisSettings()
