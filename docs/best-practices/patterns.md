# Design Patterns & Best Practices

*Elena Korvas shares battle-tested patterns from building OgPgy Bank*

---

!!! quote "Elena Korvas - Chief Technology Officer"
    *"These patterns emerged from real production challenges at OgPgy Bank. Each one solved a specific problem we faced while scaling to 2.3 million customers."*

## Multi-Context Design Patterns

### 1. Context Boundary Pattern

**Problem**: How to organize business logic into contexts that align with domain boundaries.

**Solution**: Use Domain-Driven Design bounded contexts as your context boundaries.

```python title="Well-Defined Context Boundaries"
# ✅ Good - Business domain alignment
@og_context(
    name="customer_onboarding",
    description="Complete customer acquisition and verification process",
    business_owner="Customer Experience Team"
)
class CustomerOnboardingModule:
    """
    Bounded Context: Customer Onboarding
    - Customer registration
    - Identity verification (KYC)
    - Account setup
    - Welcome communication
    """
    pass

@og_context(
    name="payment_processing", 
    description="All payment-related operations and integrations",
    business_owner="Payments Team"
)
class PaymentProcessingModule:
    """
    Bounded Context: Payment Processing
    - Payment instruction processing
    - External network integration
    - Fraud detection
    - Settlement processing
    """
    pass

# ❌ Bad - Technical layer alignment
@og_context(name="repositories")  # Technical, not business
class RepositoryModule: pass

@og_context(name="services")     # Too generic
class ServiceModule: pass
```

### 2. Import/Export Interface Pattern

**Problem**: Managing dependencies between contexts without tight coupling.

**Solution**: Export stable business interfaces, import only what you need.

```python title="Clean Import/Export Interfaces"
# ✅ Good - Stable business interface
@og_context(
    name="customer_management",
    exports=[
        CustomerService,        # Core business capability
        CustomerValidator,      # Reusable validation logic
        CustomerEvents         # Event contracts
    ],
    # Don't export implementation details
    providers=[
        CustomerService,
        CustomerValidator, 
        CustomerRepository,     # Internal - not exported
        CustomerConfig,         # Internal - not exported
        CustomerEvents
    ]
)
class CustomerManagementModule:
    pass

# ✅ Good - Minimal, focused imports
@og_context(
    name="account_management",
    imports=[
        ModuleContextImport(CustomerService, from_context="customer_management"),
        ModuleContextImport(DatabasePool, from_context="infrastructure")
    ],
    # Clear business justification for each import
)
class AccountManagementModule:
    pass

# ❌ Bad - Too many imports creates coupling
@og_context(
    imports=[
        ModuleContextImport(Service1, from_context="context1"),
        ModuleContextImport(Service2, from_context="context2"), 
        ModuleContextImport(Service3, from_context="context3"),
        # ... many more dependencies
    ]
)
class OverlyDependentModule:
    pass
```

### 3. Event-Driven Communication Pattern

**Problem**: How to enable loose coupling between contexts while maintaining consistency.

**Solution**: Use domain events for cross-context communication.

```python title="Event-Driven Context Communication"
# ✅ Good - Event-driven communication
@og_component()
class CustomerService(BaseComponent):
    
    async def onboard_customer(self, application: CustomerApplication) -> Customer:
        # Process customer onboarding
        customer = await self._create_customer(application)
        
        # Publish domain event for other contexts
        await self.event_bus.publish(CustomerOnboardedEvent(
            customer_id=customer.id,
            customer_type=customer.type,
            verification_status=customer.kyc_status,
            onboarded_at=datetime.utcnow()
        ))
        
        return customer

# Other contexts subscribe to events
@og_component()
class AccountService(BaseComponent):
    
    async def initialize(self) -> None:
        await super().initialize()
        
        # Subscribe to customer events
        self.event_bus.subscribe(
            'CustomerOnboardedEvent',
            self._handle_customer_onboarded
        )
    
    async def _handle_customer_onboarded(self, event: CustomerOnboardedEvent) -> None:
        """Automatically create default account for new customers"""
        if event.verification_status == "verified":
            await self.create_default_account(event.customer_id)

# ❌ Bad - Direct synchronous coupling
@og_component()
class TightlyCoupledService(BaseComponent):
    
    def __init__(self, account_service: AccountService):  # Direct dependency
        self.account_service = account_service
    
    async def onboard_customer(self, application: CustomerApplication) -> Customer:
        customer = await self._create_customer(application)
        
        # Direct call creates tight coupling
        await self.account_service.create_default_account(customer.id)
        
        return customer
```

