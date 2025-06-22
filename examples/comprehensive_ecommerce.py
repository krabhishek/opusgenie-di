#!/usr/bin/env python3
"""
Comprehensive E-commerce Example for OpusGenie DI

This example demonstrates a complete e-commerce application architecture using
all advanced features of OpusGenie DI including:

- Multi-layered architecture (Infrastructure, Domain, Application, API)
- Cross-context imports and dependencies
- Event hooks and lifecycle management
- Async operations and lifecycle
- Different component scopes (Singleton, Transient, Scoped)
- Error handling and validation
- Component metadata and tags
- Testing utilities integration
- Circular dependency detection demo
"""

import asyncio
from datetime import datetime
import logging
from typing import Any, Protocol
from uuid import uuid4

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    ContextModuleBuilder,
    EventHook,
    LifecycleHook,
    ModuleContextImport,
    og_component,
    og_context,
    register_hook,
    register_lifecycle_hook,
    reset_global_state,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DOMAIN MODELS AND PROTOCOLS
# ============================================================================


class Product:
    """Product domain model."""

    def __init__(self, id: str, name: str, price: float, stock: int):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.created_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "created_at": self.created_at.isoformat(),
        }


class Order:
    """Order domain model."""

    def __init__(self, id: str, user_id: str, items: list[dict[str, Any]]):
        self.id = id
        self.user_id = user_id
        self.items = items
        self.total: float = 0.0  # Will be set by the pricing service
        self.status = "pending"
        self.created_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


# Repository Protocols for type safety
class ProductRepository(Protocol):
    """Product repository protocol."""

    async def get_by_id(self, product_id: str) -> Product | None: ...
    async def get_all(self) -> list[Product]: ...
    async def create(self, product: Product) -> Product: ...
    async def update_stock(self, product_id: str, new_stock: int) -> bool: ...


class OrderRepository(Protocol):
    """Order repository protocol."""

    async def create(self, order: Order) -> Order: ...
    async def get_by_id(self, order_id: str) -> Order | None: ...
    async def get_by_user(self, user_id: str) -> list[Order]: ...
    async def update_status(self, order_id: str, status: str) -> bool: ...


