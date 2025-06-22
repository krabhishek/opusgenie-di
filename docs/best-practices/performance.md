# Performance Optimization

*Jake Morrison's guide to building high-performance banking systems*

---

!!! quote "Jake Morrison - DevOps Engineer"
    *"At OgPgy Bank, we process thousands of transactions per second with sub-100ms latency. Here's how we optimized OpusGenie DI for maximum performance."*

## Performance Optimization Strategies

### Component Initialization Performance

```python title="Optimized Component Initialization"
@og_component(scope=ComponentScope.SINGLETON)
class OptimizedDatabasePool(BaseComponent):
    """Database pool optimized for fast startup and high throughput"""
    
    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__()
        self.config = config
        self.pool = None
        self._startup_cache = {}
    
    async def initialize(self) -> None:
        """Optimized initialization with connection pre-warming"""
        start_time = time.time()
        
        # Parallel initialization of multiple components
        tasks = [
            self._create_connection_pool(),
            self._warm_connection_cache(),
            self._prepare_statements()
        ]
        
        await asyncio.gather(*tasks)
        
        init_time = time.time() - start_time
        self.logger.info(f"⚡ Database pool initialized in {init_time:.3f}s")
    
    async def _create_connection_pool(self) -> None:
        """Create optimized connection pool"""
        self.pool = await asyncpg.create_pool(
            **self.config.connection_params,
            # Performance optimizations
            min_size=20,           # Warm pool
            max_size=100,          # Scale under load
            max_queries=50000,     # Connection recycling
            max_inactive_connection_lifetime=3600,
            command_timeout=30,
            # Prepared statement caching
            server_settings={
                'application_name': 'ogpgy_bank_optimized',
                'shared_preload_libraries': 'pg_stat_statements'
            }
        )
    
    async def _warm_connection_cache(self) -> None:
        """Pre-warm connection cache for faster first requests"""
        if not self.pool:
            return
        
        # Pre-create some connections
        connections = []
        for _ in range(5):  # Warm 5 connections
            conn = await self.pool.acquire()
            connections.append(conn)
        
        # Release them back to pool (now warmed)
        for conn in connections:
            await self.pool.release(conn)
    
    async def _prepare_statements(self) -> None:
        """Pre-prepare frequently used statements"""
        if not self.pool:
            return
        
        async with self.pool.acquire() as conn:
            # Prepare high-frequency queries
            await conn.execute("PREPARE get_account AS SELECT * FROM accounts WHERE id = $1")
            await conn.execute("PREPARE get_customer AS SELECT * FROM customers WHERE id = $1")
            await conn.execute("PREPARE update_balance AS UPDATE accounts SET balance = $2 WHERE id = $1")
```

### Caching Strategies

