from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from .._base import ComponentScope

T = TypeVar("T")  # noqa: PYI001

class ScopeManagerInterface(ABC):
    @abstractmethod
    def get_or_create(
        self,
        key: str,
        factory: Callable[[], T],
        scope: ComponentScope,
    ) -> T: ...
    @abstractmethod
    async def get_or_create_async(
        self,
        key: str,
        factory: Callable[[], Coroutine[Any, Any, T]],
        scope: ComponentScope,
    ) -> T: ...
    @abstractmethod
    def create_scope(self, scope_name: str | None = None) -> str: ...
    @abstractmethod
    def dispose_scope(self, scope_name: str) -> None: ...
    @abstractmethod
    def clear_all_scopes(self) -> None: ...
