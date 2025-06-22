"""Context module builder for creating contexts from module definitions."""

from typing import Any

from pydantic import BaseModel

from .._core import Context
from .._hooks import EventHook, emit_event
from .._registry import ModuleMetadata, get_global_registry
from .._utils import get_logger, log_error, run_async_in_sync

logger = get_logger(__name__)


class ContextModuleBuilder(BaseModel):
    """
    Builder for creating contexts from module definitions.

    Orchestrates the creation of multiple contexts from module classes,
    resolving dependencies and configuring cross-context imports.
    """

    model_config = {"arbitrary_types_allowed": True}

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
        try:
            # Import here to avoid circular imports
            from .._decorators.context_decorator import (
                get_module_metadata,
                is_context_module,
            )

            # Validate all module classes
            module_metadatas = []
            for module_class in module_classes:
                if not is_context_module(module_class):
                    raise ValueError(
                        f"Class {module_class.__name__} is not a context module. "
                        f"Use @og_context decorator to define modules."
                    )

                metadata = get_module_metadata(module_class)
                if metadata is None:
                    raise ValueError(
                        f"No metadata found for module {module_class.__name__}"
                    )

                module_metadatas.append(metadata)

            # Validate module dependencies
            registry = get_global_registry()
            validation_errors = registry.validate_module_dependencies()
            if validation_errors:
                raise ValueError(
                    f"Module dependency validation failed: {'; '.join(validation_errors)}"
                )

            # Determine build order based on dependencies
            build_order = self._determine_build_order(module_metadatas)

            # Build contexts in dependency order
            contexts: dict[str, Context] = {}
            for metadata in build_order:
                context = await self._build_single_context(metadata, contexts)
                contexts[metadata.name] = context

            # Emit module built event
            emit_event(
                EventHook.MODULE_BUILT,
                {
                    "module_count": len(contexts),
                    "context_names": list(contexts.keys()),
                    "build_order": [m.name for m in build_order],
                },
            )

            return contexts

        except Exception as e:
            log_error(
                "build_contexts",
                e,
            )
            raise RuntimeError(f"Failed to build contexts from modules: {e}") from e

    def build_contexts_sync(self, *module_classes: type[Any]) -> dict[str, Context]:
        """
        Synchronous version of build_contexts.

        Args:
            *module_classes: Module classes to build contexts for

        Returns:
            Dictionary mapping context names to created contexts
        """
        result: dict[str, Context] = run_async_in_sync(
            self.build_contexts(*module_classes)
        )
        return result

    async def _build_single_context(
        self, metadata: ModuleMetadata, existing_contexts: dict[str, Context]
    ) -> Context:
        """
        Build a single context from module metadata.

        Args:
            metadata: Module metadata to build context from
            existing_contexts: Already built contexts for import resolution

        Returns:
            Created context
        """
        try:
            # Create context
            context = Context(name=metadata.name)

            # Register providers in the context
            for provider_config in metadata.providers.get_active_providers():
                registration_args = provider_config.to_registration_args()
                context.register_component(**registration_args)

                logger.debug(
                    "Registered provider in context",
                    context=metadata.name,
                    interface=provider_config.interface.__name__,
                    implementation=provider_config.get_implementation().__name__,
                    scope=provider_config.scope.value,
                )

            # Configure imports from existing contexts
            await self._configure_context_imports(context, metadata, existing_contexts)

            # Enable auto-wiring after all components and imports are configured
            try:
                context.enable_auto_wiring()
                logger.debug(
                    "Enabled auto-wiring for context",
                    context_name=metadata.name,
                )
            except Exception as e:
                logger.warning(
                    "Failed to enable auto-wiring for context",
                    context_name=metadata.name,
                    error=str(e),
                )

            logger.debug(
                "Built context from module",
                context_name=metadata.name,
                provider_count=metadata.get_provider_count(),
                import_count=metadata.get_import_count(),
                export_count=metadata.get_export_count(),
            )

            return context

        except Exception as e:
            log_error(
                "build_single_context",
                e,
                context_name=metadata.name,
            )
            raise RuntimeError(
                f"Failed to build context for module {metadata.name}: {e}"
            ) from e

    async def _configure_context_imports(
        self,
        context: Context,
        metadata: ModuleMetadata,
        existing_contexts: dict[str, Context],
    ) -> None:
        """
        Configure imports for a context from existing contexts.

        Args:
            context: Context to configure imports for
            metadata: Module metadata containing import specifications
            existing_contexts: Map of existing contexts to import from
        """
        for module_import in metadata.imports.imports:
            source_context_name = module_import.from_context

            if source_context_name not in existing_contexts:
                if module_import.required:
                    raise ValueError(
                        f"Required source context '{source_context_name}' not available "
                        f"for import in module '{metadata.name}'"
                    )
                logger.warning(
                    "Optional source context not available, skipping import",
                    target_context=metadata.name,
                    source_context=source_context_name,
                    component=module_import.component_type.__name__,
                )
                continue

            source_context = existing_contexts[source_context_name]

            # Verify that the source context exports the component
            source_metadata = get_global_registry().get_module(source_context_name)
            if source_metadata and not source_metadata.exports_component(
                module_import.component_type
            ):
                if module_import.required:
                    raise ValueError(
                        f"Source context '{source_context_name}' does not export "
                        f"component '{module_import.component_type.__name__}' "
                        f"required by module '{metadata.name}'"
                    )
                logger.warning(
                    "Source context does not export component, skipping import",
                    target_context=metadata.name,
                    source_context=source_context_name,
                    component=module_import.component_type.__name__,
                )
                continue

            # Add import declaration to the context
            import_declaration = module_import.to_core_import_declaration()
            context.add_import(import_declaration)

            # Register the source context for import resolution
            context.register_source_context(source_context_name, source_context)

            logger.debug(
                "Configured context import",
                target_context=metadata.name,
                source_context=source_context_name,
                component=module_import.component_type.__name__,
                required=module_import.required,
            )

    def _determine_build_order(
        self, module_metadatas: list[ModuleMetadata]
    ) -> list[ModuleMetadata]:
        """
        Determine the build order for modules based on dependencies.

        Args:
            module_metadatas: List of module metadata

        Returns:
            List of module metadata in build order
        """
        # Create a mapping from module names to metadata
        metadata_map = {metadata.name: metadata for metadata in module_metadatas}

        # Use the registry to get the build order
        registry = get_global_registry()
        try:
            build_order_names = registry.get_build_order()
        except ValueError as e:
            raise ValueError(f"Cannot determine build order: {e}") from e

        # Filter to only include the modules we're building and maintain order
        ordered_metadatas = []
        for module_name in build_order_names:
            if module_name in metadata_map:
                ordered_metadatas.append(metadata_map[module_name])

        # Add any modules that weren't in the registry (shouldn't happen normally)
        for metadata in module_metadatas:
            if metadata not in ordered_metadatas:
                logger.warning(
                    "Module not found in build order, adding at end",
                    module_name=metadata.name,
                )
                ordered_metadatas.append(metadata)

        logger.debug(
            "Determined module build order",
            build_order=[m.name for m in ordered_metadatas],
        )

        return ordered_metadatas

    def validate_modules(self, *module_classes: type[Any]) -> list[str]:
        """
        Validate a set of module classes.

        Args:
            *module_classes: Module classes to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Import here to avoid circular imports
        from .._decorators.context_decorator import (
            get_module_metadata,
            is_context_module,
        )

        for module_class in module_classes:
            if not is_context_module(module_class):
                errors.append(
                    f"Class {module_class.__name__} is not decorated with @og_context"
                )
                continue

            metadata = get_module_metadata(module_class)
            if metadata is None:
                errors.append(f"No metadata found for module {module_class.__name__}")
                continue

            # Validate individual module
            module_errors = metadata.validate_module()
            for error in module_errors:
                errors.append(f"Module '{metadata.name}': {error}")

        # Validate cross-module dependencies
        registry = get_global_registry()
        dependency_errors = registry.validate_module_dependencies()
        errors.extend(dependency_errors)

        return errors

    def get_module_summary(self, *module_classes: type[Any]) -> dict[str, Any]:
        """
        Get a summary of modules and their relationships.

        Args:
            *module_classes: Module classes to summarize

        Returns:
            Dictionary containing module summary
        """
        summaries = []

        # Import here to avoid circular imports
        from .._decorators.context_decorator import (
            get_module_metadata,
            is_context_module,
        )

        for module_class in module_classes:
            if is_context_module(module_class):
                metadata = get_module_metadata(module_class)
                if metadata:
                    summaries.append(metadata.get_summary())

        registry = get_global_registry()

        return {
            "module_count": len(summaries),
            "modules": summaries,
            "dependency_graph": registry.get_dependency_graph(),
            "build_order": registry.get_build_order() if summaries else [],
            "validation_errors": self.validate_modules(*module_classes),
        }
