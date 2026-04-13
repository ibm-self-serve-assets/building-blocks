# Scalability & Performance Review Skill

## Purpose
Evaluate system capacity, identify bottlenecks, and provide performance optimization recommendations.

## Expertise Areas
- Horizontal and vertical scaling strategies
- Load balancing and distribution
- Caching strategies (CDN, application, database)
- Database optimization and indexing
- Asynchronous processing and message queues
- Performance benchmarking and profiling
- Capacity planning
- SLA and SLO definition
- Content Delivery Networks (CDN)
- Auto-scaling and elasticity

## Review Process

### 1. Current Load Analysis
- What is the current traffic volume?
- What are the peak load patterns?
- What is the growth trajectory?
- What are the resource utilization metrics (CPU, memory, disk, network)?
- What are the current response times?

### 2. Scaling Strategy Assessment

**Horizontal Scaling (Scale Out)**
- Can the application scale horizontally?
- Are there stateless components?
- How is session management handled?
- Is there a load balancer?
- How are instances added/removed?

**Vertical Scaling (Scale Up)**
- What are the vertical scaling limits?
- Are there resource bottlenecks?
- Is vertical scaling cost-effective?
- What is the maximum instance size?

**Auto-Scaling**
- Is auto-scaling configured?
- What are the scaling triggers?
- What are the scaling policies?
- How quickly can the system scale?

### 3. Load Balancing
- What load balancing strategy is used (round-robin, least connections, IP hash)?
- Is there health checking?
- How is traffic distributed across regions?
- Is there session affinity/sticky sessions?
- Are there circuit breakers?

### 4. Caching Strategy

**CDN Caching**
- Is static content cached at the edge?
- What is the cache hit ratio?
- What is the cache invalidation strategy?

**Application Caching**
- What caching technology is used (Redis, Memcached)?
- What data is cached?
- What is the cache eviction policy?
- How is cache consistency maintained?

**Database Caching**
- Is there query result caching?
- Are there materialized views?
- Is there read replica caching?

### 5. Database Performance

**Query Optimization**
- Are queries optimized?
- Are there proper indexes?
- Are there N+1 query problems?
- Is there query result pagination?

**Database Scaling**
- Is there read/write splitting?
- Are there read replicas?
- Is there database sharding?
- Is there connection pooling?

**Database Technology**
- Is the right database type used (SQL vs. NoSQL)?
- Are there polyglot persistence patterns?
- Is there database partitioning?

### 6. Asynchronous Processing
- Are long-running tasks asynchronous?
- Is there a message queue (RabbitMQ, Kafka, SQS)?
- Are there background workers?
- How is task retry handled?
- Is there dead letter queue handling?

### 7. API Performance
- What are the API response times?
- Is there API rate limiting?
- Is there API throttling?
- Are there bulk operations?
- Is there GraphQL query complexity limiting?

### 8. Network Performance
- What is the network latency?
- Is there geographic distribution?
- Are there multiple availability zones?
- Is there edge computing?
- What is the bandwidth utilization?

### 9. Resource Optimization
- Are resources right-sized?
- Is there resource waste?
- Are there cost optimization opportunities?
- Is there serverless consideration?

## Performance Metrics

### Response Time Metrics
- **p50 (median)**: 50th percentile response time
- **p95**: 95th percentile response time
- **p99**: 99th percentile response time
- **p99.9**: 99.9th percentile response time

### Throughput Metrics
- Requests per second (RPS)
- Transactions per second (TPS)
- Messages per second

### Resource Metrics
- CPU utilization
- Memory utilization
- Disk I/O
- Network I/O
- Database connections

### Availability Metrics
- Uptime percentage
- Mean Time Between Failures (MTBF)
- Mean Time To Recovery (MTTR)
- Error rate

## Output Format

### ✅ Achieved
- List effective scaling mechanisms
- Highlight good performance optimizations
- Note successful caching strategies
- Identify well-optimized components

### ⚠️ Concerns
- Potential bottlenecks
- Scalability limitations
- Performance risks
- Resource inefficiencies

### ❌ Not Achieved
- Critical scalability gaps
- Performance issues
- Unmet response time goals
- Resource constraints

### 📊 Performance Metrics Table
| Metric | Target | Current | Status | Notes |
|--------|--------|---------|--------|-------|
| Response Time (p95) | [target] | [current] | ✅/⚠️/❌ | [notes] |
| Throughput (RPS) | [target] | [current] | ✅/⚠️/❌ | [notes] |
| Concurrent Users | [target] | [current] | ✅/⚠️/❌ | [notes] |
| CPU Utilization | [target] | [current] | ✅/⚠️/❌ | [notes] |
| Memory Utilization | [target] | [current] | ✅/⚠️/❌ | [notes] |
| Error Rate | [target] | [current] | ✅/⚠️/❌ | [notes] |

### 💡 Recommendations
For each performance issue:
- **Priority**: Critical/High/Medium/Low
- **Bottleneck**: Specific performance bottleneck
- **Solution**: Optimization approach
- **Expected Improvement**: Performance gain estimate
- **Effort**: Implementation complexity
- **Cost Impact**: Infrastructure cost changes

## Key Questions to Answer
1. Can the system handle expected growth?
2. What are the current bottlenecks?
3. Are response times meeting SLAs?
4. Is the caching strategy effective?
5. Can the system scale cost-effectively?
6. Are there single points of failure?
7. Is the database optimized?
8. Are resources efficiently utilized?

## Performance Testing Checklist
- [ ] Load testing performed
- [ ] Stress testing performed
- [ ] Spike testing performed
- [ ] Endurance testing performed
- [ ] Scalability testing performed
- [ ] Performance baselines established
- [ ] Performance monitoring in place
- [ ] Alerting configured for performance issues
- [ ] Performance budgets defined
- [ ] Regular performance reviews scheduled

## Common Performance Anti-Patterns
- ❌ N+1 query problems
- ❌ Missing database indexes
- ❌ Synchronous processing of long tasks
- ❌ No caching strategy
- ❌ Single point of failure
- ❌ No connection pooling
- ❌ Inefficient serialization
- ❌ Memory leaks
- ❌ Blocking I/O operations
- ❌ Over-fetching data