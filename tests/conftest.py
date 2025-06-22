"""Pytest configuration and shared fixtures for opusgenie_di tests."""

from collections.abc import Generator

import pytest

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    Context,
    MockComponent,
    TestEventCollector,
    create_test_context,
    og_component,
    reset_global_state,
)


@pytest.fixture(autouse=True)
def reset_di_state() -> Generator[None, None, None]:
    """Automatically reset DI state before each test."""
    reset_global_state()
    yield
    reset_global_state()


@pytest.fixture
def test_context() -> Context:
    """Create a test context with mock components."""
    return create_test_context("test_context")


@pytest.fixture
def empty_context() -> Context:
    """Create an empty test context."""
    return Context(name="empty_test_context")


@pytest.fixture
def mock_component() -> MockComponent:
    """Create a mock component instance."""
    return MockComponent(value="test")


@pytest.fixture
def mock_singleton() -> MockComponent:
    """Create a mock singleton component instance."""
    return MockComponent(value="singleton")


@pytest.fixture
def mock_transient() -> MockComponent:
    """Create a mock transient component instance."""
    return MockComponent(value="transient")


@pytest.fixture
def event_collector() -> TestEventCollector:
    """Create a test event collector."""
    return TestEventCollector()


@pytest.fixture
def sample_components() -> dict[str, type]:
    """Create sample components for testing."""

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class SampleService(BaseComponent):
        def __init__(self) -> None:
            super().__init__()
            self.value = "sample"

        def get_value(self) -> str:
            return self.value

    @og_component(scope=ComponentScope.TRANSIENT, auto_register=False)
    class SampleRepository(BaseComponent):
        def __init__(self) -> None:
            super().__init__()
            self.created_at = id(self)

        def get_id(self) -> int:
            return self.created_at

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class SampleController(BaseComponent):
        def __init__(self, service: SampleService, repo: SampleRepository) -> None:
            super().__init__()
            self.service = service
            self.repo = repo

        def process(self) -> dict[str, str | int]:
            return {
                "service_value": self.service.get_value(),
                "repo_id": self.repo.get_id(),
            }

    return {
        "service": SampleService,
        "repository": SampleRepository,
        "controller": SampleController,
    }


@pytest.fixture
def complex_dependency_chain() -> dict[str, type]:
    """Create a complex dependency chain for testing."""

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class DatabaseConfig(BaseComponent):
        def __init__(self) -> None:
            super().__init__()
            self.connection_string = "test://localhost"

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class DatabaseConnection(BaseComponent):
        def __init__(self, config: DatabaseConfig) -> None:
            super().__init__()
            self.config = config
            self.is_connected = True

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class UserRepository(BaseComponent):
        def __init__(self, db: DatabaseConnection) -> None:
            super().__init__()
            self.db = db

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class UserService(BaseComponent):
        def __init__(self, repo: UserRepository) -> None:
            super().__init__()
            self.repo = repo

    @og_component(scope=ComponentScope.SINGLETON, auto_register=False)
    class UserController(BaseComponent):
        def __init__(self, service: UserService, config: DatabaseConfig) -> None:
            super().__init__()
            self.service = service
            self.config = config

    return {
        "config": DatabaseConfig,
        "connection": DatabaseConnection,
        "repository": UserRepository,
        "service": UserService,
        "controller": UserController,
    }