### 4. Shared Infrastructure Pattern

**Problem**: How to share common infrastructure components across contexts.

**Solution**: Create a dedicated infrastructure context that exports shared services.

```python title="Shared Infrastructure Context"
@og_context(
    name="infrastructure",
    exports=[
        DatabasePool,
        RedisCache,
        EventBus,
        ConfigService,
        LoggingService,
        MonitoringService
    ],
    providers=[
        DatabaseConfig,
        RedisConfig,
        DatabasePool,
        RedisCache,
        EventBus,
        ConfigService,
        LoggingService,
        MonitoringService
    ],
    description="Shared infrastructure services for all contexts"
)
class InfrastructureModule:
    """
    Infrastructure Context Pattern:
    - Provides shared technical capabilities
    - No business logic
    - High reusability
    - Stable interfaces
    """
    pass

# Business contexts import from infrastructure
@og_context(
    name="payment_processing",
    imports=[
        ModuleContextImport(DatabasePool, from_context="infrastructure"),
        ModuleContextImport(RedisCache, from_context="infrastructure"),
        ModuleContextImport(EventBus, from_context="infrastructure")
    ]
)
class PaymentProcessingModule:
    pass
```

## Component Design Patterns

### 5. Repository Pattern

**Problem**: How to abstract data access and make components testable.

**Solution**: Use repository pattern with dependency injection.

```python title="Repository Pattern Implementation"
# ✅ Good - Repository pattern with interface
from typing import Protocol

class CustomerRepository(Protocol):
    async def save(self, customer: Customer) -> Customer: ...
    async def get_by_id(self, customer_id: str) -> Optional[Customer]: ...
    async def get_by_email(self, email: str) -> Optional[Customer]: ...

@og_component()
class PostgreSQLCustomerRepository(BaseComponent):
    """Concrete repository implementation"""
    
    def __init__(self, db: DatabasePool) -> None:
        super().__init__()
        self.db = db
    
    async def save(self, customer: Customer) -> Customer:
        # PostgreSQL-specific implementation
        query = "INSERT INTO customers (...) VALUES (...)"
        await self.db.execute(query, customer.to_tuple())
        return customer

@og_component()
class CustomerService(BaseComponent):
    """Business service using repository"""
    
    def __init__(self, customer_repo: CustomerRepository) -> None:
        super().__init__()
        self.customer_repo = customer_repo  # Injected dependency
    
    async def create_customer(self, application: CustomerApplication) -> Customer:
        customer = Customer.from_application(application)
        return await self.customer_repo.save(customer)

# Easy to test with mock repository
class TestCustomerService:
    async def test_create_customer(self):
        mock_repo = MockCustomerRepository()
        service = CustomerService(mock_repo)
        
        customer = await service.create_customer(test_application)
        
        assert customer.id is not None
        assert mock_repo.save_called
```

### 6. Service Layer Pattern

**Problem**: How to organize complex business logic and maintain separation of concerns.

**Solution**: Use layered service architecture with clear responsibilities.

```python title="Layered Service Architecture"
# Domain Layer - Pure business logic
@dataclass
class Account:
    def can_withdraw(self, amount: Decimal) -> bool:
        return self.available_balance >= amount
    
    def apply_interest(self, rate: Decimal) -> Decimal:
        if not self.features.has_interest:
            return Decimal('0')
        return self.balance * rate / Decimal('365')

# Application Service Layer - Orchestrates use cases
@og_component()
class AccountApplicationService(BaseComponent):
    """Application service - coordinates business operations"""
    
    def __init__(
        self,
        account_repo: AccountRepository,
        customer_service: CustomerService,
        interest_calculator: InterestCalculator,
        event_bus: EventBus
    ) -> None:
        self.account_repo = account_repo
        self.customer_service = customer_service
        self.interest_calculator = interest_calculator
        self.event_bus = event_bus
    
    async def open_account(
        self,
        customer_id: str,
        account_type: AccountType,
        initial_deposit: Decimal
    ) -> Account:
        """Use case: Open new account"""
        
        # 1. Validate customer
        customer = await self.customer_service.get_customer(customer_id)
        if not customer or customer.kyc_status != "verified":
            raise CustomerNotVerifiedError()
        
        # 2. Create account (domain logic)
        account = Account.create(
            customer_id=customer_id,
            account_type=account_type,
            initial_balance=initial_deposit
        )
        
        # 3. Persist
        await self.account_repo.save(account)
        
        # 4. Publish event
        await self.event_bus.publish(AccountOpenedEvent(
            account_id=account.id,
            customer_id=customer_id
        ))
        
        return account

# Domain Service Layer - Complex domain operations
@og_component()
class InterestCalculator(BaseComponent):
    """Domain service - complex business calculations"""
    
    def calculate_tiered_interest(self, account: Account) -> Decimal:
        """Complex domain logic for tiered interest calculation"""
        
        if account.balance <= Decimal('1000'):
            return account.apply_interest(Decimal('0.005'))  # 0.5%
        elif account.balance <= Decimal('10000'):
            return account.apply_interest(Decimal('0.015'))  # 1.5%
        else:
            return account.apply_interest(Decimal('0.025'))  # 2.5%
```

