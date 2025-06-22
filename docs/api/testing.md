# Testing API Reference

*Complete reference for testing utilities and patterns with OpusGenie DI*

---

## Test Fixtures

### Context Testing Utilities

Utilities for creating isolated test contexts and managing test state.

```python title="Test Context Utilities"
from opusgenie_di._testing.fixtures import (
    create_test_context,
    create_isolated_context,
    reset_global_state,
    TestComponentFactory
)

def create_test_context(name: str = "test") -> ContextInterface:
    """
    Create an isolated test context.
    
    Args:
        name: Optional name for the test context
        
    Returns:
        Clean context instance for testing
    """

def create_isolated_context(*components: Type) -> ContextInterface:
    """
    Create context with only specified components.
    
    Args:
        components: Component types to include in context
        
    Returns:
        Context containing only the specified components
    """

def reset_global_state() -> None:
    """
    Reset global OpusGenie DI state for test isolation.
    Should be called in test setup/teardown.
    """

class TestComponentFactory:
    """Factory for creating test components and mocks"""
    
    @staticmethod
    def create_mock_component(
        component_type: Type[T],
        **mock_attributes
    ) -> T:
        """Create a mock instance of a component"""
        
    @staticmethod
    def create_test_component(
        component_type: Type[T],
        dependencies: Dict[Type, Any] = None
    ) -> T:
        """Create a real component with test dependencies"""
```

**Usage Examples:**

```python
import pytest
from opusgenie_di._testing.fixtures import create_test_context, reset_global_state

class TestCustomerService:
    
    def setup_method(self):
        """Setup before each test"""
        reset_global_state()
        self.context = create_test_context("customer_test")
    
    async def test_customer_creation(self):
        """Test customer creation in isolation"""
        
        # Register test components
        self.context.register(CustomerRepository, MockCustomerRepository)
        self.context.register(CustomerService)
        
        # Resolve and test
        service = self.context.resolve(CustomerService)
        customer = await service.create_customer({
            'name': 'Test Customer',
            'email': 'test@example.com'
        })
        
        assert customer.name == 'Test Customer'
        assert customer.email == 'test@example.com'
    
    async def test_with_isolated_context(self):
        """Test with only required components"""
        
        context = create_isolated_context(
            CustomerService,
            MockCustomerRepository
        )
        
        service = context.resolve(CustomerService)
        # Test service functionality
```

### Mock Components

Pre-built mock components for common testing scenarios.

```python title="Mock Components"
from opusgenie_di._testing.fixtures import (
    MockDatabaseService,
    MockEventBus,
    MockCache,
    MockEmailService,
    MockPaymentGateway
)

@og_component()
class MockDatabaseService(BaseComponent):
    """Mock database service for testing"""
    
    def __init__(self) -> None:
        super().__init__()
        self.data = {}
        self.queries_executed = []
    
    async def execute(self, query: str, *params) -> List[Dict]:
        """Mock query execution"""
        self.queries_executed.append((query, params))
        return []
    
    async def fetch_one(self, query: str, *params) -> Dict:
        """Mock single row fetch"""
        self.queries_executed.append((query, params))
        return {}
    
    def get_executed_queries(self) -> List[Tuple[str, Tuple]]:
        """Get all executed queries for verification"""
        return self.queries_executed

@og_component()
class MockEventBus(BaseComponent):
    """Mock event bus for testing"""
    
    def __init__(self) -> None:
        super().__init__()
        self.published_events = []
        self.subscriptions = {}
    
    async def publish(self, event_name: str, event_data: Any = None) -> None:
        """Record published events"""
        self.published_events.append((event_name, event_data))
    
    def subscribe(self, event_name: str, handler, priority: int = 0) -> str:
        """Mock subscription"""
        if event_name not in self.subscriptions:
            self.subscriptions[event_name] = []
        self.subscriptions[event_name].append(handler)
        return f"sub_{len(self.subscriptions)}"
    
    def get_published_events(self) -> List[Tuple[str, Any]]:
        """Get all published events for verification"""
        return self.published_events

@og_component()
class MockPaymentGateway(BaseComponent):
    """Mock payment gateway for testing"""
    
    def __init__(self) -> None:
        super().__init__()
        self.processed_payments = []
        self.should_fail = False
        self.failure_reason = "Mock failure"
    
    async def process_payment(
        self,
        amount: Decimal,
        from_account: str,
        to_account: str
    ) -> Dict[str, Any]:
        """Mock payment processing"""
        
        payment_record = {
            'amount': amount,
            'from_account': from_account,
            'to_account': to_account,
            'timestamp': datetime.utcnow()
        }
        
        if self.should_fail:
            payment_record['status'] = 'failed'
            payment_record['error'] = self.failure_reason
            raise PaymentProcessingError(self.failure_reason)
        
        payment_record['status'] = 'completed'
        payment_record['transaction_id'] = f"txn_{uuid.uuid4().hex[:12]}"
        
        self.processed_payments.append(payment_record)
        return payment_record
    
    def configure_failure(self, should_fail: bool, reason: str = "Mock failure"):
        """Configure mock to simulate failures"""
        self.should_fail = should_fail
        self.failure_reason = reason
```