```python title="High-Performance Caching"
@og_component(scope=ComponentScope.SINGLETON)
class PerformantCacheService(BaseComponent):
    """Multi-tier caching for maximum performance"""
    
    def __init__(self, redis_config: RedisConfig) -> None:
        super().__init__()
        self.redis_config = redis_config
        
        # L1: In-memory cache (fastest)
        self.l1_cache = {}
        self.l1_max_size = 10000
        self.l1_stats = {'hits': 0, 'misses': 0}
        
        # L2: Redis cache (fast, distributed)
        self.redis_pool = None
        self.l2_stats = {'hits': 0, 'misses': 0}
        
        # Cache warming
        self.warm_cache_keys = [
            'active_customers',
            'account_types',
            'interest_rates',
            'fee_schedules'
        ]
    
    async def initialize(self) -> None:
        """Initialize cache with performance optimizations"""
        await super().initialize()
        
        # Create optimized Redis connection pool
        self.redis_pool = redis.ConnectionPool(
            host=self.redis_config.host,
            port=self.redis_config.port,
            password=self.redis_config.password,
            max_connections=50,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30
        )
        
        # Warm critical caches
        await self._warm_critical_caches()
        
        # Start background cache maintenance
        asyncio.create_task(self._cache_maintenance_loop())
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with L1->L2->Database fallback"""
        
        # L1 Cache (in-memory) - fastest
        if key in self.l1_cache:
            self.l1_stats['hits'] += 1
            item = self.l1_cache[key]
            if time.time() < item['expires']:
                return item['value']
            else:
                del self.l1_cache[key]  # Expired
        
        self.l1_stats['misses'] += 1
        
        # L2 Cache (Redis) - fast
        redis_conn = redis.Redis(connection_pool=self.redis_pool)
        try:
            value = await redis_conn.get(key)
            if value:
                self.l2_stats['hits'] += 1
                
                # Deserialize and populate L1
                deserialized = pickle.loads(value)
                await self._set_l1(key, deserialized, ttl=300)  # 5 min L1 TTL
                
                return deserialized
        except Exception as e:
            self.logger.warning(f"L2 cache miss: {e}")
        
        self.l2_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in both cache levels"""
        
        # Set in L2 (Redis) first
        redis_conn = redis.Redis(connection_pool=self.redis_pool)
        try:
            serialized = pickle.dumps(value)
            await redis_conn.setex(key, ttl, serialized)
        except Exception as e:
            self.logger.error(f"L2 cache set failed: {e}")
        
        # Set in L1 (memory)
        await self._set_l1(key, value, ttl=min(ttl, 300))  # Max 5 min in L1
    
    async def _set_l1(self, key: str, value: Any, ttl: int) -> None:
        """Set value in L1 cache with size management"""
        
        # Evict if cache is full
        if len(self.l1_cache) >= self.l1_max_size:
            # Simple LRU: remove oldest entry
            oldest_key = min(self.l1_cache.keys(), 
                           key=lambda k: self.l1_cache[k]['accessed'])
            del self.l1_cache[oldest_key]
        
        self.l1_cache[key] = {
            'value': value,
            'expires': time.time() + ttl,
            'accessed': time.time()
        }
    
    async def _warm_critical_caches(self) -> None:
        """Pre-warm critical cache entries"""
        
        warming_tasks = []
        for cache_key in self.warm_cache_keys:
            warming_tasks.append(self._warm_cache_entry(cache_key))
        
        await asyncio.gather(*warming_tasks, return_exceptions=True)
        self.logger.info(f"🔥 Warmed {len(self.warm_cache_keys)} critical cache entries")
    
    async def _cache_maintenance_loop(self) -> None:
        """Background cache maintenance for optimal performance"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # L1 cache cleanup (remove expired entries)
                current_time = time.time()
                expired_keys = [
                    k for k, v in self.l1_cache.items()
                    if current_time >= v['expires']
                ]
                
                for key in expired_keys:
                    del self.l1_cache[key]
                
                # Log cache statistics
                total_l1 = self.l1_stats['hits'] + self.l1_stats['misses']
                total_l2 = self.l2_stats['hits'] + self.l2_stats['misses']
                
                if total_l1 > 0:
                    l1_hit_rate = self.l1_stats['hits'] / total_l1 * 100
                    l2_hit_rate = self.l2_stats['hits'] / total_l2 * 100 if total_l2 > 0 else 0
                    
                    self.logger.debug(
                        f"📊 Cache stats: L1 {l1_hit_rate:.1f}% hit rate, "
                        f"L2 {l2_hit_rate:.1f}% hit rate, "
                        f"L1 size: {len(self.l1_cache)}"
                    )
                
            except Exception as e:
                self.logger.error(f"Cache maintenance error: {e}")
```

### Async Performance Optimization

