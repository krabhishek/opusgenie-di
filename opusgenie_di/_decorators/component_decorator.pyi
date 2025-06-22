from collections.abc import Callable
from typing import Any, TypeVar

from .._base import ComponentLayer, ComponentMetadata, ComponentScope
from .decorator_options import ComponentOptions

T = TypeVar("T")  # noqa: PYI001

def og_component(
    interface: type | None = None,
    *,
    scope: ComponentScope = ...,
    layer: ComponentLayer | None = None,
    context_name: str = "global",
    component_name: str | None = None,
    provider_name: str | None = None,
    tags: dict[str, Any] | None = None,
    auto_register: bool = True,
    lazy_init: bool = False,
    factory: Any = None,
) -> Callable[[type[T]], type[T]]: ...
def get_component_options(cls: type) -> ComponentOptions | None: ...
def get_component_metadata(cls: type) -> ComponentMetadata | None: ...
def get_enhanced_tags(cls: type) -> dict[str, str]: ...
def is_og_component(cls: type) -> bool: ...
def register_component_manually(
    cls: type,
    context_name: str = "global",
    override_options: ComponentOptions | None = None,
) -> None: ...
