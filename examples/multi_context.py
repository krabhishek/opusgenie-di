#!/usr/bin/env python3
"""Multi-context example for opusgenie-di package."""

import asyncio

from opusgenie_di import (
    BaseComponent,
    ComponentScope,
    ContextModuleBuilder,
    ModuleContextImport,
    og_component,
    og_context,
)


# Infrastructure layer components
@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class DatabaseRepository(BaseComponent):
    """Database repository."""

    def __init__(self) -> None:
        super().__init__()

    def get_data(self) -> str:
        """Get data from database."""
        return "Data from database"


@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class CacheRepository(BaseComponent):
    """Cache repository."""

    def __init__(self) -> None:
        super().__init__()

    def get_cached_data(self) -> str:
        """Get cached data."""
        return "Cached data"


# Application layer components
@og_component(scope=ComponentScope.SINGLETON, auto_register=False)
class BusinessService(BaseComponent):
    """Business service with dependencies."""

    def __init__(
        self,
        db_repo: DatabaseRepository,
        cache_repo: CacheRepository,
    ) -> None:
        super().__init__()
        # Natural assignment - much cleaner!
        self.db_repo = db_repo
        self.cache_repo = cache_repo

    def process_data(self) -> dict[str, str]:
        """Process business data."""
        return {
            "status": "processed",
            "db_data": self.db_repo.get_data(),
            "cache_data": self.cache_repo.get_cached_data(),
        }


# Define module contexts
@og_context(
    name="infrastructure_context",
    imports=[],  # Base layer - no imports
    exports=[DatabaseRepository, CacheRepository],
    providers=[DatabaseRepository, CacheRepository],
    description="Infrastructure layer with repositories",
    version="1.0.0",
)
class InfrastructureModule:
    """Infrastructure context module."""


@og_context(
    name="business_context",
    imports=[
        ModuleContextImport(
            component_type=DatabaseRepository, from_context="infrastructure_context"
        ),
        ModuleContextImport(
            component_type=CacheRepository, from_context="infrastructure_context"
        ),
    ],
    exports=[BusinessService],
    providers=[BusinessService],
    description="Business logic layer",
    version="1.0.0",
)
class BusinessModule:
    """Business context module."""


async def main() -> None:
    """Main function demonstrating multi-context usage."""
    print("🚀 OpusGenie DI Multi-Context Example")
    print("=" * 40)

    # Create module builder
    builder = ContextModuleBuilder()

    # Build contexts from module definitions
    print("\n🏗️ Building contexts from modules...")
    contexts = await builder.build_contexts(InfrastructureModule, BusinessModule)

    print(f"✅ Built {len(contexts)} contexts:")
    for context_name, context in contexts.items():
        summary = context.get_summary()
        print(f"  📦 {context_name}: {summary['component_count']} components")

    # Test infrastructure context
    print("\n🏗️ Testing Infrastructure Context:")
    infra_context = contexts["infrastructure_context"]
    db_repo = infra_context.resolve(DatabaseRepository)
    cache_repo = infra_context.resolve(CacheRepository)
    print(f"Database data: {db_repo.get_data()}")
    print(f"Cache data: {cache_repo.get_cached_data()}")

    # Test business context with cross-context dependencies
    print("\n💼 Testing Business Context with Cross-Context Dependencies:")
    business_context = contexts["business_context"]
    business_service = business_context.resolve(BusinessService)
    processed_data = business_service.process_data()
    print(f"Processed data: {processed_data}")

    # Test context isolation
    print("\n🚧 Testing Context Isolation:")
    try:
        # Try to resolve BusinessService from infrastructure context (should fail)
        infra_context.resolve(BusinessService)
        print(
            "❌ Context isolation failed - BusinessService found in infrastructure context"
        )
    except Exception:
        print(
            "✅ Context isolation working - BusinessService not available in infrastructure context"
        )

    try:
        # Try to resolve DatabaseRepository from business context directly (should work via import)
        business_db = business_context.resolve(DatabaseRepository)
        print(
            f"✅ Cross-context import working - resolved DatabaseRepository: {business_db.get_data()}"
        )
    except Exception as e:
        print(f"❌ Cross-context import failed: {e}")

    # Show context summaries
    print("\n📊 Context Summaries:")
    for context_name, context in contexts.items():
        summary = context.get_summary()
        print(f"\n{context_name}:")
        print(f"  Components: {summary['component_count']}")
        print(f"  Imports: {summary['import_count']}")
        print(f"  Types: {summary['registered_types']}")

    print("\n✅ Multi-context example completed successfully!")


def main_sync() -> None:
    """Synchronous wrapper for main function."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
