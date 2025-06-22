from typing import Any

from pydantic import BaseModel

from .._base import ComponentLayer, ComponentScope

class ComponentOptions(BaseModel):
    interface: type | None
    scope: ComponentScope
    layer: ComponentLayer | None
    context_name: str
    provider_name: str | None
    component_name: str | None
    tags: dict[str, str]
    auto_register: bool
    lazy_init: bool
    factory: Any

    def get_tags_dict(self) -> dict[str, str]: ...
    def get_provider_name(self, fallback_name: str) -> str: ...

class ContextOptions(BaseModel):
    providers: list[type] | None
    imports: list[Any] | None
    exports: list[type] | None
    auto_wire: bool
    context_name: str | None
    parent_context: str | None
    tags: dict[str, str]
    validation_enabled: bool
    lifecycle_hooks: bool

    def get_tags_dict(self) -> dict[str, str]: ...
    def get_providers_list(self) -> list[type]: ...
    def get_imports_list(self) -> list[Any]: ...
    def get_exports_list(self) -> list[type]: ...
