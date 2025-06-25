from .._core import Context as Context
from .._hooks import EventHook as EventHook, emit_event as emit_event
from .._registry import ModuleMetadata as ModuleMetadata, get_global_registry as get_global_registry
from .._utils import get_logger as get_logger, log_error as log_error, run_async_in_sync as run_async_in_sync
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class ContextModuleBuilder(BaseModel):
    """
    Builder for creating contexts from module definitions.

    Orchestrates the creation of multiple contexts from module classes,
    resolving dependencies and configuring cross-context imports.
    """
    model_config: Incomplete
    async def build_contexts(self, *module_classes: type[Any]) -> dict[str, Context]:
        """
        Build contexts from module class definitions.

        Args:
            *module_classes: Module classes to build contexts for

        Returns:
            Dictionary mapping context names to created contexts

        Raises:
            ValueError: If module validation fails
            RuntimeError: If context creation fails
        """
    def build_contexts_sync(self, *module_classes: type[Any]) -> dict[str, Context]:
        """
        Synchronous version of build_contexts.

        Args:
            *module_classes: Module classes to build contexts for

        Returns:
            Dictionary mapping context names to created contexts
        """
    async def _build_single_context(self, metadata: ModuleMetadata, existing_contexts: dict[str, Context]) -> Context:
        """
        Build a single context from module metadata.

        Args:
            metadata: Module metadata to build context from
            existing_contexts: Already built contexts for import resolution

        Returns:
            Created context
        """
    async def _configure_context_imports(self, context: Context, metadata: ModuleMetadata, existing_contexts: dict[str, Context]) -> None:
        """
        Configure imports for a context from existing contexts.

        Args:
            context: Context to configure imports for
            metadata: Module metadata containing import specifications
            existing_contexts: Map of existing contexts to import from
        """
    def _determine_build_order(self, module_metadatas: list[ModuleMetadata]) -> list[ModuleMetadata]:
        """
        Determine the build order for modules based on dependencies.

        Args:
            module_metadatas: List of module metadata

        Returns:
            List of module metadata in build order
        """
    def validate_modules(self, *module_classes: type[Any]) -> list[str]:
        """
        Validate a set of module classes.

        Args:
            *module_classes: Module classes to validate

        Returns:
            List of validation error messages
        """
    def get_module_summary(self, *module_classes: type[Any]) -> dict[str, Any]:
        """
        Get a summary of modules and their relationships.

        Args:
            *module_classes: Module classes to summarize

        Returns:
            Dictionary containing module summary
        """