### 7. Factory Pattern

**Problem**: How to create complex objects with multiple configurations.

**Solution**: Use factory pattern with dependency injection.

```python title="Factory Pattern for Complex Object Creation"
@og_component()
class AccountFactory(BaseComponent):
    """Factory for creating different account types"""
    
    def __init__(self, config_service: ConfigService) -> None:
        super().__init__()
        self.config = config_service
    
    def create_account(
        self,
        customer: Customer,
        account_type: AccountType,
        initial_deposit: Decimal = Decimal('0')
    ) -> Account:
        """Factory method for account creation"""
        
        if account_type == AccountType.PERSONAL_SAVINGS:
            return self._create_personal_savings(customer, initial_deposit)
        elif account_type == AccountType.BUSINESS_CHECKING:
            return self._create_business_checking(customer, initial_deposit)
        elif account_type == AccountType.PREMIUM_CHECKING:
            return self._create_premium_checking(customer, initial_deposit)
        else:
            raise UnsupportedAccountTypeError(f"Account type {account_type} not supported")
    
    def _create_personal_savings(self, customer: Customer, initial_deposit: Decimal) -> Account:
        features = AccountFeatures(
            has_interest=True,
            annual_interest_rate=self.config.get('savings_interest_rate'),
            minimum_balance=self.config.get('savings_minimum_balance'),
            monthly_maintenance_fee=Decimal('0')
        )
        
        return Account(
            id=self._generate_account_id(),
            customer_id=customer.id,
            account_type=AccountType.PERSONAL_SAVINGS,
            balance=initial_deposit,
            available_balance=initial_deposit,
            features=features
        )
    
    def _create_business_checking(self, customer: Customer, initial_deposit: Decimal) -> Account:
        features = AccountFeatures(
            has_interest=True,
            annual_interest_rate=self.config.get('business_interest_rate'),
            minimum_balance=self.config.get('business_minimum_balance'),
            monthly_maintenance_fee=self.config.get('business_maintenance_fee'),
            has_overdraft_protection=True,
            overdraft_limit=self.config.get('business_overdraft_limit'),
            free_transactions_per_month=200
        )
        
        return Account(
            id=self._generate_account_id(),
            customer_id=customer.id,
            account_type=AccountType.BUSINESS_CHECKING,
            balance=initial_deposit,
            available_balance=initial_deposit,
            features=features,
            authorized_signatories=[customer.id]
        )
```

## Error Handling Patterns

### 8. Circuit Breaker Pattern

**Problem**: How to handle failures in external service dependencies.

**Solution**: Implement circuit breaker pattern for resilience.

```python title="Circuit Breaker Implementation"
@og_component()
class ResilientPaymentService(BaseComponent):
    """Payment service with circuit breaker for external dependencies"""
    
    def __init__(
        self,
        velocity_pay_gateway: VelocityPayGateway,
        circuit_breaker: CircuitBreaker,
        fallback_processor: FallbackPaymentProcessor
    ) -> None:
        super().__init__()
        self.velocity_pay = velocity_pay_gateway
        self.circuit_breaker = circuit_breaker
        self.fallback_processor = fallback_processor
    
    async def process_payment(self, payment: Payment) -> PaymentResult:
        """Process payment with circuit breaker protection"""
        
        try:
            # Try primary payment processor with circuit breaker
            result = await self.circuit_breaker.call(
                lambda: self.velocity_pay.process_payment(payment)
            )
            return result
            
        except CircuitBreakerOpenError:
            # Circuit breaker is open - use fallback
            self.logger.warning("VelocityPay circuit breaker open, using fallback processor")
            return await self.fallback_processor.process_payment(payment)
        
        except VelocityPayServiceError as e:
            # Service error - may trigger circuit breaker
            self.logger.error(f"VelocityPay service error: {e}")
            raise PaymentProcessingError(f"Payment processing failed: {e}")
```

### 9. Compensation Pattern

