from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from .._modules.import_declaration import ModuleContextImport
from .._registry import ModuleMetadata
from .decorator_options import ContextOptions

T = TypeVar("T")  # noqa: PYI001

def og_context(
    name: str | None = None,
    imports: Sequence[ModuleContextImport] | None = None,
    exports: Sequence[type] | None = None,
    providers: Sequence[Any] | None = None,
    description: str | None = None,
    version: str = "1.0.0",
    tags: dict[str, Any] | None = None,
) -> Callable[[type[T]], type[T]]: ...
def get_module_metadata(cls: type) -> ModuleMetadata | None: ...
def get_module_options(cls: type) -> ContextOptions | None: ...
def is_context_module(cls: type) -> bool: ...
def get_all_context_modules() -> list[type]: ...
def validate_all_module_dependencies() -> dict[str, list[str]]: ...
