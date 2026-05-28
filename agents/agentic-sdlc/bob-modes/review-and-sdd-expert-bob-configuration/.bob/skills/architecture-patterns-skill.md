# Architecture Patterns & Best Practices Review Skill

## Purpose
Evaluate pattern usage, identify anti-patterns, and recommend appropriate architectural patterns.

## Expertise Areas
- Microservices vs. Monolith architecture
- CQRS (Command Query Responsibility Segregation)
- Event Sourcing and Event-Driven Architecture
- Domain-Driven Design (DDD)
- SOLID principles
- Design patterns (Gang of Four, Enterprise patterns)
- API design (REST, GraphQL, gRPC)
- Service mesh and API gateway patterns
- Hexagonal Architecture (Ports and Adapters)
- Clean Architecture

## Review Process

### 1. Architecture Style Assessment

**Monolithic Architecture**
- Is a monolith appropriate for this use case?
- Is the monolith modular?
- Are there clear boundaries?
- Is there a migration path to microservices if needed?

**Microservices Architecture**
- Are service boundaries well-defined?
- Is there proper service decomposition?
- How is inter-service communication handled?
- Is there service discovery?
- How is distributed tracing implemented?
- Are there circuit breakers?
- How is data consistency managed?

**Serverless Architecture**
- Are functions appropriately sized?
- Is cold start managed?
- Are there proper timeout configurations?
- Is there function composition?

### 2. CQRS Pattern
- Are commands and queries separated?
- Is there separate read and write models?
- How is eventual consistency handled?
- Are there appropriate use cases for CQRS?

### 3. Event-Driven Architecture
- What events are published?
- Is there an event bus/broker?
- How is event schema managed?
- Is there event versioning?
- How is event ordering handled?
- Are there event replay capabilities?
- Is there event sourcing?

### 4. Domain-Driven Design (DDD)

**Strategic Design**
- Are bounded contexts identified?
- Is there a context map?
- How are contexts integrated?
- Is there an ubiquitous language?

**Tactical Design**
- Are there aggregates?
- Are entities and value objects distinguished?
- Are domain events used?
- Are repositories implemented?
- Are domain services identified?

### 5. SOLID Principles

**Single Responsibility Principle (SRP)**
- Does each class have one reason to change?
- Are responsibilities clearly defined?
- Is there proper separation of concerns?

**Open/Closed Principle (OCP)**
- Is code open for extension, closed for modification?
- Are there proper abstractions?
- Is there use of interfaces and abstract classes?

**Liskov Substitution Principle (LSP)**
- Can derived classes substitute base classes?
- Are there proper inheritance hierarchies?
- Are there interface segregation issues?

**Interface Segregation Principle (ISP)**
- Are interfaces focused and cohesive?
- Are there fat interfaces?
- Do clients depend on methods they don't use?

**Dependency Inversion Principle (DIP)**
- Do high-level modules depend on abstractions?
- Is there dependency injection?
- Are dependencies properly managed?

### 6. Design Patterns Assessment

**Creational Patterns**
- Factory Pattern: Object creation abstraction
- Builder Pattern: Complex object construction
- Singleton Pattern: Single instance management
- Prototype Pattern: Object cloning

**Structural Patterns**
- Adapter Pattern: Interface compatibility
- Decorator Pattern: Dynamic behavior addition
- Facade Pattern: Simplified interface
- Proxy Pattern: Access control

**Behavioral Patterns**
- Strategy Pattern: Algorithm encapsulation
- Observer Pattern: Event notification
- Command Pattern: Request encapsulation
- Template Method: Algorithm skeleton

**Enterprise Patterns**
- Repository Pattern: Data access abstraction
- Unit of Work: Transaction management
- Service Layer: Business logic encapsulation
- Data Transfer Object (DTO): Data transfer

### 7. API Design

**REST API**
- Are REST principles followed?
- Is there proper resource modeling?
- Are HTTP methods used correctly?
- Is there proper status code usage?
- Is there API versioning?
- Is there HATEOAS?
- Is there proper error handling?

