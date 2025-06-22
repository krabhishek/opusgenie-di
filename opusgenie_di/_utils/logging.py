"""Structured logging utilities for the dependency injection system."""

from typing import Any

import structlog

# Configure structured logging for the DI system
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(30),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for the given name."""
    return structlog.get_logger(name)  # type: ignore[no-any-return]


# Create module-level logger
logger = get_logger("opusgenie_di")


def log_component_registration(
    component_type: type,
    context_name: str,
    scope: str,
    provider_name: str | None = None,
    **extra: Any,
) -> None:
    """Log component registration with structured data."""
    logger.debug(
        "Component registered",
        component=component_type.__name__,
        context=context_name,
        scope=scope,
        provider=provider_name,
        module=component_type.__module__,
        **extra,
    )


def log_component_resolution(
    component_type: type,
    context_name: str,
    resolution_time_ms: float,
    resolution_source: str = "direct",
    **extra: Any,
) -> None:
    """Log component resolution with timing information."""
    logger.debug(
        "Component resolved",
        component=component_type.__name__,
        context=context_name,
        resolution_time_ms=resolution_time_ms,
        resolution_source=resolution_source,
        **extra,
    )


def log_context_creation(
    context_name: str,
    parent_context: str | None = None,
    **extra: Any,
) -> None:
    """Log context creation."""
    logger.debug(
        "Context created",
        context=context_name,
        parent=parent_context,
        **extra,
    )


def log_module_registration(
    module_name: str,
    imports_count: int,
    exports_count: int,
    providers_count: int,
    **extra: Any,
) -> None:
    """Log module registration with counts."""
    logger.debug(
        "Module registered",
        module=module_name,
        imports=imports_count,
        exports=exports_count,
        providers=providers_count,
        **extra,
    )


def log_import_resolution(
    component_type: type,
    source_context: str,
    target_context: str,
    **extra: Any,
) -> None:
    """Log cross-context import resolution."""
    logger.debug(
        "Import resolved",
        component=component_type.__name__,
        source_context=source_context,
        target_context=target_context,
        **extra,
    )


def log_error(
    operation: str,
    error: Exception,
    context_name: str | None = None,
    component_type: type | None = None,
    **extra: Any,
) -> None:
    """Log errors with context information."""
    logger.error(
        "DI operation failed",
        operation=operation,
        error=str(error),
        error_type=type(error).__name__,
        context=context_name,
        component=component_type.__name__ if component_type else None,
        **extra,
    )


def log_warning(
    message: str,
    context_name: str | None = None,
    component_type: type | None = None,
    **extra: Any,
) -> None:
    """Log warnings with context information."""
    logger.warning(
        message,
        context=context_name,
        component=component_type.__name__ if component_type else None,
        **extra,
    )


def log_info(
    message: str,
    context_name: str | None = None,
    **extra: Any,
) -> None:
    """Log informational messages."""
    logger.info(
        message,
        context=context_name,
        **extra,
    )
