"""Test fixture for lazy initialization pattern violations.

This module demonstrates lazy initialization patterns that violate SDA principles.
Lazy init with conditionals should be replaced with proper initialization strategies.
"""

from typing import Optional, Any


class DataCache:
    """VIOLATION: Lazy initialization with conditionals."""
    
    def __init__(self):
        # ❌ BAD: Using None to indicate uninitialized state
        self._cache: Optional[dict] = None
        self._expensive_data: Optional[list] = None
    
    def get_cache(self) -> dict:
        """VIOLATION: Conditional lazy loading."""
        # ❌ BAD: if self._cache is None pattern
        if self._cache is None:  # Lazy init violation!
            print("Loading cache...")
            self._cache = self._load_cache()
        return self._cache
    
    def get_expensive_data(self) -> list:
        """VIOLATION: Another lazy init pattern."""
        # ❌ BAD: Checking for None again
        if self._expensive_data is None:  # Another violation!
            self._expensive_data = self._compute_expensive_data()
        return self._expensive_data
    
    def _load_cache(self) -> dict:
        return {"key": "value"}
    
    def _compute_expensive_data(self) -> list:
        return [1, 2, 3, 4, 5]


class ConnectionManager:
    """VIOLATION: Lazy initialization with boolean flag."""
    
    def __init__(self):
        # ❌ BAD: Boolean flag for initialization state
        self._initialized = False
        self._connection = None
    
    def get_connection(self):
        """VIOLATION: Checking initialization flag."""
        # ❌ BAD: if not self._initialized pattern
        if not self._initialized:  # Lazy init violation!
            self._initialize()
        return self._connection
    
    def _initialize(self):
        """Late initialization logic."""
        print("Initializing connection...")
        self._connection = "database_connection"
        self._initialized = True


class ConfigLoader:
    """VIOLATION: Multiple lazy initialization patterns."""
    
    def __init__(self):
        # ❌ BAD: Multiple nullable fields for lazy loading
        self._config: Optional[dict] = None
        self._secrets: Optional[dict] = None
        self._features: Optional[set] = None
    
    def get_config(self) -> dict:
        """VIOLATION: Lazy load config."""
        # ❌ BAD: Repeated pattern
        if self._config is None:  # Violation!
            self._config = {"app": "myapp"}
        return self._config
    
    def get_secrets(self) -> dict:
        """VIOLATION: Lazy load secrets."""
        # ❌ BAD: Same pattern again
        if self._secrets is None:  # Another violation!
            self._secrets = {"api_key": "secret"}
        return self._secrets
    
    def is_feature_enabled(self, feature: str) -> bool:
        """VIOLATION: Lazy load with membership check."""
        # ❌ BAD: Conditional initialization
        if self._features is None:  # Yet another violation!
            self._features = {"feature1", "feature2"}
        return feature in self._features


# ============================================================================
# SDA-COMPLIANT ALTERNATIVES  
# ============================================================================

from pydantic import BaseModel, Field
from functools import cached_property


class DataCacheSDA(BaseModel):
    """✅ GOOD: Eager initialization with computed properties."""
    
    # Initialize eagerly in __init__ or use factory pattern
    _cache: dict = Field(default_factory=dict)
    
    @cached_property
    def expensive_data(self) -> list:
        """✅ GOOD: Use cached_property for expensive computations."""
        print("Computing expensive data once...")
        return [1, 2, 3, 4, 5]
    
    @classmethod
    def create_with_cache(cls, cache_data: dict) -> "DataCacheSDA":
        """✅ GOOD: Factory method for initialization."""
        return cls(_cache=cache_data)


from enum import StrEnum


class ConnectionState(StrEnum):
    """✅ GOOD: Explicit state instead of boolean flag."""
    UNINITIALIZED = "uninitialized"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"


class ConnectionManagerSDA(BaseModel):
    """✅ GOOD: Explicit state management."""
    
    state: ConnectionState = ConnectionState.UNINITIALIZED
    connection: Optional[Any] = None
    
    def ensure_connected(self) -> "ConnectionManagerSDA":
        """✅ GOOD: Return new state instead of mutation."""
        state_handlers = {
            ConnectionState.UNINITIALIZED: lambda: self._connect(),
            ConnectionState.CONNECTING: lambda: self,
            ConnectionState.CONNECTED: lambda: self,
            ConnectionState.FAILED: lambda: self._reconnect(),
        }
        return state_handlers[self.state]()
    
    def _connect(self) -> "ConnectionManagerSDA":
        """Create new instance with connection."""
        return self.model_copy(
            update={
                "state": ConnectionState.CONNECTED,
                "connection": "database_connection"
            }
        )
    
    def _reconnect(self) -> "ConnectionManagerSDA":
        """Attempt reconnection."""
        return self._connect()


class ConfigLoaderSDA(BaseModel):
    """✅ GOOD: Initialize everything upfront."""
    
    config: dict = Field(default_factory=lambda: {"app": "myapp"})
    secrets: dict = Field(default_factory=lambda: {"api_key": "secret"})
    features: set = Field(default_factory=lambda: {"feature1", "feature2"})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """No lazy loading needed - data already initialized."""
        return feature in self.features


# The SDA way: Initialize eagerly or use explicit state machines
# No conditional lazy loading - use cached_property or factories
# Model state explicitly with enums, not nullable fields