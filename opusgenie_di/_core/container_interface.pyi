from abc import ABC, abstractmethod
from typing import Any, TypeVar

from .._base import ComponentMetadataProtocol, ComponentProviderProtocol, ComponentScope

T = TypeVar("T")  # noqa: PYI001
TInterface = TypeVar("TInterface")  # noqa: PYI001
TImplementation = TypeVar("TImplementation")  # noqa: PYI001

class ContainerInterface[T](ABC):
    @abstractmethod
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
    @abstractmethod
    def register_provider(
        self,
        interface: type[TInterface],
        provider: ComponentProviderProtocol[TInterface],
        *,
        name: str | None = None,
        tags: dict[str, Any] | None = None,
    ) -> None: ...
    @abstractmethod
    def resolve(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface: ...
    @abstractmethod
    async def resolve_async(
        self, interface: type[TInterface], name: str | None = None
    ) -> TInterface: ...
    @abstractmethod
    def is_registered(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool: ...
    @abstractmethod
    def get_metadata(
        self, interface: type[TInterface], name: str | None = None
    ) -> ComponentMetadataProtocol: ...
    @abstractmethod
    def unregister(
        self, interface: type[TInterface], name: str | None = None
    ) -> bool: ...
    @abstractmethod
    def clear(self) -> None: ...
    @abstractmethod
    def get_registered_types(self) -> list[type]: ...
    @abstractmethod
    def get_registration_count(self) -> int: ...
