# Hooks & Events API Reference

*Complete reference for the OpusGenie DI event system and lifecycle hooks*

---

## Event System

### Event Bus

Central event dispatcher for framework-wide event handling.

```python title="Event Bus Interface"
from opusgenie_di._hooks.event_hooks import EventBus, EventHandler
from typing import Callable, Any, Dict, List

class EventBus:
    """Central event bus for framework events"""
    
    def __init__(self) -> None:
        """Initialize event bus"""
        
    async def publish(self, event_name: str, event_data: Any = None) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_name: Name of the event to publish
            event_data: Optional data to send with the event
        """
        
    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
        priority: int = 0
    ) -> str:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of the event to subscribe to
            handler: Function or coroutine to handle the event
            priority: Handler priority (higher = earlier execution)
            
        Returns:
            Subscription ID for later unsubscription
        """
        
    def unsubscribe(self, event_name: str, subscription_id: str) -> bool:
        """Unsubscribe from an event"""
        
    def get_subscribers(self, event_name: str) -> List[EventHandler]:
        """Get all subscribers for an event"""
        
    async def publish_and_collect(
        self,
        event_name: str,
        event_data: Any = None
    ) -> List[Any]:
        """Publish event and collect return values from handlers"""
```

**Usage Examples:**

```python
# Create event bus
event_bus = EventBus()

# Subscribe to events
async def log_customer_created(event_data):
    customer = event_data['customer']
    print(f"Customer created: {customer.id}")

subscription_id = event_bus.subscribe(
    'customer_created',
    log_customer_created,
    priority=100  # High priority for logging
)

# Publish events
await event_bus.publish('customer_created', {
    'customer': customer,
    'timestamp': datetime.utcnow(),
    'source': 'customer_service'
})

# Unsubscribe
event_bus.unsubscribe('customer_created', subscription_id)
```

### Event Handler Types

Different types of event handlers supported by the system.

```python title="Event Handler Types"
from typing import Union, Awaitable

# Type alias for event handlers
EventHandler = Union[
    Callable[[Any], None],           # Sync function
    Callable[[Any], Awaitable[None]], # Async function
    Callable[[], None],              # No-argument function
    Callable[[], Awaitable[None]]    # No-argument async function
]

# Example handlers
def sync_handler(event_data):
    """Synchronous event handler"""
    print(f"Sync: {event_data}")

async def async_handler(event_data):
    """Asynchronous event handler"""
    await asyncio.sleep(0.1)
    print(f"Async: {event_data}")

def no_arg_handler():
    """Handler that doesn't need event data"""
    print("Event occurred")

# All handler types can be subscribed
event_bus.subscribe('test_event', sync_handler)
event_bus.subscribe('test_event', async_handler)
event_bus.subscribe('test_event', no_arg_handler)
```

---

## Lifecycle Hooks

### Component Lifecycle Events

Events fired during component lifecycle management.

```python title="Lifecycle Events"
from opusgenie_di._hooks.lifecycle_hooks import (
    LifecycleHookManager,
    LifecycleStage,
    ComponentLifecycleEvent
)

@dataclass
class ComponentLifecycleEvent:
    """Event data for component lifecycle events"""
    
    component_type: Type
    component_instance: Any
    context_name: str
    stage: LifecycleStage
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class LifecycleStage(Enum):
    """Component lifecycle stages"""
    
    BEFORE_CREATION = "before_creation"
    AFTER_CREATION = "after_creation"
    BEFORE_INITIALIZATION = "before_initialization"
    AFTER_INITIALIZATION = "after_initialization"
    BEFORE_CLEANUP = "before_cleanup"
    AFTER_CLEANUP = "after_cleanup"
```

**Lifecycle Event Names:**
- `component_before_creation`
- `component_after_creation`
- `component_before_initialization`
- `component_after_initialization`
- `component_before_cleanup`
- `component_after_cleanup`

### Lifecycle Hook Manager