# ============================================================================
# INFRASTRUCTURE LAYER COMPONENTS
# ============================================================================


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "infrastructure", "type": "database"},
)
class DatabaseConnection(BaseComponent):
    """Simulated database connection with async lifecycle."""

    def __init__(self) -> None:
        super().__init__()
        self.connected = False
        self.connection_pool_size = 10

    async def initialize(self) -> None:
        """Async initialization."""
        await super().initialize()
        logger.info("🔌 Connecting to database...")
        await asyncio.sleep(0.1)  # Simulate connection time
        self.connected = True
        logger.info("✅ Database connection established")

    async def cleanup(self) -> None:
        """Async cleanup."""
        logger.info("🔌 Closing database connection...")
        await asyncio.sleep(0.05)
        self.connected = False
        logger.info("✅ Database connection closed")
        await super().cleanup()

    async def execute_query(self, query: str) -> dict[str, Any]:
        """Execute a database query."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        logger.debug(f"📝 Executing query: {query}")
        await asyncio.sleep(0.01)  # Simulate query time
        return {"result": "success", "query": query}


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "infrastructure", "type": "cache"},
)
class CacheService(BaseComponent):
    """Redis-like cache service."""

    def __init__(self) -> None:
        super().__init__()
        self._cache: dict[str, Any] = {}

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        logger.debug(f"🔍 Cache GET: {key}")
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache."""
        logger.debug(f"💾 Cache SET: {key}")
        self._cache[key] = value

    async def delete(self, key: str) -> bool:
        """Delete from cache."""
        logger.debug(f"🗑️ Cache DELETE: {key}")
        return self._cache.pop(key, None) is not None


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "infrastructure", "type": "repository"},
)
class SqlProductRepository(BaseComponent):
    """SQL-based product repository implementation."""

    def __init__(self, db: DatabaseConnection, cache: CacheService) -> None:
        super().__init__()
        self.db = db
        self.cache = cache
        self._products: dict[str, Product] = {}

    async def initialize(self) -> None:
        """Initialize with sample data."""
        await super().initialize()
        # Create sample products
        sample_products = [
            Product("1", "Laptop", 999.99, 10),
            Product("2", "Mouse", 29.99, 50),
            Product("3", "Keyboard", 79.99, 25),
            Product("4", "Monitor", 299.99, 8),
        ]
        for product in sample_products:
            self._products[product.id] = product
        logger.info(
            f"📦 Initialized product repository with {len(sample_products)} products"
        )

    async def get_by_id(self, product_id: str) -> Product | None:
        """Get product by ID with caching."""
        cache_key = f"product:{product_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug(f"🎯 Cache hit for product {product_id}")
            # Create product from cached data, excluding created_at
            return Product(
                cached["id"], cached["name"], cached["price"], cached["stock"]
            )

        await self.db.execute_query(f"SELECT * FROM products WHERE id = '{product_id}'")
        product = self._products.get(product_id)
        if product:
            await self.cache.set(cache_key, product.to_dict())
        return product

    async def get_all(self) -> list[Product]:
        """Get all products."""
        await self.db.execute_query("SELECT * FROM products")
        return list(self._products.values())

    async def create(self, product: Product) -> Product:
        """Create new product."""
        await self.db.execute_query("INSERT INTO products VALUES (...)")
        self._products[product.id] = product
        return product

    async def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Update product stock."""
        await self.db.execute_query(
            f"UPDATE products SET stock = {new_stock} WHERE id = '{product_id}'"
        )
        if product_id in self._products:
            self._products[product_id].stock = new_stock
            # Invalidate cache
            await self.cache.delete(f"product:{product_id}")
            return True
        return False


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "infrastructure", "type": "repository"},
)
class SqlOrderRepository(BaseComponent):
    """SQL-based order repository implementation."""

    def __init__(self, db: DatabaseConnection) -> None:
        super().__init__()
        self.db = db
        self._orders: dict[str, Order] = {}

    async def create(self, order: Order) -> Order:
        """Create new order."""
        await self.db.execute_query("INSERT INTO orders VALUES (...)")
        self._orders[order.id] = order
        logger.info(f"📋 Created order {order.id} for user {order.user_id}")
        return order

    async def get_by_id(self, order_id: str) -> Order | None:
        """Get order by ID."""
        await self.db.execute_query(f"SELECT * FROM orders WHERE id = '{order_id}'")
        return self._orders.get(order_id)

    async def get_by_user(self, user_id: str) -> list[Order]:
        """Get orders by user ID."""
        await self.db.execute_query(f"SELECT * FROM orders WHERE user_id = '{user_id}'")
        return [order for order in self._orders.values() if order.user_id == user_id]

    async def update_status(self, order_id: str, status: str) -> bool:
        """Update order status."""
        await self.db.execute_query(
            f"UPDATE orders SET status = '{status}' WHERE id = '{order_id}'"
        )
        if order_id in self._orders:
            self._orders[order_id].status = status
            return True
        return False


# ============================================================================
# DOMAIN LAYER COMPONENTS
# ============================================================================


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "domain", "type": "service"},
)
class InventoryService(BaseComponent):
    """Domain service for inventory management."""

    def __init__(self, product_repo: SqlProductRepository) -> None:
        super().__init__()
        self.product_repo = product_repo

    async def check_availability(self, product_id: str, quantity: int) -> bool:
        """Check if product is available in requested quantity."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return False
        return product.stock >= quantity

    async def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve stock for an order."""
        product = await self.product_repo.get_by_id(product_id)
        if not product or product.stock < quantity:
            return False

        new_stock = product.stock - quantity
        return await self.product_repo.update_stock(product_id, new_stock)


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "domain", "type": "service"},
)
class PricingService(BaseComponent):
    """Domain service for pricing calculations."""

    def __init__(self, product_repo: SqlProductRepository) -> None:
        super().__init__()
        self.product_repo = product_repo

    async def calculate_order_total(self, items: list[dict[str, Any]]) -> float:
        """Calculate total price for order items."""
        total = 0.0
        for item in items:
            product = await self.product_repo.get_by_id(item["product_id"])
            if product:
                total += product.price * item["quantity"]
        return total

    async def apply_discounts(self, total: float, user_id: str) -> float:
        """Apply user-specific discounts."""
        # Simple discount logic
        if total > 500:
            total *= 0.9  # 10% discount for orders over $500
        return total


# ============================================================================
# APPLICATION LAYER COMPONENTS
# ============================================================================


@og_component(
    scope=ComponentScope.SCOPED,  # Request-scoped for better isolation
    auto_register=False,
    tags={"category": "application", "type": "service"},
)
class OrderService(BaseComponent):
    """Application service for order management."""

    def __init__(
        self,
        order_repo: SqlOrderRepository,
        inventory_service: InventoryService,
        pricing_service: PricingService,
        notification_service: "NotificationService",
    ) -> None:
        super().__init__()
        self.order_repo = order_repo
        self.inventory_service = inventory_service
        self.pricing_service = pricing_service
        self.notification_service = notification_service

    async def create_order(
        self, user_id: str, items: list[dict[str, Any]]
    ) -> Order | None:
        """Create a new order with validation."""
        logger.info(f"🛒 Creating order for user {user_id} with {len(items)} items")

        # Validate inventory
        for item in items:
            available = await self.inventory_service.check_availability(
                item["product_id"], item["quantity"]
            )
            if not available:
                logger.warning(
                    f"❌ Insufficient stock for product {item['product_id']}"
                )
                return None

        # Calculate pricing
        total = await self.pricing_service.calculate_order_total(items)
        total = await self.pricing_service.apply_discounts(total, user_id)

        # Create order
        order_id = str(uuid4())
        order = Order(order_id, user_id, items)
        order.total = total

        # Reserve inventory
        for item in items:
            await self.inventory_service.reserve_stock(
                item["product_id"], item["quantity"]
            )

        # Save order
        saved_order = await self.order_repo.create(order)

        # Send notification
        await self.notification_service.send_order_confirmation(saved_order)

        return saved_order

    async def get_user_orders(self, user_id: str) -> list[Order]:
        """Get all orders for a user."""
        return await self.order_repo.get_by_user(user_id)

    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status."""
        success = await self.order_repo.update_status(order_id, status)
        if success:
            order = await self.order_repo.get_by_id(order_id)
            if order:
                await self.notification_service.send_status_update(order, status)
        return success


