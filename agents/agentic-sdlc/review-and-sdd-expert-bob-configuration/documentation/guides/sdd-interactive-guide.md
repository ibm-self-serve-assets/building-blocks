# Interactive Guide: Crafting Effective Prompts for SDLC

## Introduction

This interactive guide helps you craft effective prompts for AI-assisted development throughout the Software Development Life Cycle (SDLC). By following this structured approach, you'll create clear, comprehensive prompts that lead to better outcomes.

## Why Prompt Quality Matters

**Poor prompts lead to:**
- ❌ Vague or incorrect implementations
- ❌ Missing edge cases and error handling
- ❌ Misaligned with business requirements
- ❌ Wasted time on rework
- ❌ Frustration and confusion

**Good prompts result in:**
- ✅ Clear, accurate implementations
- ✅ Comprehensive solutions
- ✅ Aligned with requirements
- ✅ Efficient development
- ✅ Satisfied stakeholders

## The 5-Step Prompt Crafting Framework

### Step 1: Understand Your Context 🎯

Before writing a prompt, answer these questions:

#### 1.1 What SDLC Phase Are You In?
- [ ] **Planning**: Defining project scope and objectives
- [ ] **Requirements**: Gathering and documenting needs
- [ ] **Design**: Creating architecture and detailed designs
- [ ] **Implementation**: Writing code
- [ ] **Testing**: Validating functionality
- [ ] **Deployment**: Releasing to production
- [ ] **Maintenance**: Fixing bugs and adding features

#### 1.2 What Is Your Specific Goal?
Write a one-sentence goal statement:
```
I want to [action] so that [outcome/benefit]
```

**Examples:**
- "I want to create a user authentication system so that users can securely access the application"
- "I want to optimize database queries so that page load times are under 200ms"
- "I want to document the API endpoints so that frontend developers can integrate easily"

#### 1.3 What Information Do You Already Have?
- [ ] Requirements document
- [ ] Architecture diagrams
- [ ] Existing codebase
- [ ] API specifications
- [ ] Design mockups
- [ ] Test cases
- [ ] Performance benchmarks
- [ ] User feedback

#### 1.4 What Are Your Constraints?
- **Technical**: Programming language, frameworks, libraries
- **Business**: Budget, timeline, resources
- **Regulatory**: Compliance requirements (GDPR, HIPAA, etc.)
- **Performance**: Response time, throughput, scalability
- **Security**: Authentication, authorization, encryption

---

### Step 2: Structure Your Prompt 📝

Use this template to structure your prompt:

```markdown
# [Task Title]

## Context
[Provide background information about the project, current state, and relevant details]

## Objective
[Clearly state what you want to achieve - be specific and measurable]

## Requirements
### Functional Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

### Non-Functional Requirements
- [Performance requirement]
- [Security requirement]
- [Scalability requirement]

## Constraints
- [Technical constraint 1]
- [Business constraint 2]
- [Regulatory constraint 3]

## Current State
[Describe what exists now, if applicable]

## Expected Output
[Describe the format and content of the expected output]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Examples (Optional)
[Provide examples if helpful]

## Additional Context
[Any other relevant information]
```

---

### Step 3: Apply SDLC-Specific Guidelines 🔄

Different SDLC phases require different prompt approaches:

#### Planning Phase Prompts

**Focus on:**
- Project scope and objectives
- Stakeholder identification
- High-level requirements
- Risk assessment
- Resource planning

**Example Prompt:**
```markdown
# Project Planning: E-commerce Platform

## Context
We're planning to build a new e-commerce platform for a mid-sized retail company 
with 50,000 monthly visitors. The current system is outdated and doesn't support 
mobile devices well.

## Objective
Create a comprehensive project plan that outlines scope, timeline, resources, 
and key milestones for the e-commerce platform development.

## Requirements
- Support 50,000+ monthly active users
- Mobile-responsive design
- Integration with existing inventory system
- Payment gateway integration (Stripe, PayPal)
- Admin dashboard for product management
- Customer account management
- Order tracking and history

## Constraints
- Budget: $200,000
- Timeline: 6 months
- Team: 5 developers, 1 designer, 1 PM
- Must maintain current system during migration

## Expected Output
- Project scope statement
- Work breakdown structure (WBS)
- Timeline with milestones
- Resource allocation plan
- Risk assessment matrix
- Success metrics

## Success Criteria
- [ ] All stakeholders approve the plan
- [ ] Timeline is realistic and achievable
- [ ] Budget is within constraints
- [ ] Risks are identified and mitigated
```

