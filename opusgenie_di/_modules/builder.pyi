from typing import Any

from pydantic import BaseModel

from .._core import Context
from .._registry import ModuleMetadata

class ContextModuleBuilder(BaseModel):
    async def build_contexts(
        self, *module_classes: type[Any]
    ) -> dict[str, Context]: ...
    def build_contexts_sync(self, *module_classes: type[Any]) -> dict[str, Context]: ...
    def _determine_build_order(
        self, metadatas: list[ModuleMetadata]
    ) -> list[ModuleMetadata]: ...
    async def _build_single_context(
        self, metadata: ModuleMetadata, existing_contexts: dict[str, Context]
    ) -> Context: ...
    def _topological_sort(self, dependencies: dict[str, list[str]]) -> list[str]: ...
    def _has_circular_dependency(self, dependencies: dict[str, list[str]]) -> bool: ...
