#!/usr/bin/env python3
"""Basic usage example for opusgenie-di package."""

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    get_global_context,
    og_component,
)


# Define a simple component
@og_component(scope=ComponentScope.SINGLETON)
class DatabaseService(BaseComponent):
    """Simple database service."""

    def __init__(self) -> None:
        super().__init__()

    def get_data(self) -> str:
        """Get data from database."""
        return "Data from database"


# Define a component with dependencies
@og_component(scope=ComponentScope.SINGLETON)
class UserService(BaseComponent):
    """User service with database dependency."""

    def __init__(self, db_service: DatabaseService) -> None:
        super().__init__()
        # Natural assignment - no more __dict__ manipulation!
        self.db_service = db_service

    def get_user(self, user_id: str) -> dict[str, str]:
        """Get a user."""
        data = self.db_service.get_data()
        return {"id": user_id, "name": f"User_{user_id}", "source": data}


# Define a transient component
@og_component(scope=ComponentScope.TRANSIENT)
class NotificationService(BaseComponent):
    """Transient notification service."""

    def __init__(self) -> None:
        super().__init__()

    def send_notification(self, message: str) -> str:
        """Send a notification."""
        return f"Notification sent: {message} (instance: {id(self)})"


def main() -> None:
    """Main function demonstrating basic usage."""
    print("🚀 OpusGenie DI Basic Usage Example")
    print("=" * 40)

    # Get the global context
    context = get_global_context()

    # Enable auto-wiring for automatic dependency injection
    context.enable_auto_wiring()

    # Test singleton components
    print("\n📦 Testing Singleton Components:")
    db1 = context.resolve(DatabaseService)
    db2 = context.resolve(DatabaseService)
    print(f"DatabaseService 1: {db1.get_data()}")
    print(f"DatabaseService 2: {db2.get_data()}")
    print(f"Same instance? {db1 is db2}")

    # Test dependency injection
    print("\n🔗 Testing Dependency Injection:")
    user_service = context.resolve(UserService)
    user_data = user_service.get_user("123")
    print(f"User data: {user_data}")

    # Test transient components
    print("\n🔄 Testing Transient Components:")
    notif1 = context.resolve(NotificationService)
    notif2 = context.resolve(NotificationService)
    result1 = notif1.send_notification("Hello")
    result2 = notif2.send_notification("World")
    print(f"Notification 1: {result1}")
    print(f"Notification 2: {result2}")
    print(f"Different instances? {notif1 is not notif2}")

    # Show context summary
    print("\n📊 Context Summary:")
    summary = context.get_summary()
    print(f"Context: {summary['name']}")
    print(f"Components: {summary['component_count']}")
    print(f"Registered types: {summary['registered_types']}")

    print("\n✅ Basic usage example completed successfully!")


if __name__ == "__main__":
    main()
