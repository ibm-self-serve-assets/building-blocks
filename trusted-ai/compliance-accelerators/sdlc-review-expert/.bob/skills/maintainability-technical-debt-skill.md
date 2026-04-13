# Maintainability & Technical Debt Review Skill

## Purpose
Identify maintainability issues, quantify technical debt, and provide refactoring recommendations.

## Expertise Areas
- Code complexity analysis (cyclomatic complexity, cognitive complexity)
- Dependency management and coupling analysis
- Code duplication detection
- Test coverage and quality assessment
- Refactoring strategies
- Technical debt quantification
- Code review best practices
- Static analysis and linting
- Code smells identification
- Software entropy management

## Review Process

### 1. Code Complexity Analysis

**Cyclomatic Complexity**
- What is the average cyclomatic complexity?
- Are there functions with high complexity (>10)?
- Are complex functions properly tested?
- Can complex functions be simplified?

**Cognitive Complexity**
- How difficult is the code to understand?
- Are there deeply nested structures?
- Is there excessive branching?
- Are there long methods/functions?

**Lines of Code (LOC)**
- What is the average function/method size?
- Are there excessively long files?
- Is code properly modularized?

### 2. Coupling and Cohesion

**Coupling Analysis**
- What is the level of coupling between modules?
- Are there tight coupling issues?
- Is there proper dependency injection?
- Are there circular dependencies?
- Is there temporal coupling?

**Cohesion Analysis**
- Are modules cohesive?
- Do classes have single responsibilities?
- Are related functions grouped together?
- Is there low cohesion (scattered functionality)?

### 3. Code Duplication

**Duplication Detection**
- What percentage of code is duplicated?
- Where is duplication occurring?
- Is duplication intentional or accidental?
- Can duplication be eliminated through abstraction?

**DRY Principle Violations**
- Are there repeated code blocks?
- Is there duplicated business logic?
- Are there copy-paste patterns?

### 4. Dependency Management

**Dependency Analysis**
- How many dependencies does the project have?
- Are dependencies up-to-date?
- Are there unused dependencies?
- Are there security vulnerabilities in dependencies?
- Is there dependency version pinning?

**Dependency Structure**
- Is there a clear dependency hierarchy?
- Are there layering violations?
- Is there proper dependency inversion?

### 5. Test Coverage and Quality

**Test Coverage**
- What is the overall test coverage percentage?
- What is the branch coverage?
- Are critical paths tested?
- Are edge cases covered?

**Test Quality**
- Are tests meaningful?
- Are tests maintainable?
- Are there flaky tests?
- Is there test duplication?
- Are tests fast?

**Test Types**
- Unit tests coverage
- Integration tests coverage
- End-to-end tests coverage
- Performance tests
- Security tests

### 6. Code Smells Identification

**Bloaters**
- Long Method
- Large Class
- Primitive Obsession
- Long Parameter List
- Data Clumps

**Object-Orientation Abusers**
- Switch Statements (should be polymorphism)
- Temporary Field
- Refused Bequest
- Alternative Classes with Different Interfaces

**Change Preventers**
- Divergent Change (one class changes for many reasons)
- Shotgun Surgery (one change affects many classes)
- Parallel Inheritance Hierarchies

**Dispensables**
- Comments (excessive or outdated)
- Duplicate Code
- Lazy Class
- Data Class
- Dead Code
- Speculative Generality

**Couplers**
- Feature Envy
- Inappropriate Intimacy
- Message Chains
- Middle Man

### 7. Technical Debt Quantification

**Debt Categories**
- **Code Debt**: Poor code quality, complexity
- **Design Debt**: Architectural issues, pattern violations
- **Test Debt**: Missing or poor tests
- **Documentation Debt**: Missing or outdated docs
- **Infrastructure Debt**: Outdated tools, platforms
- **Dependency Debt**: Outdated or vulnerable dependencies

**Debt Measurement**
- Time to fix (hours/days)
- Cost to fix (monetary)
- Interest (ongoing cost of not fixing)
- Risk level (probability × impact)

**Debt Prioritization**
- High interest, high risk → Fix immediately
- High interest, low risk → Schedule soon
- Low interest, high risk → Monitor
- Low interest, low risk → Backlog

### 8. Refactoring Opportunities