@og_component(
    scope=ComponentScope.TRANSIENT,  # Transient for each notification
    auto_register=False,
    tags={"category": "application", "type": "service"},
)
class NotificationService(BaseComponent):
    """Service for sending notifications."""

    def __init__(self) -> None:
        super().__init__()
        self.instance_id = str(uuid4())[:8]

    async def send_order_confirmation(self, order: Order) -> None:
        """Send order confirmation notification."""
        message = f"Order {order.id} confirmed for ${order.total:.2f}"
        logger.info(f"📧 [{self.instance_id}] Sending confirmation: {message}")
        await asyncio.sleep(0.1)  # Simulate sending time

    async def send_status_update(self, order: Order, status: str) -> None:
        """Send order status update notification."""
        message = f"Order {order.id} status updated to: {status}"
        logger.info(f"📧 [{self.instance_id}] Sending update: {message}")
        await asyncio.sleep(0.1)


# ============================================================================
# API LAYER COMPONENTS
# ============================================================================


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "api", "type": "controller"},
)
class ProductController(BaseComponent):
    """API controller for product operations."""

    def __init__(self, product_repo: SqlProductRepository, cache: CacheService) -> None:
        super().__init__()
        self.product_repo = product_repo
        self.cache = cache

    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Get product by ID."""
        product = await self.product_repo.get_by_id(product_id)
        return product.to_dict() if product else None

    async def list_products(self) -> list[dict[str, Any]]:
        """List all products."""
        products = await self.product_repo.get_all()
        return [p.to_dict() for p in products]


@og_component(
    scope=ComponentScope.SINGLETON,
    auto_register=False,
    tags={"category": "api", "type": "controller"},
)
class OrderController(BaseComponent):
    """API controller for order operations."""

    def __init__(self, order_service: OrderService) -> None:
        super().__init__()
        self.order_service = order_service

    async def create_order(
        self, user_id: str, items: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Create a new order."""
        order = await self.order_service.create_order(user_id, items)
        return order.to_dict() if order else None

    async def get_user_orders(self, user_id: str) -> list[dict[str, Any]]:
        """Get orders for a user."""
        orders = await self.order_service.get_user_orders(user_id)
        return [o.to_dict() for o in orders]