#### Requirements Phase Prompts

**Focus on:**
- User needs and pain points
- Functional requirements
- Non-functional requirements
- Acceptance criteria
- Prioritization

**Example Prompt:**
```markdown
# Requirements Gathering: User Authentication System

## Context
Building a SaaS application that requires secure user authentication. We have 
enterprise customers who need SSO integration and compliance with SOC2.

## Objective
Define comprehensive requirements for a user authentication system that supports 
multiple authentication methods and meets enterprise security standards.

## Requirements to Elicit
- Authentication methods (email/password, OAuth, SAML, MFA)
- User roles and permissions
- Session management
- Password policies
- Account recovery
- Audit logging
- SSO integration requirements

## Stakeholders
- End users (need simple, secure login)
- Enterprise customers (need SSO, compliance)
- Security team (need audit trails, compliance)
- Development team (need clear specifications)

## Constraints
- Must comply with SOC2 Type II
- Must support SAML 2.0 for SSO
- Must integrate with existing user database
- Response time < 500ms for authentication

## Expected Output
- Functional requirements document
- Non-functional requirements (security, performance)
- User stories with acceptance criteria
- Priority matrix (MoSCoW)
- Traceability matrix

## Success Criteria
- [ ] All authentication scenarios covered
- [ ] Security requirements meet SOC2 standards
- [ ] Stakeholders approve requirements
- [ ] Requirements are testable and unambiguous
```

#### Design Phase Prompts

**Focus on:**
- Architecture decisions
- Component design
- Data models
- API contracts
- Design patterns

**Example Prompt:**
```markdown
# System Design: Microservices Architecture

## Context
Designing a microservices architecture for an e-commerce platform. Current 
monolithic system has scalability issues and slow deployment cycles.

## Objective
Design a microservices architecture that improves scalability, enables 
independent deployments, and maintains data consistency.

## Requirements
- Support 10,000 concurrent users
- Independent service deployments
- Event-driven communication
- Data consistency across services
- API gateway for external access
- Service discovery and load balancing

## Services to Design
1. User Service (authentication, profiles)
2. Product Service (catalog, inventory)
3. Order Service (cart, checkout, orders)
4. Payment Service (payment processing)
5. Notification Service (emails, SMS)

## Constraints
- Use Kubernetes for orchestration
- PostgreSQL for transactional data
- Redis for caching
- RabbitMQ for messaging
- REST APIs with OpenAPI specs

## Expected Output
- Architecture diagram (C4 model)
- Service boundaries and responsibilities
- Data model for each service
- API contracts (OpenAPI specs)
- Communication patterns (sync/async)
- Data consistency strategy (Saga pattern)
- Deployment architecture

## Success Criteria
- [ ] Services are loosely coupled
- [ ] Data consistency is maintained
- [ ] System can scale horizontally
- [ ] APIs are well-defined and versioned
- [ ] Architecture supports independent deployments
```

#### Implementation Phase Prompts

**Focus on:**
- Code structure and organization
- Implementation details
- Error handling
- Testing approach
- Code quality