**Problem**: How to handle failures in multi-step business processes.

**Solution**: Implement compensation actions for rollback.

```python title="Compensation Pattern for Complex Operations"
@og_component()
class TransactionalLoanService(BaseComponent):
    """Loan service with compensation for failed operations"""
    
    async def disburse_loan(self, loan_id: str) -> LoanDisbursement:
        """Disburse loan with compensation on failure"""
        
        compensation_actions = []
        
        try:
            # Step 1: Reserve funds
            reservation = await self.treasury_service.reserve_funds(loan.amount)
            compensation_actions.append(
                lambda: self.treasury_service.release_reservation(reservation.id)
            )
            
            # Step 2: Create disbursement record
            disbursement = await self.loan_repo.create_disbursement(loan_id)
            compensation_actions.append(
                lambda: self.loan_repo.cancel_disbursement(disbursement.id)
            )
            
            # Step 3: Transfer funds to customer account
            transfer = await self.payment_service.transfer_funds(
                from_account=self.treasury_account,
                to_account=loan.customer_account,
                amount=loan.amount
            )
            compensation_actions.append(
                lambda: self.payment_service.reverse_transfer(transfer.id)
            )
            
            # Step 4: Update loan status
            await self.loan_repo.mark_disbursed(loan_id)
            
            return disbursement
            
        except Exception as e:
            # Execute compensation actions in reverse order
            for action in reversed(compensation_actions):
                try:
                    await action()
                except Exception as comp_error:
                    self.logger.error(f"Compensation failed: {comp_error}")
            
            raise LoanDisbursementError(f"Loan disbursement failed: {e}")
```

## Testing Patterns

### 10. Test Context Pattern

**Problem**: How to test components in isolation while maintaining integration testing.

**Solution**: Use test-specific contexts with mocks and test doubles.

```python title="Test Context Pattern"
# Production context
@og_context(
    name="payment_processing",
    imports=[
        ModuleContextImport(DatabasePool, from_context="infrastructure"),
        ModuleContextImport(VelocityPayGateway, from_context="infrastructure")
    ]
)
class PaymentProcessingModule:
    pass

# Test context with mocks
@og_context(
    name="payment_processing_test",
    providers=[
        MockDatabasePool,           # Test double
        MockVelocityPayGateway,     # Test double
        PaymentService,             # Real service under test
        PaymentRepository,          # Real repository
    ]
)
class PaymentProcessingTestModule:
    pass

class TestPaymentService:
    
    async def test_payment_processing(self):
        """Test payment service with test context"""
        
        # Create test context
        builder = ContextModuleBuilder()
        contexts = await builder.build_contexts(PaymentProcessingTestModule)
        
        payment_service = contexts["payment_processing_test"].resolve(PaymentService)
        
        # Configure mocks
        velocity_gateway = contexts["payment_processing_test"].resolve(MockVelocityPayGateway)
        velocity_gateway.configure_success_response({
            'transaction_id': 'test_txn_123',
            'status': 'completed'
        })
        
        # Test the service
        result = await payment_service.process_payment(test_payment)
        
        assert result.status == 'completed'
        assert velocity_gateway.process_payment_called
```

## Performance Patterns

### 11. Caching Pattern

**Problem**: How to improve performance while maintaining data consistency.

**Solution**: Implement multi-level caching with proper invalidation.

```python title="Multi-Level Caching Pattern"
@og_component()
class CachedCustomerService(BaseComponent):
    """Customer service with multi-level caching"""
    
    def __init__(
        self,
        customer_repo: CustomerRepository,
        l1_cache: LocalCache,      # In-memory cache
        l2_cache: RedisCache,      # Distributed cache
        event_bus: EventBus
    ) -> None:
        super().__init__()
        self.customer_repo = customer_repo
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache
        self.event_bus = event_bus
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer with multi-level caching"""
        
        # L1 Cache (in-memory)
        customer = await self.l1_cache.get(f"customer:{customer_id}")
        if customer:
            return customer
        
        # L2 Cache (Redis)
        customer_data = await self.l2_cache.get(f"customer:{customer_id}")
        if customer_data:
            customer = Customer.from_json(customer_data)
            # Populate L1 cache
            await self.l1_cache.set(f"customer:{customer_id}", customer, ttl=300)
            return customer
        
        # Database
        customer = await self.customer_repo.get_by_id(customer_id)
        if customer:
            # Populate both cache levels
            await self.l2_cache.set(f"customer:{customer_id}", customer.to_json(), ttl=3600)
            await self.l1_cache.set(f"customer:{customer_id}", customer, ttl=300)
        
        return customer
    
    async def update_customer(self, customer: Customer) -> Customer:
        """Update customer with cache invalidation"""
        
        # Update in database
        updated_customer = await self.customer_repo.save(customer)
        
        # Invalidate all cache levels
        await self.l1_cache.delete(f"customer:{customer.id}")
        await self.l2_cache.delete(f"customer:{customer.id}")
        
        # Publish cache invalidation event for other instances
        await self.event_bus.publish(CustomerUpdatedEvent(
            customer_id=customer.id,
            updated_at=datetime.utcnow()
        ))
        
        return updated_customer
```

