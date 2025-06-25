import structlog
from _typeshed import Incomplete
from typing import Any

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for the given name."""

logger: Incomplete

def log_component_registration(component_type: type, context_name: str, scope: str, provider_name: str | None = None, **extra: Any) -> None:
    """Log component registration with structured data."""
def log_component_resolution(component_type: type, context_name: str, resolution_time_ms: float, resolution_source: str = 'direct', **extra: Any) -> None:
    """Log component resolution with timing information."""
def log_context_creation(context_name: str, parent_context: str | None = None, **extra: Any) -> None:
    """Log context creation."""
def log_module_registration(module_name: str, imports_count: int, exports_count: int, providers_count: int, **extra: Any) -> None:
    """Log module registration with counts."""
def log_import_resolution(component_type: type, source_context: str, target_context: str, **extra: Any) -> None:
    """Log cross-context import resolution."""
def log_error(operation: str, error: Exception, context_name: str | None = None, component_type: type | None = None, **extra: Any) -> None:
    """Log errors with context information."""
def log_warning(message: str, context_name: str | None = None, component_type: type | None = None, **extra: Any) -> None:
    """Log warnings with context information."""
def log_info(message: str, context_name: str | None = None, **extra: Any) -> None:
    """Log informational messages."""
