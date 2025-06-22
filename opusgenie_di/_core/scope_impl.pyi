from collections.abc import Callable, Coroutine, Generator
from contextvars import ContextVar
from threading import RLock
from typing import Any, TypeVar
from weakref import WeakValueDictionary

from .._base import ComponentScope
from .scope_interface import ScopeManagerInterface

T = TypeVar("T")  # noqa: PYI001

_current_scope: ContextVar[str | None]

class ScopeManager(ScopeManagerInterface):
    _lock: RLock
    _singletons: dict[str, Any]
    _scoped_instances: dict[str, dict[str, Any]]
    _disposable_instances: WeakValueDictionary[int, Any]
    _lifecycle_callback: Callable[..., None] | None

    def __init__(
        self, lifecycle_callback: Callable[..., None] | None = None
    ) -> None: ...
    def get_or_create(
        self,
        key: str,
        factory: Callable[[], T],
        scope: ComponentScope,
    ) -> T: ...
    async def get_or_create_async(
        self,
        key: str,
        factory: Callable[[], Coroutine[Any, Any, T]],
        scope: ComponentScope,
    ) -> T: ...
    def create_scope(self, scope_name: str | None = None) -> str: ...
    def dispose_scope(self, scope_name: str) -> None: ...
    def clear_all_scopes(self) -> None: ...
    def get_current_scope(self) -> str | None: ...
    def scoped_context(
        self, scope_name: str | None = None
    ) -> Generator[str, None, None]: ...
    def _handle_singleton(self, key: str, factory: Callable[[], T]) -> T: ...
    def _handle_scoped(
        self, key: str, factory: Callable[[], T], scope_name: str
    ) -> T: ...
    def _handle_transient(self, factory: Callable[[], T]) -> T: ...
    def _cleanup_instance(self, instance: Any) -> None: ...