---

## Test Context Patterns

### Test Module Definition

Creating test-specific context modules for comprehensive testing.

```python title="Test Module Patterns"
# Production context
@og_context(
    name="customer_management",
    providers=[CustomerService, CustomerRepository, CustomerValidator],
    imports=[
        ModuleContextImport(DatabaseService, from_context="infrastructure")
    ],
    exports=[CustomerService]
)
class CustomerManagementModule:
    pass

# Test context with mocks
@og_context(
    name="customer_management_test",
    providers=[
        CustomerService,           # Real service under test
        MockCustomerRepository,    # Mock repository
        MockCustomerValidator,     # Mock validator
        MockDatabaseService        # Mock database
    ],
    exports=[CustomerService]
)
class CustomerManagementTestModule:
    pass

# Integration test context (partial mocks)
@og_context(
    name="customer_management_integration",
    providers=[
        CustomerService,           # Real service
        CustomerRepository,        # Real repository
        MockCustomerValidator,     # Mock validator (external service)
        TestDatabaseService        # Test database
    ],
    exports=[CustomerService]
)
class CustomerManagementIntegrationModule:
    pass
```

### Multi-Context Testing

Testing interactions between multiple contexts.

```python title="Multi-Context Testing"
from opusgenie_di._modules.builder import ContextModuleBuilder

class TestMultiContextInteraction:
    
    async def test_customer_payment_interaction(self):
        """Test interaction between customer and payment contexts"""
        
        # Build test contexts
        builder = ContextModuleBuilder()
        contexts = await builder.build_contexts(
            InfrastructureTestModule,     # Mock infrastructure
            CustomerManagementTestModule, # Customer context with mocks
            PaymentProcessingTestModule   # Payment context with mocks
        )
        
        customer_service = contexts["customer_management_test"].resolve(CustomerService)
        payment_service = contexts["payment_processing_test"].resolve(PaymentService)
        
        # Create test customer
        customer = await customer_service.create_customer({
            'name': 'Test Customer',
            'email': 'test@example.com'
        })
        
        # Open account
        account = await customer_service.open_account(customer.id, 'checking')
        
        # Process payment (should use customer data)
        payment_result = await payment_service.process_payment({
            'from_account': account.id,
            'to_account': 'external_account',
            'amount': Decimal('100.00')
        })
        
        assert payment_result.status == 'completed'
        
        # Verify cross-context interaction
        mock_customer_repo = contexts["customer_management_test"].resolve(MockCustomerRepository)
        assert len(mock_customer_repo.saved_customers) == 1
        
        mock_payment_gateway = contexts["payment_processing_test"].resolve(MockPaymentGateway)
        assert len(mock_payment_gateway.processed_payments) == 1
```

---

## Testing Lifecycle & Events

### Lifecycle Testing

Testing component initialization and cleanup behavior.

```python title="Lifecycle Testing"
class TestComponentLifecycle:
    
    async def test_initialization_order(self):
        """Test that components initialize in correct dependency order"""
        
        initialization_order = []
        
        @og_component()
        class ComponentA(BaseComponent):
            async def initialize(self):
                await super().initialize()
                initialization_order.append('A')
        
        @og_component()
        class ComponentB(BaseComponent):
            def __init__(self, comp_a: ComponentA):
                super().__init__()
                self.comp_a = comp_a
            
            async def initialize(self):
                await super().initialize()
                initialization_order.append('B')
        
        @og_component()
        class ComponentC(BaseComponent):
            def __init__(self, comp_b: ComponentB):
                super().__init__()
                self.comp_b = comp_b
            
            async def initialize(self):
                await super().initialize()
                initialization_order.append('C')
        
        # Create test context
        context = create_isolated_context(ComponentA, ComponentB, ComponentC)
        
        # Initialize context (should initialize components in dependency order)
        await context.initialize_all()
        
        # Verify initialization order
        assert initialization_order == ['A', 'B', 'C']
    
    async def test_cleanup_order(self):
        """Test that components cleanup in reverse dependency order"""
        
        cleanup_order = []
        
        @og_component()
        class ComponentA(BaseComponent):
            async def cleanup(self):
                cleanup_order.append('A')
                await super().cleanup()
        
        @og_component()
        class ComponentB(BaseComponent):
            def __init__(self, comp_a: ComponentA):
                super().__init__()
                self.comp_a = comp_a
            
            async def cleanup(self):
                cleanup_order.append('B')
                await super().cleanup()
        
        context = create_isolated_context(ComponentA, ComponentB)
        await context.initialize_all()
        
        # Cleanup should be in reverse order
        await context.cleanup_all()
        
        assert cleanup_order == ['B', 'A']
```