# ============================================================================
# CONTEXT MODULE DEFINITIONS
# ============================================================================


@og_context(
    name="infrastructure_context",
    imports=[],
    exports=[
        DatabaseConnection,
        CacheService,
        SqlProductRepository,
        SqlOrderRepository,
    ],
    providers=[
        DatabaseConnection,
        CacheService,
        SqlProductRepository,
        SqlOrderRepository,
    ],
    description="Infrastructure layer with database, cache, and repositories",
    version="1.0.0",
)
class InfrastructureModule:
    """Infrastructure context module."""


@og_context(
    name="domain_context",
    imports=[
        ModuleContextImport(
            component_type=SqlProductRepository, from_context="infrastructure_context"
        ),
    ],
    exports=[InventoryService, PricingService],
    providers=[InventoryService, PricingService],
    description="Domain layer with business logic services",
    version="1.0.0",
)
class DomainModule:
    """Domain context module."""


@og_context(
    name="application_context",
    imports=[
        ModuleContextImport(
            component_type=SqlOrderRepository, from_context="infrastructure_context"
        ),
        ModuleContextImport(
            component_type=InventoryService, from_context="domain_context"
        ),
        ModuleContextImport(
            component_type=PricingService, from_context="domain_context"
        ),
    ],
    exports=[OrderService, NotificationService],
    providers=[OrderService, NotificationService],
    description="Application layer with use case services",
    version="1.0.0",
)
class ApplicationModule:
    """Application context module."""


@og_context(
    name="api_context",
    imports=[
        ModuleContextImport(
            component_type=SqlProductRepository, from_context="infrastructure_context"
        ),
        ModuleContextImport(
            component_type=CacheService, from_context="infrastructure_context"
        ),
        ModuleContextImport(
            component_type=OrderService, from_context="application_context"
        ),
    ],
    exports=[ProductController, OrderController],
    providers=[ProductController, OrderController],
    description="API layer with controllers",
    version="1.0.0",
)
class ApiModule:
    """API context module."""


# ============================================================================
# EVENT HOOKS AND LIFECYCLE MONITORING
# ============================================================================


def on_component_resolved(event_data: dict[str, Any]) -> None:
    """Hook for component resolution events."""
    component_type = event_data.get("component_type", "Unknown")
    context_name = event_data.get("context_name", "Unknown")
    if hasattr(component_type, "__name__"):
        logger.debug(
            f"🎯 Component resolved: {component_type.__name__} in {context_name}"
        )


def on_component_initialized(component: Any, event_data: dict[str, Any]) -> None:
    """Hook for component initialization."""
    component_name = type(component).__name__
    tags = getattr(component, "_og_metadata", {}).get("tags", {})
    logger.info(f"🚀 Component initialized: {component_name} (tags: {tags})")


def on_component_disposing(component: Any, event_data: dict[str, Any]) -> None:
    """Hook for component disposal."""
    component_name = type(component).__name__
    logger.info(f"🧹 Component disposing: {component_name}")


def on_component_error(component: Any, event_data: dict[str, Any]) -> None:
    """Hook for component lifecycle errors."""
    component_name = type(component).__name__
    error_message = event_data.get("error_message", "Unknown error")
    hook_type = event_data.get("lifecycle_hook", "unknown")
    logger.error(f"❌ Error in {component_name} during {hook_type}: {error_message}")


