"""Core enumerations for the dependency injection system."""

from enum import Enum


class ComponentScope(Enum):
    """
    Enumeration of component lifecycle scopes.

    Defines how component instances are managed throughout their lifecycle.
    """

    SINGLETON = "singleton"  # Single instance shared across application
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # Instance per scope (request, etc.)
    FACTORY = "factory"  # Created by factory function
    CONDITIONAL = "conditional"  # Created based on runtime condition


class ComponentLayer(Enum):
    """
    Enumeration of architectural layers for component organization.

    Helps organize components by their architectural responsibilities.
    """

    INFRASTRUCTURE = "infrastructure"  # Data access, external services
    APPLICATION = "application"  # Business logic, use cases
    DOMAIN = "domain"  # Core business entities and rules
    FRAMEWORK = "framework"  # Framework-level components
    PRESENTATION = "presentation"  # UI, controllers, API endpoints


class RegistrationStrategy(Enum):
    """
    Enumeration of component registration strategies.

    Defines how components are registered and created.
    """

    FACTORY = "factory"
    INSTANCE = "instance"
    CLASS_CONSTRUCTOR = "class_constructor"
    FACTORY_METHOD = "factory_method"


class LifecycleStage(Enum):
    """
    Enumeration of component lifecycle stages.

    Tracks the current state of a component through its lifecycle.
    """

    # Core lifecycle stages
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

    # Extended lifecycle stages for coordinated management
    PRE_INITIALIZATION = "pre_initialization"
    POST_INITIALIZATION = "post_initialization"
    STARTUP = "startup"
    RUNNING = "running"  # Alias for ACTIVE
    PRE_SHUTDOWN = "pre_shutdown"
    SHUTDOWN = "shutdown"  # Alias for STOPPING
    POST_SHUTDOWN = "post_shutdown"