Manager for component lifecycle hooks and events.

```python title="Lifecycle Hook Manager"
class LifecycleHookManager:
    """Manages component lifecycle hooks"""
    
    def __init__(self, event_bus: EventBus) -> None:
        """Initialize with event bus"""
        
    async def fire_lifecycle_event(
        self,
        stage: LifecycleStage,
        component_type: Type,
        component_instance: Any,
        context_name: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Fire a lifecycle event"""
        
    def register_hook(
        self,
        stage: LifecycleStage,
        hook: Callable[[ComponentLifecycleEvent], Any],
        component_filter: Callable[[Type], bool] = None
    ) -> str:
        """
        Register a lifecycle hook.
        
        Args:
            stage: Lifecycle stage to hook into
            hook: Function to call during lifecycle event
            component_filter: Optional filter for which components to hook
            
        Returns:
            Hook registration ID
        """
        
    def unregister_hook(self, hook_id: str) -> bool:
        """Unregister a lifecycle hook"""
```

**Usage Examples:**

```python
# Create lifecycle hook manager
hook_manager = LifecycleHookManager(event_bus)

# Performance monitoring hook
async def monitor_initialization(event: ComponentLifecycleEvent):
    if event.stage == LifecycleStage.BEFORE_INITIALIZATION:
        event.metadata['start_time'] = time.time()
    elif event.stage == LifecycleStage.AFTER_INITIALIZATION:
        start_time = event.metadata.get('start_time', time.time())
        duration = time.time() - start_time
        print(f"{event.component_type.__name__} initialized in {duration:.3f}s")

# Register hooks
hook_manager.register_hook(
    LifecycleStage.BEFORE_INITIALIZATION,
    monitor_initialization
)
hook_manager.register_hook(
    LifecycleStage.AFTER_INITIALIZATION,
    monitor_initialization
)

# Component-specific hook with filter
def is_service_component(component_type: Type) -> bool:
    return component_type.__name__.endswith('Service')

async def log_service_creation(event: ComponentLifecycleEvent):
    print(f"Service component created: {event.component_type.__name__}")

hook_manager.register_hook(
    LifecycleStage.AFTER_CREATION,
    log_service_creation,
    component_filter=is_service_component
)
```

---

## Custom Events

### Framework Events

Built-in events fired by the OpusGenie DI framework.

```python title="Framework Events"
# Context Events
CONTEXT_CREATED = "context_created"
CONTEXT_INITIALIZED = "context_initialized"
CONTEXT_DESTROYED = "context_destroyed"

# Component Events  
COMPONENT_REGISTERED = "component_registered"
COMPONENT_RESOLVED = "component_resolved"
COMPONENT_CREATED = "component_created"
COMPONENT_INITIALIZED = "component_initialized"
COMPONENT_DESTROYED = "component_destroyed"

# Import/Export Events
COMPONENT_IMPORTED = "component_imported"
COMPONENT_EXPORTED = "component_exported"
IMPORT_FAILED = "import_failed"

# Error Events
DEPENDENCY_RESOLUTION_FAILED = "dependency_resolution_failed"
CIRCULAR_DEPENDENCY_DETECTED = "circular_dependency_detected"
INITIALIZATION_FAILED = "initialization_failed"
```

### Domain Events

Custom events for application-specific business logic.