# Register hooks - this demonstrates the lifecycle monitoring capabilities
def register_monitoring_hooks() -> None:
    """Register all monitoring hooks for the application."""
    logger.info("📊 Registering lifecycle monitoring hooks...")

    # Register event hooks
    register_hook(EventHook.COMPONENT_RESOLVED, on_component_resolved)

    # Register lifecycle hooks for normal flow
    register_lifecycle_hook(
        LifecycleHook.AFTER_INITIALIZATION, on_component_initialized
    )
    register_lifecycle_hook(LifecycleHook.BEFORE_CLEANUP, on_component_disposing)

    # Register error handling hooks
    register_lifecycle_hook(LifecycleHook.INITIALIZATION_ERROR, on_component_error)
    register_lifecycle_hook(LifecycleHook.START_ERROR, on_component_error)
    register_lifecycle_hook(LifecycleHook.STOP_ERROR, on_component_error)
    register_lifecycle_hook(LifecycleHook.CLEANUP_ERROR, on_component_error)

    logger.info("✅ Lifecycle monitoring hooks registered successfully")


# ============================================================================
# CIRCULAR DEPENDENCY DEMONSTRATION
# ============================================================================


@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class CircularServiceA(BaseComponent):
    """Service A for circular dependency demo."""

    def __init__(self, service_b: "CircularServiceB") -> None:
        super().__init__()
        self.service_b = service_b


@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class CircularServiceB(BaseComponent):
    """Service B for circular dependency demo."""

    def __init__(self, service_a: CircularServiceA) -> None:
        super().__init__()
        self.service_a = service_a


async def demonstrate_circular_dependency() -> None:
    """Demonstrate circular dependency detection."""
    print("\n🔄 Demonstrating Circular Dependency Detection:")
    print("=" * 50)

    try:
        from opusgenie_di import Context

        context = Context("circular_demo")
        context.register_component(CircularServiceA, scope=ComponentScope.SINGLETON)
        context.register_component(CircularServiceB, scope=ComponentScope.SINGLETON)
        context.enable_auto_wiring()

        # This should trigger circular dependency detection
        _ = context.resolve(CircularServiceA)
        print("❌ Circular dependency not detected!")

    except Exception as e:
        if "circular" in str(e).lower():
            print(f"✅ Circular dependency correctly detected: {e}")
        else:
            print(f"❌ Unexpected error: {e}")


# ============================================================================
# TESTING UTILITIES DEMONSTRATION
# ============================================================================


async def demonstrate_testing_utilities() -> None:
    """Demonstrate testing utilities."""
    print("\n🧪 Demonstrating Testing Utilities:")
    print("=" * 40)

    from opusgenie_di import create_test_context

    # Create isolated test context
    test_context = create_test_context()

    # Create a mock database connection (since register_instance is not available)
    @og_component(auto_register=False)
    class MockDatabaseConnection(BaseComponent):
        async def execute_query(self, query: str) -> dict[str, Any]:
            return {"result": "mock_data", "query": query, "mock": True}

    # Test service that uses the mock
    @og_component(auto_register=False)
    class TestService(BaseComponent):
        def __init__(self, db: MockDatabaseConnection) -> None:
            super().__init__()
            self.db = db

        async def get_data(self) -> dict[str, Any]:
            return await self.db.execute_query("SELECT * FROM test")

    # Register mock and test service
    test_context.register_component(MockDatabaseConnection)
    test_context.register_component(TestService)
    test_context.enable_auto_wiring()

    service = test_context.resolve(TestService)
    result = await service.get_data()

    print(f"✅ Test service with mock DB: {result}")
    print("✅ Testing utilities work correctly!")


# ============================================================================
# MAIN APPLICATION
# ============================================================================