**Extract Method/Function**
- Long methods that can be broken down
- Repeated code blocks
- Complex conditional logic

**Extract Class**
- Classes with multiple responsibilities
- Large classes with distinct groups of methods
- Data clumps that belong together

**Introduce Parameter Object**
- Long parameter lists
- Related parameters passed together

**Replace Conditional with Polymorphism**
- Switch statements on type codes
- Repeated conditional logic

**Simplify Conditional Expressions**
- Complex boolean expressions
- Nested conditionals
- Duplicate conditions

### 9. Maintainability Metrics

**Maintainability Index**
- Composite metric (0-100 scale)
- Based on cyclomatic complexity, LOC, and Halstead volume
- >85: Good, 65-85: Moderate, <65: Difficult to maintain

**Technical Debt Ratio**
- Remediation cost / Development cost
- Industry average: 5-10%
- >20%: High debt, needs attention

**Code Churn**
- Frequency of changes to files
- High churn may indicate instability
- Correlate with defect rates

### 10. Documentation Quality

**Code Documentation**
- Are functions/methods documented?
- Are complex algorithms explained?
- Are public APIs documented?
- Is documentation up-to-date?

**Architecture Documentation**
- Are design decisions documented?
- Are there architecture diagrams?
- Is there a README?
- Are there contribution guidelines?

## Output Format

### ✅ Achieved
- List well-maintained areas
- Highlight good code organization
- Note appropriate abstractions
- Identify manageable dependencies

### ⚠️ Concerns
- Code smells identified
- Increasing complexity
- Dependency concerns
- Test coverage gaps

### ❌ Not Achieved
- High coupling issues
- Excessive technical debt
- Unmaintainable code areas
- Critical refactoring needs

### 🔧 Technical Debt Assessment Table
| Area | Severity | Effort to Fix | Interest (Cost/Month) | Priority |
|------|----------|---------------|----------------------|----------|
| [Component] | High/Med/Low | High/Med/Low | $[amount] | Critical/High/Med/Low |

### 📈 Code Quality Metrics
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Cyclomatic Complexity (Avg) | [value] | <10 | ✅/⚠️/❌ |
| Code Duplication | [%] | <5% | ✅/⚠️/❌ |
| Test Coverage | [%] | >80% | ✅/⚠️/❌ |
| Maintainability Index | [value] | >85 | ✅/⚠️/❌ |
| Technical Debt Ratio | [%] | <10% | ✅/⚠️/❌ |
| Dependency Count | [number] | [target] | ✅/⚠️/❌ |

### 💡 Recommendations
For each maintainability issue:
- **Priority**: Critical/High/Medium/Low
- **Issue**: Specific problem description
- **Impact**: Effect on maintainability
- **Refactoring Approach**: Strategy to fix
- **Effort**: Time estimate
- **Benefits**: Expected improvements
- **Risks**: Potential issues during refactoring

## Key Questions to Answer
1. Is the codebase maintainable?
2. What is the technical debt level?
3. Are there high-complexity areas?
4. Is test coverage adequate?
5. Are dependencies well-managed?
6. Are there significant code smells?
7. What refactoring is most urgent?
8. Is the code well-documented?

## Refactoring Checklist
- [ ] Identify high-complexity functions
- [ ] Detect code duplication
- [ ] Find coupling issues
- [ ] Locate code smells
- [ ] Assess test coverage
- [ ] Review dependencies
- [ ] Check documentation
- [ ] Quantify technical debt
- [ ] Prioritize refactoring
- [ ] Create refactoring plan

## Tools and Techniques
- **Static Analysis**: SonarQube, ESLint, Pylint, RuboCop
- **Complexity Analysis**: Lizard, CodeClimate
- **Duplication Detection**: CPD, Simian
- **Dependency Analysis**: Dependency-cruiser, Madge
- **Test Coverage**: Istanbul, JaCoCo, Coverage.py
- **Code Review**: Pull request reviews, pair programming
- **Refactoring Tools**: IDE refactoring features, automated tools

## Best Practices
- ✅ Regular code reviews
- ✅ Continuous refactoring
- ✅ Boy Scout Rule (leave code better than you found it)
- ✅ Test-driven development (TDD)
- ✅ Automated quality gates
- ✅ Technical debt tracking
- ✅ Refactoring sprints
- ✅ Knowledge sharing sessions