### Event Testing

Testing event publication and subscription.

```python title="Event Testing"
from opusgenie_di._testing.fixtures import create_test_event_bus

class TestEventSystem:
    
    async def test_event_publication(self):
        """Test that components publish events correctly"""
        
        event_bus = create_test_event_bus()
        published_events = []
        
        # Subscribe to events
        async def event_collector(event_data):
            published_events.append(event_data)
        
        event_bus.subscribe('customer_created', event_collector)
        
        # Create service with test event bus
        context = create_test_context()
        context.register(EventBus, lambda: event_bus, scope=ComponentScope.SINGLETON)
        context.register(CustomerService)
        
        service = context.resolve(CustomerService)
        
        # Trigger event
        customer = await service.create_customer({'name': 'Test', 'email': 'test@example.com'})
        
        # Verify event was published
        assert len(published_events) == 1
        assert published_events[0].customer_id == customer.id
    
    async def test_event_driven_workflow(self):
        """Test complex event-driven workflow"""
        
        event_bus = create_test_event_bus()
        workflow_steps = []
        
        # Service that reacts to customer creation
        @og_component()
        class WelcomeService(BaseComponent):
            def __init__(self, event_bus: EventBus):
                super().__init__()
                self.event_bus = event_bus
            
            async def initialize(self):
                await super().initialize()
                self.event_bus.subscribe('customer_created', self.send_welcome_email)
            
            async def send_welcome_email(self, event_data):
                workflow_steps.append(f"welcome_email_sent:{event_data.customer_id}")
        
        # Service that creates customer account
        @og_component()
        class AccountSetupService(BaseComponent):
            def __init__(self, event_bus: EventBus):
                super().__init__()
                self.event_bus = event_bus
            
            async def initialize(self):
                await super().initialize()
                self.event_bus.subscribe('customer_created', self.create_default_account)
            
            async def create_default_account(self, event_data):
                workflow_steps.append(f"account_created:{event_data.customer_id}")
        
        # Setup test context
        context = create_test_context()
        context.register(EventBus, lambda: event_bus, scope=ComponentScope.SINGLETON)
        context.register(CustomerService)
        context.register(WelcomeService)
        context.register(AccountSetupService)
        
        await context.initialize_all()
        
        # Trigger workflow
        customer_service = context.resolve(CustomerService)
        customer = await customer_service.create_customer({'name': 'Test', 'email': 'test@example.com'})
        
        # Allow events to propagate
        await asyncio.sleep(0.1)
        
        # Verify workflow steps
        assert f"welcome_email_sent:{customer.id}" in workflow_steps
        assert f"account_created:{customer.id}" in workflow_steps
```

---

## Performance Testing

### Performance Test Utilities

Utilities for testing component performance and scalability.