### 12. Async Batch Processing Pattern

**Problem**: How to efficiently process large volumes of data.

**Solution**: Use async batch processing with concurrency control.

```python title="Async Batch Processing"
@og_component()
class InterestBatchProcessor(BaseComponent):
    """Batch processor for daily interest calculation"""
    
    def __init__(
        self,
        account_repo: AccountRepository,
        interest_calculator: InterestCalculator,
        semaphore_limit: int = 50  # Concurrency limit
    ) -> None:
        super().__init__()
        self.account_repo = account_repo
        self.interest_calculator = interest_calculator
        self.semaphore = asyncio.Semaphore(semaphore_limit)
    
    async def process_daily_interest(self) -> BatchResult:
        """Process daily interest for all accounts"""
        
        self.logger.info("Starting daily interest calculation batch")
        
        # Get all eligible accounts in batches
        batch_size = 1000
        processed_count = 0
        error_count = 0
        
        async for account_batch in self._get_accounts_in_batches(batch_size):
            # Process batch concurrently
            tasks = [
                self._process_account_interest(account)
                for account in account_batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            for result in results:
                if isinstance(result, Exception):
                    error_count += 1
                    self.logger.error(f"Interest calculation failed: {result}")
                else:
                    processed_count += 1
        
        self.logger.info(f"Interest calculation complete: {processed_count} processed, {error_count} errors")
        
        return BatchResult(
            processed_count=processed_count,
            error_count=error_count,
            batch_duration=time.time() - start_time
        )
    
    async def _process_account_interest(self, account: Account) -> None:
        """Process interest for single account with concurrency control"""
        
        async with self.semaphore:  # Limit concurrency
            try:
                interest = await self.interest_calculator.calculate_daily_interest(account)
                
                if interest > 0:
                    await self.account_repo.credit_interest(account.id, interest)
                
            except Exception as e:
                raise InterestCalculationError(f"Failed to calculate interest for {account.id}: {e}")
```

## Security Patterns

### 13. Data Access Control Pattern

**Problem**: How to implement fine-grained access control for sensitive data.

**Solution**: Use component-level access control with context propagation.

```python title="Data Access Control Pattern"
@dataclass
class SecurityContext:
    """Security context for access control"""
    user_id: str
    roles: List[str]
    permissions: List[str]
    customer_id: Optional[str] = None  # For customer-scoped access

@og_component()
class SecureCustomerService(BaseComponent):
    """Customer service with access control"""
    
    def __init__(
        self,
        customer_repo: CustomerRepository,
        access_control: AccessControlService
    ) -> None:
        super().__init__()
        self.customer_repo = customer_repo
        self.access_control = access_control
    
    async def get_customer(
        self,
        customer_id: str,
        security_context: SecurityContext
    ) -> Optional[Customer]:
        """Get customer with access control"""
        
        # Check permissions
        if not await self.access_control.can_access_customer(security_context, customer_id):
            raise AccessDeniedError(f"User {security_context.user_id} cannot access customer {customer_id}")
        
        customer = await self.customer_repo.get_by_id(customer_id)
        
        # Apply data filtering based on permissions
        if customer:
            customer = await self.access_control.filter_customer_data(customer, security_context)
        
        return customer

@og_component()
class AccessControlService(BaseComponent):
    """Centralized access control logic"""
    
    async def can_access_customer(self, context: SecurityContext, customer_id: str) -> bool:
        """Check if user can access customer data"""
        
        # Admin can access all customers
        if "admin" in context.roles:
            return True
        
        # Customer can access their own data
        if context.customer_id == customer_id:
            return True
        
        # Relationship manager can access assigned customers
        if "relationship_manager" in context.roles:
            return await self._is_assigned_customer(context.user_id, customer_id)
        
        return False
```

These patterns represent battle-tested approaches used in production at OgPgy Bank. They solve real-world problems while maintaining clean architecture principles and OpusGenie DI best practices.