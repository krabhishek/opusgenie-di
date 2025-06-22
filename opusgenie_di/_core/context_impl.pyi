from typing import Any, TypeVar
from weakref import WeakSet

from .._base import ComponentScope
from .container_impl import Container
from .context_interface import ContextInterface

TInterface = TypeVar("TInterface")  # noqa: PYI001

class ImportDeclaration:
    component_type: type
    source_context: str
    name: str | None
    alias: str | None

    def __init__(
        self,
        component_type: type,
        source_context: str,
        name: str | None = None,
        alias: str | None = None,
    ) -> None: ...
    def get_provider_name(self) -> str: ...
    def get_import_key(self) -> str: ...

class ImportManager:
    _context: Context
    _imports: dict[str, ImportDeclaration]
    _source_contexts: dict[str, Context]

    def __init__(self, context: Context) -> None: ...
    def add_import(self, declaration: ImportDeclaration) -> None: ...
    def register_source_context(self, name: str, context: Context) -> None: ...
    def resolve_import(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface: ...
    async def resolve_import_async(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface: ...
    def can_resolve_import(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool: ...
    def clear_imports(self) -> None: ...
    def get_imports_summary(self) -> dict[str, Any]: ...

class Context(ContextInterface):
    name: str
    parent: Context | None
    auto_wire: bool
    _container: Container[Any]
    _import_manager: ImportManager
    _children: WeakSet[Context]
    _creation_time: float

    def __init__(
        self, name: str, parent: Context | None = None, auto_wire: bool = True
    ) -> None: ...
    def get_container(self, name: str | None = None) -> Container[Any]: ...
    def create_child_context(self, name: str) -> Context: ...
    def register_component(
        self,
        interface: type[TInterface],
        implementation: type[TInterface] | None = None,
        *,
        scope: ComponentScope = ...,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
    ) -> None: ...
    def resolve(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface: ...
    async def resolve_async(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface: ...
    def is_registered(
        self,
        interface: type[TInterface],
        name: str | None = None,
        include_imports: bool = True,
    ) -> bool: ...
    def add_import(self, declaration: ImportDeclaration) -> None: ...
    def register_source_context(self, context_name: str, context: Context) -> None: ...
    def get_summary(self) -> dict[str, Any]: ...