```python title="Performance Testing"
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

class PerformanceTestHarness:
    """Harness for performance testing components"""
    
    def __init__(self, context: ContextInterface):
        self.context = context
        self.metrics = {}
    
    async def measure_operation(
        self,
        operation_name: str,
        operation: Callable,
        iterations: int = 100
    ) -> Dict[str, float]:
        """Measure operation performance over multiple iterations"""
        
        durations = []
        
        for _ in range(iterations):
            start_time = time.time()
            await operation() if asyncio.iscoroutinefunction(operation) else operation()
            duration = time.time() - start_time
            durations.append(duration)
        
        return {
            'min': min(durations),
            'max': max(durations),
            'avg': sum(durations) / len(durations),
            'total': sum(durations),
            'iterations': iterations
        }
    
    async def measure_concurrent_operations(
        self,
        operation: Callable,
        concurrency: int = 10,
        total_operations: int = 100
    ) -> Dict[str, Any]:
        """Measure performance under concurrent load"""
        
        start_time = time.time()
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_operation():
            async with semaphore:
                return await operation() if asyncio.iscoroutinefunction(operation) else operation()
        
        # Execute operations concurrently
        tasks = [limited_operation() for _ in range(total_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Count successes and failures
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = sum(1 for r in results if isinstance(r, Exception))
        
        return {
            'total_time': total_time,
            'operations_per_second': total_operations / total_time,
            'concurrency': concurrency,
            'total_operations': total_operations,
            'successes': successes,
            'failures': failures,
            'success_rate': successes / total_operations
        }

# Usage example
class TestPaymentServicePerformance:
    
    async def test_payment_processing_performance(self):
        """Test payment service performance under load"""
        
        # Setup test context with mocks
        context = create_test_context()
        context.register(PaymentService)
        context.register(MockPaymentGateway)
        context.register(MockAccountService)
        
        await context.initialize_all()
        
        harness = PerformanceTestHarness(context)
        payment_service = context.resolve(PaymentService)
        
        # Test single operation performance
        async def process_test_payment():
            return await payment_service.process_payment({
                'from_account': 'acc_123',
                'to_account': 'acc_456',
                'amount': Decimal('100.00')
            })
        
        # Measure single operation
        single_op_metrics = await harness.measure_operation(
            'process_payment',
            process_test_payment,
            iterations=50
        )
        
        # Verify performance thresholds
        assert single_op_metrics['avg'] < 0.1  # Average under 100ms
        assert single_op_metrics['max'] < 0.5  # Max under 500ms
        
        # Measure concurrent performance
        concurrent_metrics = await harness.measure_concurrent_operations(
            process_test_payment,
            concurrency=10,
            total_operations=100
        )
        
        # Verify concurrent performance
        assert concurrent_metrics['success_rate'] >= 0.95  # 95% success rate
        assert concurrent_metrics['operations_per_second'] >= 50  # 50 ops/sec minimum
    
    async def test_context_initialization_performance(self):
        """Test context initialization performance"""
        
        start_time = time.time()
        
        # Build complex context
        builder = ContextModuleBuilder()
        contexts = await builder.build_contexts(
            InfrastructureModule,
            CustomerManagementModule,
            AccountManagementModule,
            PaymentProcessingModule,
            LoanProcessingModule
        )
        
        initialization_time = time.time() - start_time
        
        # Verify initialization completes within reasonable time
        assert initialization_time < 5.0  # Under 5 seconds
        
        # Verify all contexts were created
        assert len(contexts) == 5
        
        # Verify components can be resolved
        customer_service = contexts["customer_management"].resolve(CustomerService)
        assert customer_service is not None
```

---

## Integration Testing

### Database Integration Testing

Testing with real database connections in controlled environments.

```python title="Database Integration Testing"
import pytest
from opusgenie_di._testing.fixtures import create_test_database

@pytest.mark.integration
class TestDatabaseIntegration:
    
    async def setup_method(self):
        """Setup test database"""
        self.test_db = await create_test_database()
        
        # Create test context with real database
        self.context = create_test_context()
        self.context.register(DatabaseService, lambda: self.test_db)
        self.context.register(CustomerRepository)
        self.context.register(CustomerService)
        
        await self.context.initialize_all()
    
    async def teardown_method(self):
        """Cleanup test database"""
        await self.test_db.cleanup()
        await self.context.cleanup_all()
    
    async def test_customer_persistence(self):
        """Test customer creation and retrieval with real database"""
        
        customer_service = self.context.resolve(CustomerService)
        
        # Create customer
        customer = await customer_service.create_customer({
            'name': 'Integration Test Customer',
            'email': 'integration@example.com'
        })
        
        # Verify customer was persisted
        retrieved_customer = await customer_service.get_customer(customer.id)
        assert retrieved_customer is not None
        assert retrieved_customer.name == 'Integration Test Customer'
        assert retrieved_customer.email == 'integration@example.com'
    
    async def test_transaction_rollback(self):
        """Test transaction rollback on error"""
        
        customer_service = self.context.resolve(CustomerService)
        
        with pytest.raises(ValidationError):
            # This should fail and rollback transaction
            await customer_service.create_customer({
                'name': '',  # Invalid empty name
                'email': 'invalid-email'  # Invalid email format
            })
        
        # Verify no customer was created
        customers = await customer_service.list_customers()
        assert len(customers) == 0
```

This comprehensive testing API enables thorough testing of OpusGenie DI applications at all levels - from unit tests with mocks to integration tests with real dependencies, performance testing under load, and complex multi-context workflows.