async def main() -> None:
    """Main application demonstrating comprehensive e-commerce system."""
    print("🛒 OpusGenie DI Comprehensive E-commerce Example")
    print("=" * 55)
    print("This example demonstrates:")
    print("• Multi-layered architecture (Infrastructure, Domain, Application, API)")
    print("• Cross-context imports and dependencies")
    print("• Event hooks and lifecycle management")
    print("• Async operations and lifecycle")
    print("• Different component scopes")
    print("• Error handling and validation")
    print("• Component metadata and tags")
    print("• Testing utilities")
    print("• Circular dependency detection")
    print("=" * 55)

    try:
        # Register monitoring hooks first
        register_monitoring_hooks()
        # Build contexts
        print("\n🏗️ Building Multi-Context Architecture...")
        builder = ContextModuleBuilder()
        contexts = await builder.build_contexts(
            InfrastructureModule,
            DomainModule,
            ApplicationModule,
            ApiModule,
        )

        print(f"✅ Built {len(contexts)} contexts successfully!")
        for name, context in contexts.items():
            summary = context.get_summary()
            print(f"  📦 {name}: {summary['component_count']} components")

        # Initialize infrastructure components that need async setup
        print("\n🔧 Initializing infrastructure components...")
        infra_context = contexts["infrastructure_context"]
        db_connection = infra_context.resolve(DatabaseConnection)
        await db_connection.initialize()

        # Initialize repositories that depend on the database
        product_repo = infra_context.resolve(SqlProductRepository)
        await product_repo.initialize()
        print("✅ Infrastructure initialization completed")

        # Get API controllers
        api_context = contexts["api_context"]
        product_controller = api_context.resolve(ProductController)
        order_controller = api_context.resolve(OrderController)

        # Demonstrate product operations
        print("\n📦 Testing Product Operations:")
        products = await product_controller.list_products()
        print(f"Available products: {len(products)}")
        for product in products[:2]:  # Show first 2
            print(
                f"  • {product['name']}: ${product['price']} (stock: {product['stock']})"
            )

        # Demonstrate order creation
        print("\n🛒 Testing Order Creation:")
        order_items = [
            {"product_id": "1", "quantity": 2},
            {"product_id": "2", "quantity": 3},
        ]

        order_result = await order_controller.create_order("user123", order_items)
        if order_result:
            print("✅ Order created successfully:")
            print(f"  Order ID: {order_result['id']}")
            print(f"  Total: ${order_result['total']:.2f}")
            print(f"  Status: {order_result['status']}")
        else:
            print("❌ Order creation failed")

        # Demonstrate user orders
        print("\n📋 Testing User Order History:")
        user_orders = await order_controller.get_user_orders("user123")
        print(f"User has {len(user_orders)} orders")

        # Test different scopes
        print("\n🔄 Testing Component Scopes:")
        app_context = contexts["application_context"]

        # Test singleton behavior
        order_service1 = app_context.resolve(OrderService)
        order_service2 = app_context.resolve(OrderService)
        print(
            f"OrderService (Scoped) - Same instance? {order_service1 is order_service2}"
        )

        # Test transient behavior
        notif1 = app_context.resolve(NotificationService)
        notif2 = app_context.resolve(NotificationService)
        print(
            f"NotificationService (Transient) - Different instances? {notif1 is not notif2}"
        )
        print(f"  Instance 1 ID: {notif1.instance_id}")
        print(f"  Instance 2 ID: {notif2.instance_id}")

        # Show context summaries
        print("\n📊 Context Summaries:")
        for context_name, context in contexts.items():
            summary = context.get_summary()
            print(f"\n{context_name}:")
            print(f"  Components: {summary['component_count']}")
            print(f"  Imports: {summary['import_count']}")
            print(
                f"  Types: {', '.join(t.__name__ for t in summary['registered_types'])}"
            )

        # Demonstrate circular dependency detection
        await demonstrate_circular_dependency()

        # Demonstrate testing utilities
        await demonstrate_testing_utilities()

        print("\n✅ Comprehensive e-commerce example completed successfully!")
        print("🎉 All OpusGenie DI features demonstrated!")

    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        raise
    finally:
        # Cleanup - this will trigger cleanup for all components
        print("\n🧹 Cleaning up resources...")
        for context in contexts.values():
            context.shutdown()
        print("✅ Cleanup completed")


def main_sync() -> None:
    """Synchronous wrapper for main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
    finally:
        # Reset global state for clean exit
        reset_global_state()


if __name__ == "__main__":
    main_sync()