**Example Prompt:**
```markdown
# Implementation: User Authentication API

## Context
Implementing the user authentication API based on approved requirements and design. 
Using Node.js with Express, PostgreSQL database, and JWT for tokens.

## Objective
Implement a secure, production-ready user authentication API with email/password 
login, JWT tokens, and password reset functionality.

## Requirements
### Functional
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- POST /api/auth/refresh - Token refresh
- POST /api/auth/forgot-password - Password reset request
- POST /api/auth/reset-password - Password reset

### Non-Functional
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- Rate limiting: 5 requests per minute per IP
- Input validation and sanitization
- Comprehensive error handling
- Audit logging for security events

## Technical Stack
- Node.js 18+
- Express 4.x
- PostgreSQL 14+
- bcrypt for password hashing
- jsonwebtoken for JWT
- express-validator for validation
- winston for logging

## Code Structure
```
src/
  auth/
    controllers/
    services/
    models/
    middleware/
    validators/
    routes/
  utils/
  config/
```

## Expected Output
- Complete implementation of all endpoints
- Unit tests (>80% coverage)
- Integration tests for API endpoints
- Error handling for all edge cases
- API documentation (OpenAPI/Swagger)
- Security best practices implemented

## Success Criteria
- [ ] All endpoints work as specified
- [ ] Security requirements met
- [ ] Tests pass with >80% coverage
- [ ] Code follows style guide
- [ ] No security vulnerabilities (npm audit)
- [ ] API documentation is complete
```

#### Testing Phase Prompts

**Focus on:**
- Test strategy
- Test cases
- Coverage requirements
- Performance testing
- Security testing

**Example Prompt:**
```markdown
# Testing Strategy: E-commerce Checkout Flow

## Context
Need comprehensive testing for the checkout flow, which is critical for revenue. 
The flow includes cart management, address entry, payment processing, and order 
confirmation.

## Objective
Create a comprehensive testing strategy that ensures the checkout flow works 
correctly under all conditions and meets performance requirements.

## Scope
- Unit tests for business logic
- Integration tests for API endpoints
- End-to-end tests for user flows
- Performance tests for load handling
- Security tests for payment processing

## Requirements
### Functional Testing
- Cart operations (add, remove, update quantities)
- Address validation
- Payment processing (success, failure, timeout)
- Order creation and confirmation
- Email notifications
- Inventory updates

### Non-Functional Testing
- Performance: Handle 1000 concurrent checkouts
- Security: PCI-DSS compliance for payment data
- Reliability: 99.9% success rate
- Usability: Complete checkout in < 3 minutes

## Test Scenarios
1. Happy path: Successful checkout
2. Payment failure scenarios
3. Inventory out of stock during checkout
4. Network timeout during payment
5. Concurrent checkout of same item
6. Invalid address or payment information
7. Session timeout during checkout

## Expected Output
- Test plan document
- Test cases with steps and expected results
- Automated test scripts
- Performance test scenarios
- Security test checklist
- Test data requirements
- Test environment setup

## Success Criteria
- [ ] All critical paths have test coverage
- [ ] Automated tests run in CI/CD pipeline
- [ ] Performance tests meet SLA requirements
- [ ] Security tests pass PCI-DSS requirements
- [ ] Test documentation is complete
```

#### Deployment Phase Prompts

**Focus on:**
- Deployment strategy
- Infrastructure setup
- Configuration management
- Monitoring and alerting
- Rollback procedures

**Example Prompt:**
```markdown
# Deployment Plan: Production Release

## Context
Deploying the e-commerce platform to production. Using AWS infrastructure with 
Kubernetes for container orchestration. Need zero-downtime deployment.

## Objective
Create a comprehensive deployment plan that ensures safe, zero-downtime release 
to production with proper monitoring and rollback capabilities.

## Requirements
- Zero-downtime deployment
- Blue-green deployment strategy
- Automated health checks
- Database migration strategy
- Configuration management
- Monitoring and alerting
- Rollback procedure

## Infrastructure
- AWS EKS for Kubernetes
- RDS PostgreSQL for database
- ElastiCache Redis for caching
- CloudFront CDN
- Route53 for DNS
- CloudWatch for monitoring

## Deployment Steps
1. Pre-deployment checks
2. Database migrations
3. Deploy to staging
4. Smoke tests on staging
5. Deploy to production (blue-green)
6. Health checks and validation
7. Switch traffic to new version
8. Monitor for issues
9. Rollback if needed

## Expected Output
- Deployment runbook
- Infrastructure as Code (Terraform)
- Kubernetes manifests
- CI/CD pipeline configuration
- Monitoring dashboard setup
- Alerting rules
- Rollback procedure
- Post-deployment checklist

## Success Criteria
- [ ] Zero downtime during deployment
- [ ] All health checks pass
- [ ] Monitoring shows normal metrics
- [ ] No critical errors in logs
- [ ] Rollback procedure tested
- [ ] Documentation updated
```

