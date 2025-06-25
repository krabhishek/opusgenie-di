from enum import Enum

class ComponentScope(Enum):
    """
    Enumeration of component lifecycle scopes.

    Defines how component instances are managed throughout their lifecycle.
    """
    SINGLETON = 'singleton'
    TRANSIENT = 'transient'
    SCOPED = 'scoped'
    FACTORY = 'factory'
    CONDITIONAL = 'conditional'

class ComponentLayer(Enum):
    """
    Enumeration of architectural layers for component organization.

    Helps organize components by their architectural responsibilities.
    """
    INFRASTRUCTURE = 'infrastructure'
    APPLICATION = 'application'
    DOMAIN = 'domain'
    FRAMEWORK = 'framework'
    PRESENTATION = 'presentation'

class RegistrationStrategy(Enum):
    """
    Enumeration of component registration strategies.

    Defines how components are registered and created.
    """
    AUTO = 'auto'
    MANUAL = 'manual'
    LAZY = 'lazy'

class LifecycleStage(Enum):
    """
    Enumeration of component lifecycle stages.

    Tracks the current state of a component through its lifecycle.
    """
    CREATED = 'created'
    INITIALIZING = 'initializing'
    INITIALIZED = 'initialized'
    ACTIVE = 'active'
    STOPPING = 'stopping'
    STOPPED = 'stopped'
    DISPOSING = 'disposing'
    DISPOSED = 'disposed'
    ERROR = 'error'
    PRE_INITIALIZATION = 'pre_initialization'
    POST_INITIALIZATION = 'post_initialization'
    STARTUP = 'startup'
    RUNNING = 'running'
    SHUTDOWN = 'shutdown'
    POST_SHUTDOWN = 'post_shutdown'
