from abc import ABC, abstractmethod
from typing import Any, TypeVar

from .._base import ComponentScope
from .container_interface import ContainerInterface

TInterface = TypeVar("TInterface")  # noqa: PYI001

class ContextInterface(ABC):
    @abstractmethod
    def get_container(
        self, name: str | None = None
    ) -> ContainerInterface[TInterface]: ...
    @abstractmethod
    def create_child_context(self, name: str) -> ContextInterface: ...
    @abstractmethod
    def register_component(
        self,
        interface: type[TInterface],
        implementation: type[TInterface] | None = None,
        *,
        scope: ComponentScope = ...,
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
    def get_summary(self) -> dict[str, Any]: ...