```python title="High-Performance Async Operations"
@og_component(scope=ComponentScope.SINGLETON)
class OptimizedPaymentService(BaseComponent):
    """Payment service optimized for high throughput"""
    
    def __init__(
        self,
        account_service: AccountService,
        velocity_gateway: VelocityPayGateway,
        fraud_detector: FraudDetectionService,
        db_pool: DatabasePool
    ) -> None:
        super().__init__()
        self.account_service = account_service
        self.velocity_gateway = velocity_gateway
        self.fraud_detector = fraud_detector
        self.db_pool = db_pool
        
        # Performance optimization settings
        self.batch_size = 100
        self.max_concurrent_payments = 50
        self.semaphore = asyncio.Semaphore(self.max_concurrent_payments)
        
        # Connection pooling for external services
        self.http_session = None
    
    async def initialize(self) -> None:
        """Initialize with performance optimizations"""
        await super().initialize()
        
        # Create optimized HTTP session for external APIs
        connector = aiohttp.TCPConnector(
            limit=100,              # Total connection pool size
            limit_per_host=20,      # Per-host connection limit
            keepalive_timeout=30,   # Keep connections alive
            enable_cleanup_closed=True
        )
        
        self.http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30),
            # Connection reuse headers
            headers={'Connection': 'keep-alive'}
        )
    
    async def process_payment_batch(self, payments: List[Payment]) -> List[PaymentResult]:
        """Process payments in optimized batches"""
        
        self.logger.info(f"⚡ Processing batch of {len(payments)} payments")
        start_time = time.time()
        
        # Process in chunks to avoid overwhelming external services
        results = []
        for i in range(0, len(payments), self.batch_size):
            batch = payments[i:i + self.batch_size]
            
            # Process batch concurrently with semaphore control
            batch_tasks = [
                self._process_single_payment_optimized(payment)
                for payment in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Small delay between batches to be respectful to external services
            if i + self.batch_size < len(payments):
                await asyncio.sleep(0.1)
        
        processing_time = time.time() - start_time
        throughput = len(payments) / processing_time
        
        self.logger.info(
            f"✅ Batch complete: {len(payments)} payments in {processing_time:.3f}s "
            f"({throughput:.1f} payments/sec)"
        )
        
        return results
    
    async def _process_single_payment_optimized(self, payment: Payment) -> PaymentResult:
        """Process single payment with performance optimizations"""
        
        async with self.semaphore:  # Limit concurrency
            try:
                # Parallel validation and fraud check
                validation_task = self._validate_payment_fast(payment)
                fraud_task = self._check_fraud_fast(payment)
                
                # Wait for both to complete
                validation_result, fraud_result = await asyncio.gather(
                    validation_task, fraud_task
                )
                
                if not validation_result.valid:
                    return PaymentResult.failed(validation_result.reason)
                
                if not fraud_result.approved:
                    return PaymentResult.rejected(f"Fraud detected: {fraud_result.risk_score}")
                
                # Process through VelocityPay
                velocity_result = await self.velocity_gateway.process_payment_optimized(payment)
                
                # Update account balances in parallel
                await asyncio.gather(
                    self.account_service.debit_account_fast(payment.from_account, payment.amount),
                    self.account_service.credit_account_fast(payment.to_account, payment.amount)
                )
                
                return PaymentResult.success(velocity_result.transaction_id)
                
            except Exception as e:
                self.logger.error(f"Payment processing failed: {e}")
                return PaymentResult.failed(str(e))
    
    async def _validate_payment_fast(self, payment: Payment) -> ValidationResult:
        """Fast payment validation with caching"""
        
        # Use cached account information when possible
        cache_key = f"account_validation:{payment.from_account}"
        cached_validation = await self.cache.get(cache_key)
        
        if cached_validation and cached_validation['expires'] > time.time():
            return ValidationResult(valid=True, cached=True)
        
        # Parallel account validation
        from_account_task = self.account_service.get_account_fast(payment.from_account)
        to_account_task = self.account_service.get_account_fast(payment.to_account)
        
        from_account, to_account = await asyncio.gather(from_account_task, to_account_task)
        
        # Fast validation logic
        if not from_account or not to_account:
            return ValidationResult(valid=False, reason="Account not found")
        
        if from_account.balance < payment.amount:
            return ValidationResult(valid=False, reason="Insufficient funds")
        
        # Cache validation result
        await self.cache.set(cache_key, {
            'valid': True,
            'expires': time.time() + 60  # Cache for 1 minute
        })
        
        return ValidationResult(valid=True)
```