#### Maintenance Phase Prompts

**Focus on:**
- Bug fixes
- Performance optimization
- Feature enhancements
- Technical debt reduction
- Documentation updates

**Example Prompt:**
```markdown
# Bug Fix: Slow Database Queries

## Context
Users are reporting slow page load times (5-10 seconds) on the product listing 
page. Database monitoring shows slow queries on the products table.

## Objective
Identify and fix the slow database queries to achieve page load times under 
200ms for 95% of requests.

## Current State
- Products table has 100,000 rows
- Query uses multiple JOINs with categories and reviews
- No indexes on foreign keys
- N+1 query problem in ORM
- No query result caching

## Requirements
- Analyze slow queries
- Add appropriate indexes
- Optimize ORM queries
- Implement caching strategy
- Measure performance improvement

## Constraints
- Cannot change database schema significantly
- Must maintain backward compatibility
- Zero downtime for optimization
- Must work with existing ORM (Sequelize)

## Expected Output
- Query analysis report
- Index recommendations
- Optimized query code
- Caching implementation
- Performance benchmarks (before/after)
- Migration scripts
- Documentation updates

## Success Criteria
- [ ] Page load time < 200ms for 95% of requests
- [ ] Database CPU usage reduced by 50%
- [ ] No breaking changes to API
- [ ] All tests pass
- [ ] Performance improvements documented
```

---

### Step 4: Validate Your Prompt ✅

Before submitting your prompt, check these quality criteria:

#### Clarity Checklist
- [ ] **Objective is clear**: Can someone unfamiliar with the project understand what you want?
- [ ] **Context is sufficient**: Is there enough background information?
- [ ] **Requirements are specific**: Are requirements measurable and testable?
- [ ] **Constraints are explicit**: Are limitations clearly stated?
- [ ] **Output is well-defined**: Is it clear what the expected result should be?

#### Completeness Checklist
- [ ] **All necessary information included**: Nothing critical is missing
- [ ] **Edge cases considered**: Error conditions and exceptions addressed
- [ ] **Success criteria defined**: Clear definition of "done"
- [ ] **Examples provided** (if helpful): Concrete examples clarify expectations
- [ ] **Assumptions documented**: Any assumptions are explicitly stated

#### Quality Checklist
- [ ] **No ambiguous terms**: Avoid words like "fast", "good", "user-friendly"
- [ ] **Consistent terminology**: Same terms used throughout
- [ ] **Proper formatting**: Easy to read and scan
- [ ] **Appropriate detail level**: Not too vague, not too prescriptive
- [ ] **Testable requirements**: Can verify if requirements are met

#### Common Issues to Avoid

**❌ Too Vague:**
```
Create a login page that works well
```

**✅ Specific:**
```
Create a login page with:
- Email and password fields with validation
- "Remember me" checkbox
- "Forgot password" link
- Error messages for invalid credentials
- Loading state during authentication
- Redirect to dashboard on success
- WCAG 2.1 Level AA accessibility compliance
```

**❌ Missing Context:**
```
Optimize the database queries
```

**✅ With Context:**
```
Optimize the product listing queries that are currently taking 5-10 seconds.
The products table has 100,000 rows with JOINs to categories and reviews.
Target: < 200ms response time for 95% of requests.
```

**❌ No Success Criteria:**
```
Implement user authentication
```

