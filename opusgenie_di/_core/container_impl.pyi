from threading import RLock
from typing import Any, TypeVar

from .._base import ComponentMetadata, ComponentScope
from .._base.protocols import ComponentMetadataProtocol, ComponentProviderProtocol
from .container_interface import ContainerInterface
from .scope_impl import ScopeManager

T = TypeVar("T")  # noqa: PYI001
TInterface = TypeVar("TInterface")  # noqa: PYI001
TImplementation = TypeVar("TImplementation")  # noqa: PYI001

def _get_resolution_chain() -> list[str]: ...
def _push_resolution(component_name: str) -> None: ...
def _pop_resolution() -> str | None: ...
def _clear_resolution_chain() -> None: ...

class Container(ContainerInterface[T]):
    name: str
    _providers: dict[str, Any]
    _metadata: dict[str, ComponentMetadata]
    _scope_manager: ScopeManager
    _lock: RLock
    _creation_time: float

    def __init__(self, name: str = "default") -> None: ...
    def register(
        self,
        interface: type[TInterface],
        implementation: type[TImplementation] | None = None,
        *,
        scope: ComponentScope = ...,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
        factory: Any = None,
    ) -> None: ...
    def register_provider(
        self,
        interface: type[TInterface],
        provider: ComponentProviderProtocol[TInterface],
        *,
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
        self, interface: type[TInterface], name: str | None = None
    ) -> bool: ...
    def get_metadata(
        self, interface: type[TInterface], name: str | None = None
    ) -> ComponentMetadataProtocol: ...
    def unregister(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool: ...
    def clear(self) -> None: ...
    def get_registered_types(self) -> list[type]: ...
    def get_registration_count(self) -> int: ...
    def _get_provider_key(self, interface: type, name: str | None = None) -> str: ...
    def _create_provider(
        self,
        implementation: type[TImplementation],
        scope: ComponentScope,
        factory: Any = None,
    ) -> Any: ...
    def _validate_registration(
        self,
        interface: type[TInterface],
        implementation: type[TImplementation] | None,
    ) -> None: ...