### Database Performance Optimization

```python title="Database Performance Patterns"
@og_component()
class HighPerformanceAccountRepository(BaseComponent):
    """Account repository optimized for high-frequency operations"""
    
    def __init__(self, db_pool: DatabasePool) -> None:
        super().__init__()
        self.db_pool = db_pool
        
        # Prepared statement cache
        self.prepared_statements = {}
        
        # Batch operation settings
        self.batch_insert_size = 1000
        self.batch_update_size = 500
    
    async def initialize(self) -> None:
        """Initialize with prepared statements for performance"""
        await super().initialize()
        
        async with self.db_pool.acquire() as conn:
            # Prepare frequently used statements
            self.prepared_statements = {
                'get_account': await conn.prepare(
                    "SELECT * FROM accounts WHERE id = $1"
                ),
                'update_balance': await conn.prepare(
                    "UPDATE accounts SET balance = $2, available_balance = $3, "
                    "last_transaction_at = $4 WHERE id = $1"
                ),
                'get_customer_accounts': await conn.prepare(
                    "SELECT * FROM accounts WHERE customer_id = $1 AND status = 'active'"
                ),
                'insert_transaction': await conn.prepare(
                    "INSERT INTO account_transactions (id, account_id, amount, type, "
                    "balance_after, created_at) VALUES ($1, $2, $3, $4, $5, $6)"
                )
            }
    
    async def get_account_fast(self, account_id: str) -> Optional[Account]:
        """Optimized account retrieval"""
        
        async with self.db_pool.acquire() as conn:
            # Use prepared statement for better performance
            stmt = self.prepared_statements['get_account']
            row = await stmt.fetchrow(account_id)
            
            if row:
                return self._row_to_account(row)
            return None
    
    async def update_balances_batch(self, balance_updates: List[BalanceUpdate]) -> None:
        """Batch balance updates for high throughput"""
        
        if not balance_updates:
            return
        
        async with self.db_pool.acquire() as conn:
            # Use transaction for consistency
            async with conn.transaction():
                stmt = self.prepared_statements['update_balance']
                
                # Batch execute for better performance
                await stmt.executemany([
                    (update.account_id, update.new_balance, update.new_available_balance, 
                     datetime.utcnow())
                    for update in balance_updates
                ])
        
        self.logger.debug(f"⚡ Updated {len(balance_updates)} account balances in batch")
    
    async def get_accounts_by_criteria_optimized(
        self,
        criteria: Dict[str, Any],
        limit: int = 1000
    ) -> List[Account]:
        """Optimized account search with indexing hints"""
        
        # Build optimized query with proper indexing
        where_conditions = []
        params = []
        
        if 'customer_id' in criteria:
            where_conditions.append(f"customer_id = ${len(params) + 1}")
            params.append(criteria['customer_id'])
        
        if 'account_type' in criteria:
            where_conditions.append(f"account_type = ${len(params) + 1}")
            params.append(criteria['account_type'])
        
        if 'status' in criteria:
            where_conditions.append(f"status = ${len(params) + 1}")
            params.append(criteria['status'])
        
        # Optimized query with index hints
        query = f"""
            SELECT /*+ INDEX(accounts, idx_accounts_customer_status) */ *
            FROM accounts
            WHERE {' AND '.join(where_conditions)}
            ORDER BY created_at DESC
            LIMIT ${len(params) + 1}
        """
        params.append(limit)
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_account(row) for row in rows]
```

### Monitoring and Metrics