**✅ With Success Criteria:**
```
Implement user authentication with:
Success Criteria:
- [ ] Users can register with email/password
- [ ] Users can log in and receive JWT token
- [ ] Passwords are hashed with bcrypt
- [ ] Invalid credentials show appropriate error
- [ ] Rate limiting prevents brute force attacks
- [ ] All tests pass with >80% coverage
```

---

### Step 5: Iterate and Improve 🔄

After receiving results, evaluate and refine:

#### Evaluation Questions
1. **Did the output meet your expectations?**
   - If yes: What made the prompt effective?
   - If no: What was missing or unclear?

2. **Were there any misunderstandings?**
   - What caused the confusion?
   - How can you clarify in the future?

3. **What would you change?**
   - More context?
   - Better examples?
   - Clearer constraints?
   - More specific requirements?

#### Refinement Process
1. **Identify gaps**: What information was missing?
2. **Add specificity**: Make vague requirements concrete
3. **Provide examples**: Show what good looks like
4. **Clarify constraints**: Be explicit about limitations
5. **Update success criteria**: Make them more measurable

#### Learning Loop
Keep a prompt journal:
```markdown
## Prompt: [Title]
**Date**: YYYY-MM-DD
**Phase**: [SDLC Phase]

### Original Prompt
[Your original prompt]

### Result Quality
- [ ] Met expectations
- [ ] Partially met expectations
- [ ] Did not meet expectations

### What Worked Well
- [Point 1]
- [Point 2]

### What Could Be Improved
- [Point 1]
- [Point 2]

### Refined Prompt
[Your improved version]

### Lessons Learned
- [Lesson 1]
- [Lesson 2]
```

---

## Real-World Examples

### Example 1: From Vague to Specific

**❌ Vague Prompt:**
```
Create a REST API for user management
```

**✅ Specific Prompt:**
```markdown
# Implementation: User Management REST API

## Context
Building a user management API for a SaaS application with role-based access 
control. The API will be used by both web and mobile clients.

## Objective
Implement a RESTful API for user management that supports CRUD operations, 
role management, and follows REST best practices.

## Requirements
### Endpoints
- GET /api/users - List users (paginated, filterable)
- GET /api/users/:id - Get user by ID
- POST /api/users - Create new user
- PUT /api/users/:id - Update user
- DELETE /api/users/:id - Delete user (soft delete)
- GET /api/users/:id/roles - Get user roles
- POST /api/users/:id/roles - Assign role to user
- DELETE /api/users/:id/roles/:roleId - Remove role from user

### Data Model
```json
{
  "id": "uuid",
  "email": "string (unique, validated)",
  "firstName": "string",
  "lastName": "string",
  "roles": ["array of role objects"],
  "status": "active | inactive | suspended",
  "createdAt": "timestamp",
  "updatedAt": "timestamp",
  "deletedAt": "timestamp (nullable)"
}
```

### Validation
- Email: Valid format, unique
- Names: 2-50 characters, letters only
- Roles: Must exist in roles table
- Status: One of allowed values

### Security
- JWT authentication required
- Admin role required for user management
- Users can only view their own data (unless admin)
- Audit log all user changes

### Performance
- List endpoint: < 100ms for 1000 users
- Pagination: 20 items per page
- Filtering: by email, name, role, status

## Technical Stack
- Node.js 18+ with Express
- PostgreSQL with Sequelize ORM
- JWT for authentication
- express-validator for validation
- winston for logging

## Expected Output
- Complete API implementation
- OpenAPI/Swagger documentation
- Unit tests (>80% coverage)
- Integration tests for all endpoints
- Error handling for all cases
- Input validation and sanitization

## Success Criteria
- [ ] All endpoints work as specified
- [ ] Validation prevents invalid data
- [ ] Security requirements enforced
- [ ] Performance targets met
- [ ] Tests pass with >80% coverage
- [ ] API documentation complete
```

### Example 2: Adding Missing Context

**❌ Missing Context:**
```
Fix the performance issue
```