**GraphQL API**
- Is the schema well-designed?
- Are there proper resolvers?
- Is there query complexity limiting?
- Is there N+1 query prevention?
- Is there proper error handling?

**gRPC API**
- Are protocol buffers well-defined?
- Is there proper service definition?
- Is there streaming where appropriate?
- Is there proper error handling?

### 8. Integration Patterns
- Point-to-Point vs. Publish-Subscribe
- Request-Reply vs. Fire-and-Forget
- Synchronous vs. Asynchronous
- API Gateway pattern
- Backend for Frontend (BFF) pattern
- Strangler Fig pattern (for migration)

### 9. Data Patterns
- Database per Service
- Shared Database (anti-pattern in microservices)
- Saga Pattern (distributed transactions)
- Event Sourcing
- CQRS with separate data stores
- Polyglot Persistence

### 10. Resilience Patterns
- Circuit Breaker
- Retry with exponential backoff
- Bulkhead
- Timeout
- Fallback
- Health Check

## Output Format

### ✅ Achieved
- List patterns appropriately used
- Highlight good design principles
- Note industry standards followed
- Identify well-structured components

### ⚠️ Concerns
- Pattern misuse or overuse
- Principle violations
- Deviation from standards
- Complexity issues

### ❌ Not Achieved
- Missing critical patterns
- Anti-patterns identified
- Significant principle violations
- Poor architectural decisions

### 🏗️ Pattern Analysis Table
| Pattern/Practice | Usage | Assessment | Notes |
|-----------------|-------|------------|-------|
| Microservices | ✅ Used | ⭐⭐⭐⭐☆ | Well-bounded services |
| CQRS | ❌ Not Used | N/A | Consider for read-heavy workloads |
| Event Sourcing | ⚠️ Partial | ⭐⭐⭐☆☆ | Missing event replay |
| DDD | ✅ Used | ⭐⭐⭐⭐⭐ | Clear bounded contexts |
| Repository Pattern | ✅ Used | ⭐⭐⭐⭐☆ | Good data abstraction |
| Circuit Breaker | ❌ Not Used | N/A | Critical for resilience |

### 💡 Recommendations
For each pattern issue:
- **Priority**: Critical/High/Medium/Low
- **Current State**: What's currently implemented
- **Proposed Pattern**: Recommended pattern
- **Benefits**: Expected improvements
- **Trade-offs**: Considerations and costs
- **Implementation**: Specific steps

## Key Questions to Answer
1. Are architectural patterns appropriate for the use case?
2. Are SOLID principles followed?
3. Are there anti-patterns in use?
4. Is the API design consistent and well-structured?
5. Are resilience patterns implemented?
6. Is the architecture maintainable and extensible?
7. Are integration patterns appropriate?
8. Is there proper separation of concerns?

## Common Anti-Patterns to Avoid
- ❌ **God Object**: Class that knows/does too much
- ❌ **Spaghetti Code**: Tangled, unstructured code
- ❌ **Golden Hammer**: Using one pattern for everything
- ❌ **Lava Flow**: Dead code that's never removed
- ❌ **Cargo Cult Programming**: Using patterns without understanding
- ❌ **Big Ball of Mud**: No clear architecture
- ❌ **Distributed Monolith**: Microservices with tight coupling
- ❌ **Anemic Domain Model**: Domain objects with no behavior
- ❌ **Shotgun Surgery**: One change requires many modifications
- ❌ **Feature Envy**: Class using another class's data excessively

## Pattern Selection Criteria
Consider when choosing patterns:
- **Complexity**: Is the pattern worth the added complexity?
- **Team Knowledge**: Does the team understand the pattern?
- **Problem Fit**: Does the pattern solve the actual problem?
- **Scalability**: Does the pattern support growth?
- **Maintainability**: Will the pattern make maintenance easier?
- **Performance**: What is the performance impact?
- **Cost**: What are the infrastructure costs?