```python title="Domain Events"
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

# Base class for domain events
@dataclass
class DomainEvent:
    """Base class for domain events"""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return asdict(self)

# Banking domain events
@dataclass
class CustomerCreatedEvent(DomainEvent):
    customer_id: str
    customer_type: str
    created_by: str

@dataclass
class AccountOpenedEvent(DomainEvent):
    account_id: str
    customer_id: str
    account_type: str
    initial_balance: Decimal

@dataclass
class PaymentProcessedEvent(DomainEvent):
    payment_id: str
    from_account: str
    to_account: str
    amount: Decimal
    status: str

# Usage in components
@og_component()
class CustomerService(BaseComponent):
    
    def __init__(self, event_bus: EventBus) -> None:
        super().__init__()
        self.event_bus = event_bus
    
    async def create_customer(self, customer_data: Dict) -> Customer:
        customer = Customer(**customer_data)
        await self.repository.save(customer)
        
        # Publish domain event
        event = CustomerCreatedEvent(
            customer_id=customer.id,
            customer_type=customer.type,
            created_by=customer_data.get('created_by', 'system'),
            source='customer_service'
        )
        
        await self.event_bus.publish('customer_created', event)
        return customer
```

---

## Event-Driven Patterns

### Event Sourcing

Using events to build event-sourced components.

```python title="Event Sourcing Pattern"
@og_component()
class EventSourcedAccountService(BaseComponent):
    """Account service using event sourcing"""
    
    def __init__(self, event_bus: EventBus, event_store: EventStore) -> None:
        super().__init__()
        self.event_bus = event_bus
        self.event_store = event_store
        
    async def initialize(self) -> None:
        await super().initialize()
        
        # Subscribe to account events for projection updates
        self.event_bus.subscribe('account_opened', self._update_account_projection)
        self.event_bus.subscribe('account_credited', self._update_account_projection)
        self.event_bus.subscribe('account_debited', self._update_account_projection)
    
    async def open_account(self, customer_id: str, account_type: str) -> str:
        account_id = f"acc_{uuid.uuid4().hex[:12]}"
        
        # Create and store event
        event = AccountOpenedEvent(
            account_id=account_id,
            customer_id=customer_id,
            account_type=account_type,
            initial_balance=Decimal('0')
        )
        
        await self.event_store.append(account_id, event)
        await self.event_bus.publish('account_opened', event)
        
        return account_id
    
    async def credit_account(self, account_id: str, amount: Decimal) -> None:
        # Load current state from events
        current_balance = await self._get_current_balance(account_id)
        
        event = AccountCreditedEvent(
            account_id=account_id,
            amount=amount,
            balance_after=current_balance + amount
        )
        
        await self.event_store.append(account_id, event)
        await self.event_bus.publish('account_credited', event)
    
    async def _get_current_balance(self, account_id: str) -> Decimal:
        """Rebuild current balance from events"""
        events = await self.event_store.get_events(account_id)
        balance = Decimal('0')
        
        for event in events:
            if isinstance(event, AccountOpenedEvent):
                balance = event.initial_balance
            elif isinstance(event, AccountCreditedEvent):
                balance += event.amount
            elif isinstance(event, AccountDebitedEvent):
                balance -= event.amount
                
        return balance
```

### Saga Pattern

Coordinating complex business processes across multiple contexts using events.