```python title="Performance Monitoring"
@og_component()
class PerformanceMonitor(BaseComponent):
    """Real-time performance monitoring for optimization"""
    
    def __init__(self) -> None:
        super().__init__()
        self.metrics = {}
        self.performance_thresholds = {
            'payment_processing_ms': 100,    # 100ms threshold
            'account_lookup_ms': 50,         # 50ms threshold
            'database_query_ms': 30,         # 30ms threshold
            'cache_hit_rate_percent': 80     # 80% hit rate threshold
        }
    
    @contextmanager
    def measure_operation(self, operation_name: str):
        """Context manager for measuring operation performance"""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(operation_name, duration_ms)
            
            # Alert if performance threshold exceeded
            threshold_key = f"{operation_name}_ms"
            if threshold_key in self.performance_thresholds:
                threshold = self.performance_thresholds[threshold_key]
                if duration_ms > threshold:
                    self.logger.warning(
                        f"⚠️ Performance threshold exceeded: {operation_name} "
                        f"took {duration_ms:.1f}ms (threshold: {threshold}ms)"
                    )
    
    def _record_metric(self, operation_name: str, duration_ms: float) -> None:
        """Record performance metric"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'recent_times': []
            }
        
        metric = self.metrics[operation_name]
        metric['count'] += 1
        metric['total_time'] += duration_ms
        metric['min_time'] = min(metric['min_time'], duration_ms)
        metric['max_time'] = max(metric['max_time'], duration_ms)
        
        # Keep recent times for percentile calculations
        metric['recent_times'].append(duration_ms)
        if len(metric['recent_times']) > 1000:  # Keep last 1000 measurements
            metric['recent_times'] = metric['recent_times'][-1000:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        report = {}
        
        for operation, metric in self.metrics.items():
            if metric['count'] > 0:
                avg_time = metric['total_time'] / metric['count']
                
                # Calculate percentiles
                recent_times = sorted(metric['recent_times'])
                p50 = recent_times[len(recent_times) // 2] if recent_times else 0
                p95 = recent_times[int(len(recent_times) * 0.95)] if recent_times else 0
                p99 = recent_times[int(len(recent_times) * 0.99)] if recent_times else 0
                
                report[operation] = {
                    'count': metric['count'],
                    'avg_ms': round(avg_time, 2),
                    'min_ms': round(metric['min_time'], 2),
                    'max_ms': round(metric['max_time'], 2),
                    'p50_ms': round(p50, 2),
                    'p95_ms': round(p95, 2),
                    'p99_ms': round(p99, 2)
                }
        
        return report

# Usage example
async def optimized_payment_processing():
    """Example of using performance monitoring"""
    
    monitor = PerformanceMonitor()
    payment_service = OptimizedPaymentService()
    
    # Measure payment processing performance
    with monitor.measure_operation('payment_processing'):
        result = await payment_service.process_payment(payment)
    
    # Measure database operations
    with monitor.measure_operation('account_lookup'):
        account = await account_service.get_account_fast(account_id)
    
    # Generate performance report
    report = monitor.get_performance_report()
    logger.info(f"📊 Performance report: {report}")
```

## Performance Best Practices Summary

!!! tip "Key Performance Optimization Strategies"
    
    **Component Design:**
    - Use singleton scope for expensive-to-create components
    - Initialize components in parallel when possible
    - Implement proper cleanup to prevent resource leaks
    - Use connection pooling for databases and external services
    
    **Caching:**
    - Implement multi-level caching (L1/L2)
    - Use appropriate TTLs based on data volatility
    - Implement cache warming for critical data
    - Monitor cache hit rates and optimize accordingly
    
    **Async Operations:**
    - Use asyncio.gather() for parallel operations
    - Implement concurrency limits with semaphores
    - Batch operations when possible
    - Use prepared statements for database operations
    
    **Monitoring:**
    - Monitor performance metrics continuously
    - Set performance thresholds and alerts
    - Use profiling tools to identify bottlenecks
    - Implement distributed tracing for complex operations

These performance optimizations have enabled OgPgy Bank to achieve:
- **Sub-100ms** payment processing latency
- **>99.9%** system availability
- **1000+** transactions per second throughput
- **<5s** system startup time

The key is to measure everything, optimize based on real bottlenecks, and continuously monitor performance in production.