**✅ With Context:**
```markdown
# Performance Optimization: Product Search

## Context
The product search feature is experiencing severe performance degradation. Users 
report search taking 10-15 seconds, causing cart abandonment. This started after 
we added full-text search and increased the product catalog to 500,000 items.

## Current State
- Products table: 500,000 rows
- Search uses PostgreSQL full-text search
- No indexes on search columns
- Search includes product name, description, category, tags
- Results include product images, prices, reviews
- No caching implemented
- Database CPU at 90% during peak hours

## Objective
Optimize product search to achieve < 500ms response time for 95% of searches 
under normal load (1000 concurrent users).

## Requirements
- Maintain current search functionality
- Support fuzzy matching
- Include filters (category, price range, rating)
- Sort by relevance, price, rating
- Paginate results (20 per page)
- Highlight search terms in results

## Constraints
- Cannot change database (PostgreSQL)
- Must maintain backward compatibility
- Zero downtime for optimization
- Budget: Can add caching layer (Redis)

## Investigation Needed
- Analyze slow query logs
- Profile database queries
- Identify N+1 query problems
- Evaluate index usage
- Consider caching strategy

## Expected Output
- Performance analysis report
- Optimized queries
- Index recommendations
- Caching implementation
- Load testing results
- Before/after benchmarks
- Implementation plan

## Success Criteria
- [ ] Search response time < 500ms (95th percentile)
- [ ] Database CPU usage < 50%
- [ ] No degradation in search quality
- [ ] All existing tests pass
- [ ] New performance tests added
- [ ] Documentation updated
```

---

## Quick Reference: Prompt Templates

### Template 1: Feature Implementation
```markdown
# Feature: [Feature Name]

## Context
[Background and current state]

## Objective
[What you want to achieve]

## Requirements
- [Requirement 1]
- [Requirement 2]

## Technical Details
- Stack: [Technologies]
- Constraints: [Limitations]

## Expected Output
- [Deliverable 1]
- [Deliverable 2]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

### Template 2: Bug Fix
```markdown
# Bug Fix: [Issue Description]

## Problem
[What's broken and impact]

## Current Behavior
[What happens now]

## Expected Behavior
[What should happen]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]

## Root Cause (if known)
[Analysis of the issue]

## Proposed Solution
[How to fix it]

## Success Criteria
- [ ] Bug is fixed
- [ ] No regressions
- [ ] Tests added
```

### Template 3: Architecture Decision
```markdown
# Architecture Decision: [Topic]

## Context
[Background and problem]

## Options Considered
1. [Option 1]: Pros/Cons
2. [Option 2]: Pros/Cons

## Decision Criteria
- [Criterion 1]
- [Criterion 2]

## Recommendation
[Preferred option and why]

## Consequences
- Positive: [Benefits]
- Negative: [Trade-offs]

## Implementation Plan
[How to implement]
```

---

## Conclusion

Effective prompt crafting is a skill that improves with practice. By following this guide and iterating on your prompts, you'll:

✅ Get better results from AI-assisted development
✅ Save time on rework and clarification
✅ Improve communication with stakeholders
✅ Build better software faster
✅ Reduce errors and misunderstandings

Remember: **The quality of your output depends on the quality of your input.**

---

## Additional Resources

### Further Reading
- [IBM Requirements Management Best Practices](https://www.ibm.com/think/topics/what-is-requirements-management)
- [Spec-Driven Development with IBM Bob](https://alain-airom.medium.com/spec-driven-development-with-ibm-bob-sdlc-01594799e38d)
- [Why IBM Bob for SDLC](https://heidloff.net/article/why-ibm-bob-software-development-lifecycle-partner/)
- [Vibes, Specs, Skills, Agents in AI Coding](https://developers.redhat.com/articles/2026/03/30/vibes-specs-skills-agents-ai-coding)

### Related Skills
- Requirements Management Skill
- Architecture Review Skills
- Prompt Engineering Best Practices

---

**Guide Version**: 1.0  
**Last Updated**: 2026-05-26  
**Maintained By**: SDD Team