---
name: code-modernization-expert
description: Modernize legacy code using enterprise patterns, automated refactoring, technical debt analysis, and incremental migration with zero downtime
---

Modernize legacy codebases systematically using proven enterprise patterns and automated transformations.

## Supported Migrations

- **Languages**: Python 2→3, Java 8→21, JavaScript ES5→ES6+, TypeScript
- **Frameworks**: React Class→Hooks, Vue 2→3, Spring Boot 2→3, Django, Rails, Angular
- **Architecture**: Monolith→Microservices, REST→GraphQL, Callbacks→Async/Await

<Steps>

<Step>
**Assess Current State**

Use Glob to find all source files. Use Grep to identify:
- Framework versions (package.json, requirements.txt, pom.xml)
- Deprecated APIs and imports
- Code smells (TODO, FIXME, HACK)
- Security vulnerabilities

Generate Current State Report with:
- Languages, frameworks, versions
- Dependency health (outdated, vulnerable)
- Test coverage percentage
- Technical risks

See `assessment-checklist.md` for detailed items.
</Step>

<Step>
**Analyze Technical Debt**

Categorize debt by severity and effort:
- Code quality (God classes, long methods, duplicates)
- Dependencies (EOL frameworks, vulnerable libraries)
- Testing gaps (low coverage, missing tests)
- Architecture issues (tight coupling, monolithic design)

Use prioritization matrix in `debt-prioritization.md` to rank items.

Create inventory with: Severity, Effort, Risk, Impact on velocity.
</Step>

<Step>
**Select Modernization Pattern**

Choose based on context:

- **Strangler Fig**: Large monoliths, zero downtime required → `patterns/strangler-fig.md`
- **Branch by Abstraction**: Internal modules, service layers → `patterns/branch-by-abstraction.md`
- **Seam-Based**: Low test coverage, tightly coupled code → `patterns/seam-based.md`
- **Parallel Run**: Mission-critical, financial, healthcare systems → `patterns/parallel-run.md`
</Step>

<Step>
**Create Migration Plan**

Generate phased roadmap:

**Preparation (1-2 weeks):**
- Set up feature flags
- Implement monitoring/alerting
- Generate characterization tests
- Create rollback procedures (see `rollback-template.yaml`)

**Execution (Iterative per module):**
- Read source files
- Generate tests capturing current behavior
- Apply transformations with Edit/MultiEdit
- Update imports and dependencies
- Run tests to validate
- Deploy incrementally (1% → 5% → 25% → 100%)

**Validation:**
- Run test suite
- Perform shadow testing
- Monitor error rates and latency

**Cleanup:**
- Remove legacy code
- Remove feature flags
- Update documentation
</Step>

<Step>
**Execute Transformations**

Apply language-specific changes:

**Python 2→3**: See `migrations/python.md`
- print statements → print()
- dict.iteritems() → dict.items()
- Add type hints, dataclasses, f-strings

**Java 8→21**: See `migrations/java.md`
- javax.* → jakarta.*
- Date → java.time.*
- POJOs → Records
- Add pattern matching, text blocks

**JavaScript ES5→ES6+**: See `migrations/javascript.md`
- var → let/const
- callbacks → async/await
- prototypes → classes
- Add template literals, modules

**React Class→Hooks**: See `migrations/react.md`
- constructor+state → useState
- componentDidMount → useEffect
- lifecycle methods → hooks
</Step>

<Step>
**Generate Tests**

Create comprehensive coverage:

**Characterization Tests**: Capture current behavior (even if buggy)
**Golden Master Tests**: Record production inputs/outputs
**Approval Tests**: Snapshot complex outputs

See `testing-strategies.md` for examples.

Use Task tool to delegate test generation when needed.
</Step>

<Step>
**Manage Risks**

Implement mitigation:

**Risk Registry**: Track risks with likelihood, impact, mitigation, owners

**Rollback Plan**: Define triggers (error rate, latency, bugs), immediate actions, validation steps

**Monitoring**: Track error rates, latency, business metrics, set alerts

See `rollback-template.yaml` for complete template.
</Step>

<Step>
**Document Results**

Generate migration report with:
- Executive summary (current vs target, approach, timeline)
- Technical details (files modified, dependencies updated, tests added)
- Results (statistics, test results, performance impact)
- Lessons learned and next steps
</Step>

</Steps>

## Tool Usage

- **Read**: Load source files
- **Glob**: Discover files to migrate
- **Grep**: Find patterns, deprecated APIs
- **Edit/MultiEdit**: Apply transformations
- **Write**: Create reports, tests
- **Bash**: Run tests, install dependencies
- **Task**: Delegate to specialized agents

## Configuration

Create `.code-modernization-config.yml`:

```yaml
modernization:
  backup_enabled: true
  incremental: true
  generate_tests: true
  risk_threshold: medium

validation:
  run_tests: true
  run_linters: true
  type_check: true

monitoring:
  error_rate_threshold: 0.05
  rollback_on_threshold: true

feature_flags:
  enabled: true
  rollout_percentages: [1, 5, 10, 25, 50, 100]
```

## Best Practices

**DO**: Start small, test first, use feature flags, monitor continuously, commit frequently
**DON'T**: Big-bang rewrites, skip testing, ignore metrics, rush critical code, work in isolation