```python title="Saga Pattern"
@og_component()
class LoanDisbursementSaga(BaseComponent):
    """Saga for coordinating loan disbursement process"""
    
    def __init__(self, event_bus: EventBus) -> None:
        super().__init__()
        self.event_bus = event_bus
        self.active_sagas: Dict[str, Dict] = {}
    
    async def initialize(self) -> None:
        await super().initialize()
        
        # Subscribe to saga events
        self.event_bus.subscribe('loan_approved', self._start_disbursement_saga)
        self.event_bus.subscribe('funds_reserved', self._handle_funds_reserved)
        self.event_bus.subscribe('account_credited', self._handle_account_credited)
        self.event_bus.subscribe('disbursement_failed', self._handle_disbursement_failed)
    
    async def _start_disbursement_saga(self, event: LoanApprovedEvent) -> None:
        """Start loan disbursement saga"""
        saga_id = f"saga_{uuid.uuid4().hex[:12]}"
        
        self.active_sagas[saga_id] = {
            'loan_id': event.loan_id,
            'amount': event.amount,
            'customer_account': event.customer_account,
            'status': 'started',
            'steps_completed': []
        }
        
        # Step 1: Reserve funds from treasury
        await self.event_bus.publish('reserve_funds', {
            'saga_id': saga_id,
            'amount': event.amount,
            'purpose': f'loan_disbursement_{event.loan_id}'
        })
    
    async def _handle_funds_reserved(self, event) -> None:
        """Handle funds reservation success"""
        saga_id = event['saga_id']
        saga = self.active_sagas.get(saga_id)
        
        if saga:
            saga['steps_completed'].append('funds_reserved')
            saga['reservation_id'] = event['reservation_id']
            
            # Step 2: Credit customer account
            await self.event_bus.publish('credit_account', {
                'saga_id': saga_id,
                'account_id': saga['customer_account'],
                'amount': saga['amount'],
                'reference': f"Loan disbursement {saga['loan_id']}"
            })
    
    async def _handle_account_credited(self, event) -> None:
        """Handle account credit success - complete saga"""
        saga_id = event.get('saga_id')
        saga = self.active_sagas.get(saga_id)
        
        if saga:
            saga['steps_completed'].append('account_credited')
            saga['status'] = 'completed'
            
            # Publish completion event
            await self.event_bus.publish('loan_disbursed', {
                'loan_id': saga['loan_id'],
                'amount': saga['amount'],
                'disbursed_at': datetime.utcnow()
            })
            
            # Clean up saga
            del self.active_sagas[saga_id]
    
    async def _handle_disbursement_failed(self, event) -> None:
        """Handle disbursement failure - compensate completed steps"""
        saga_id = event['saga_id']
        saga = self.active_sagas.get(saga_id)
        
        if saga:
            # Compensate in reverse order
            if 'funds_reserved' in saga['steps_completed']:
                await self.event_bus.publish('release_funds', {
                    'reservation_id': saga['reservation_id']
                })
            
            saga['status'] = 'failed'
            del self.active_sagas[saga_id]
```

---

## Testing Event Systems

### Event Testing Utilities

Utilities for testing event-driven components.

```python title="Event Testing"
from opusgenie_di._testing.fixtures import create_test_event_bus

class TestEventDrivenComponent:
    
    async def test_customer_creation_publishes_event(self):
        """Test that customer creation publishes correct event"""
        
        # Create test event bus
        event_bus = create_test_event_bus()
        
        # Track published events
        published_events = []
        
        async def event_collector(event_data):
            published_events.append(event_data)
        
        event_bus.subscribe('customer_created', event_collector)
        
        # Create component with test event bus
        customer_service = CustomerService(event_bus)
        
        # Execute action
        customer = await customer_service.create_customer({
            'name': 'Test Customer',
            'email': 'test@example.com'
        })
        
        # Verify event was published
        assert len(published_events) == 1
        
        event = published_events[0]
        assert isinstance(event, CustomerCreatedEvent)
        assert event.customer_id == customer.id
        assert event.source == 'customer_service'
    
    async def test_saga_compensation(self):
        """Test saga compensation on failure"""
        
        event_bus = create_test_event_bus()
        saga = LoanDisbursementSaga(event_bus)
        
        # Start saga
        await saga._start_disbursement_saga(LoanApprovedEvent(
            loan_id='loan_123',
            amount=Decimal('10000'),
            customer_account='acc_456'
        ))
        
        # Simulate funds reserved
        await saga._handle_funds_reserved({
            'saga_id': list(saga.active_sagas.keys())[0],
            'reservation_id': 'res_789'
        })
        
        # Simulate failure
        await saga._handle_disbursement_failed({
            'saga_id': list(saga.active_sagas.keys())[0],
            'error': 'Account credit failed'
        })
        
        # Verify saga was cleaned up
        assert len(saga.active_sagas) == 0
```

This hooks and events API provides a powerful foundation for building event-driven, loosely coupled applications with OpusGenie DI, enabling sophisticated patterns like event sourcing, sagas, and domain event handling.