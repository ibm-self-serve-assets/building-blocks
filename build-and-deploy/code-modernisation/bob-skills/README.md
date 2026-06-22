# Code Modernization Skills

This directory contains Bob skills for Code Modernization, enabling automated refactoring, technical debt analysis, and systematic migration of legacy codebases to modern architectures and frameworks.

## 🎯 Overview

The Code Modernization skills empower Bob to help you modernize legacy applications using enterprise patterns, automated transformations, and incremental migration strategies with zero downtime. These skills provide comprehensive capabilities for analyzing technical debt, executing code transformations, and managing migration risks across multiple languages and frameworks.

## 📦 Available Skills

### code-modernization-expert

A comprehensive skill for modernizing legacy codebases systematically using proven enterprise patterns and automated transformations.

#### 1. 🔍 **Current State Assessment**
Comprehensive analysis of existing codebase:
- Framework version detection (package.json, requirements.txt, pom.xml)
- Deprecated API and import identification
- Code smell detection (TODO, FIXME, HACK)
- Security vulnerability scanning
- Dependency health analysis (outdated, vulnerable)
- Test coverage percentage calculation
- Technical risk assessment

#### 2. 📊 **Technical Debt Analysis**
Systematic debt categorization and prioritization:
- Code quality issues (God classes, long methods, duplicates)
- Dependency problems (EOL frameworks, vulnerable libraries)
- Testing gaps (low coverage, missing tests)
- Architecture issues (tight coupling, monolithic design)
- Severity and effort-based prioritization matrix
- Impact on development velocity assessment

#### 3. 🎯 **Modernization Pattern Selection**
Choose the right migration strategy:
- **Strangler Fig Pattern**: Large monoliths, zero downtime required
- **Branch by Abstraction**: Internal modules, service layers
- **Seam-Based Pattern**: Low test coverage, tightly coupled code
- **Parallel Run Pattern**: Mission-critical, financial, healthcare systems

#### 4. 🔄 **Supported Migrations**
Comprehensive multi-language and framework support:

**Programming Languages:**
- **Python**: Python 2 → Python 3 (with modern patterns for 3.6+)
- **Java**: Java 8 → Java 17/21
- **JavaScript**: ES5 → ES6+
- **TypeScript**: Full support
- **PHP**: PHP 5 → PHP 8
- **Ruby**: Ruby 2 → Ruby 3

**Frameworks:**
- **React**: Class Components → Hooks
- **Vue**: Vue 2 → Vue 3
- **Angular**: Angular.js → React migration
- **Spring Boot**: Spring Boot 2 → Spring Boot 3
- **Django**: Python framework support
- **Rails**: Ruby on Rails support

**Architecture Patterns:**
- **Monolith → Microservices**: Decompose monolithic applications
- **REST → GraphQL**: API modernization
- **Callbacks → Async/Await**: Asynchronous pattern updates

#### 5. 🛠️ **Code Transformations**
Automated language-specific changes:
- **Python 2→3**: print statements, dict methods, type hints, dataclasses, f-strings
- **Java 8→21**: javax.* → jakarta.*, Date → java.time.*, POJOs → Records, pattern matching
- **JavaScript ES5→ES6+**: var → let/const, callbacks → async/await, prototypes → classes
- **React**: Class components → Hooks, lifecycle methods → useEffect

#### 6. 🧪 **Test Generation**
Comprehensive test coverage:
- Characterization tests (capture current behavior)
- Golden master tests (record production inputs/outputs)
- Approval tests (snapshot complex outputs)
- Automated test suite generation

#### 7. ⚠️ **Risk Management**
Systematic risk mitigation:
- Risk registry with likelihood and impact tracking
- Rollback plan templates
- Monitoring and alerting setup
- Feature flag implementation
- Incremental deployment strategies (1% → 5% → 25% → 100%)

### maximo-code-optimization

An expert skill for fetching, analyzing, optimizing, and securing IBM Maximo automation scripts with comprehensive best practices.

#### 1. 🔌 **Maximo API Integration**
Automated script fetching from Maximo environments:
- REST API integration with authentication
- Automatic script discovery and download
- Support for both `member` and `rdfs:member` response formats
- SSL certificate handling for self-signed certificates
- Environment-based configuration (.env file)
- Organized directory structure (original/, optimized/, reports/)

#### 2. 🔒 **Security Analysis**
Comprehensive security vulnerability detection:
- SQL injection vulnerability identification
- Input validation gap detection
- Secure coding pattern recommendations
- Credential and sensitive data exposure checks
- Authentication and authorization review

#### 3. ⚡ **Performance Optimization**
Maximo-specific performance improvements:
- MboSet lifecycle management optimization
- Database query optimization
- Resource leak prevention
- Memory management improvements
- Efficient API usage patterns

#### 4. 🛡️ **Error Handling & Logging**
Robust error management:
- Comprehensive error handling implementation
- MXLoggerFactory integration
- Proper exception handling patterns
- Logging best practices
- Null safety checks

#### 5. 📋 **Script Analysis**
Multi-level issue detection:
- **Critical**: Security vulnerabilities, incomplete code, logic errors
- **High**: Resource leaks, major performance problems, missing error handling
- **Medium**: Code quality issues, minor performance improvements
- **Low**: Style improvements, documentation enhancements

#### 6. 📊 **Comprehensive Reporting**
Detailed optimization documentation:
- Individual script reports with before/after comparisons
- Issue summary with severity levels
- Optimization explanations
- Deployment recommendations
- Testing guidelines
- Summary report across all scripts

#### 7. 🔄 **Interactive Workflow**
Systematic optimization process:
- Environment setup and credential management
- Automated script fetching
- Script analysis and optimization
- Report generation
- Deployment guidance

### maximo-modernization-java

A specialized skill for modernizing Java-based Maximo customizations and extensions (Note: This appears to be the same as code-modernization-expert with Java focus).

#### 1. 🔍 **Java-Specific Assessment**
Focused on Java middleware and Maximo customizations:
- Java version detection and compatibility analysis
- Framework version assessment
- Deprecated Java API identification
- Maven/Gradle dependency analysis

#### 2. ☕ **Java Modernization**
Java-specific transformations:
- Java 8 → 21 migration
- javax.* → jakarta.* namespace migration
- Legacy Date API → java.time.* migration
- POJOs → Records transformation
- Pattern matching and text blocks adoption

#### 3. 🏗️ **Maximo Integration**
Maximo-specific Java modernization:
- Maximo Business Object (MBO) optimization
- Maximo API usage modernization
- Integration framework updates
- Custom service modernization

## 🚀 Installation and Setup

### Step 1: Download the Skills

Download the skill packages from this directory:
- `code-modernization-expert.zip` - General code modernization
- `maximo-code-optimization.zip` - Maximo script optimization
- `maximo-modernization-java.zip` - Java/Maximo modernization

### Step 2: Extract Skills to Bob Workspace

Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skills
unzip /path/to/code-modernization-expert.zip
unzip /path/to/maximo-code-optimization.zip
unzip /path/to/maximo-modernization-java.zip
```

After extraction, you should see the skill folders in your `.bob/skills` directory.

### Step 3: Verify Installation

Check that the skills are properly installed:

```bash
ls -la .bob/skills/code-modernization-expert
ls -la .bob/skills/maximo-code-optimization
ls -la .bob/skills/maximo-modernization-java
```

You should see the skill files including SKILL.md, supporting documentation, and pattern files.

### Step 4: Activate the Skills

To use the skills:
1. Open Bob and select Advanced mode (or any mode with skills support)
2. Enable the **Skills** button in that mode
3. The code modernization skills will be available for use within that mode

## 💡 Usage Examples

Once activated, you can ask Bob to help with tasks like:

### General Code Modernization

#### Assessment & Analysis
- *"Analyze my Python 2 codebase for migration to Python 3"*
- *"Assess technical debt in my Java application"*
- *"Identify deprecated APIs in my JavaScript project"*
- *"Generate a migration assessment report"*

#### Code Transformation
- *"Migrate this Java 8 code to Java 21"*
- *"Convert React class components to hooks"*
- *"Transform callbacks to async/await in JavaScript"*
- *"Update javax imports to jakarta"*

#### Migration Planning
- *"Create a migration plan using the Strangler Fig pattern"*
- *"Generate rollback procedures for this migration"*
- *"Set up feature flags for incremental deployment"*
- *"Create characterization tests for legacy code"*

### Maximo Script Optimization

#### Script Fetching
- *"Fetch all automation scripts from my Maximo environment"*
- *"Download Maximo scripts using API key authentication"*
- *"Set up the project structure for Maximo script optimization"*

#### Script Analysis
- *"Analyze my Maximo scripts for security vulnerabilities"*
- *"Identify performance issues in Maximo automation scripts"*
- *"Check for SQL injection vulnerabilities"*
- *"Review MboSet lifecycle management"*

#### Optimization
- *"Optimize this Maximo script for performance"*
- *"Add proper error handling to my automation scripts"*
- *"Implement MXLoggerFactory logging"*
- *"Fix resource leaks in Maximo scripts"*

#### Reporting
- *"Generate optimization report for all scripts"*
- *"Create deployment recommendations"*
- *"Provide testing guidelines for optimized scripts"*

### Java/Maximo Modernization

#### Java Migration
- *"Migrate my Maximo customization from Java 8 to Java 21"*
- *"Update Maximo MBO code to use modern Java features"*
- *"Convert legacy Date usage to java.time API"*
- *"Transform POJOs to Records in Maximo extensions"*

## 🎓 What Bob Can Help You Build

With these skills, Bob can assist you in creating:

### General Modernization Projects
1. **Migration Plans**: Comprehensive roadmaps with risk assessment and rollback procedures
2. **Automated Tests**: Characterization tests, golden master tests, approval tests
3. **Refactored Code**: Modern, maintainable code following current best practices
4. **Documentation**: Migration reports, technical debt analysis, lessons learned
5. **Monitoring Setup**: Error tracking, performance monitoring, alerting systems
6. **Feature Flags**: Incremental deployment infrastructure

### Maximo-Specific Projects
1. **Optimized Scripts**: Secure, performant Maximo automation scripts
2. **Security Reports**: Vulnerability assessments and remediation plans
3. **Performance Analysis**: Bottleneck identification and optimization recommendations
4. **Best Practice Implementation**: Error handling, logging, resource management
5. **Deployment Guides**: Step-by-step deployment and testing procedures
6. **Modernized Java Code**: Updated Maximo customizations using modern Java features

## 📋 Prerequisites

To work with these skills effectively, you should have:

### For General Code Modernization
- Source code access to legacy applications
- Version control system (Git recommended)
- Test environment for validation
- CI/CD pipeline (optional but recommended)
- Monitoring and observability tools

### For Maximo Script Optimization
- IBM Maximo instance with API access
- Maximo REST API credentials (base URL and API key)
- Python 3.8+ installed
- Network connectivity to Maximo instance
- Understanding of Maximo automation scripting

### For Java/Maximo Modernization
- Java Development Kit (JDK 8, 11, 17, or 21)
- Maven or Gradle build tools
- Maximo development environment
- Java IDE (Eclipse, IntelliJ IDEA, VS Code)

## 🔧 Key Technologies

These skills help you work with:

### General Modernization Stack
- **Languages**: Python, Java, JavaScript, TypeScript
- **Frameworks**: React, Vue, Spring Boot, Django, Rails, Angular
- **Patterns**: Strangler Fig, Branch by Abstraction, Seam-Based, Parallel Run
- **Testing**: JUnit, pytest, Jest, Mocha, Cypress
- **Monitoring**: Prometheus, Grafana, ELK Stack, Datadog

### Maximo Stack
- **IBM Maximo**: Asset management platform
- **Jython/Python**: Maximo automation scripting
- **JavaScript/Nashorn**: Alternative scripting language
- **Maximo REST API**: Script management and deployment
- **MXLoggerFactory**: Maximo logging framework
- **MboSet**: Maximo Business Object Set API

### Java Modernization Stack
- **Java**: Versions 8, 11, 17, 21
- **Jakarta EE**: Modern enterprise Java
- **Spring Framework**: Spring Boot, Spring Cloud
- **Build Tools**: Maven, Gradle
- **Testing**: JUnit 5, Mockito, AssertJ

## 🔍 Skill Capabilities Summary

### Code Modernization Expert

| Capability | Description |
|------------|-------------|
| **Assessment** | Comprehensive codebase analysis with technical debt identification |
| **Pattern Selection** | Choose appropriate migration strategy based on context |
| **Multi-Language** | Python 2→3, Java 8→17/21, JavaScript ES5→ES6+, TypeScript, PHP 5→8, Ruby 2→3 |
| **Framework Migration** | React, Vue, Angular.js→React, Spring Boot, Django, Rails |
| **Test Generation** | Automated characterization, golden master, approval tests |
| **Risk Management** | Risk registry, rollback plans, monitoring setup |
| **Incremental Deployment** | Feature flags and phased rollout strategies |
| **Documentation** | Comprehensive migration reports and lessons learned |

### Maximo Code Optimization

| Capability | Description |
|------------|-------------|
| **API Integration** | Automated script fetching from Maximo REST API |
| **Security Analysis** | SQL injection, input validation, credential exposure detection |
| **Performance Optimization** | MboSet management, query optimization, resource leak prevention |
| **Error Handling** | Comprehensive exception handling and logging implementation |
| **Multi-Level Analysis** | Critical, High, Medium, Low severity issue detection |
| **Reporting** | Individual and summary reports with deployment guidance |
| **Interactive Workflow** | Step-by-step optimization process with user guidance |
| **Best Practices** | Maximo-specific coding standards and patterns |

### Maximo Modernization Java

| Capability | Description |
|------------|-------------|
| **Java Migration** | Java 8 → 21 with modern features |
| **Namespace Updates** | javax.* → jakarta.* transformation |
| **API Modernization** | Legacy Date → java.time.*, POJOs → Records |
| **Maximo Integration** | MBO optimization and API modernization |
| **Pattern Adoption** | Pattern matching, text blocks, sealed classes |
| **Framework Updates** | Spring Boot, Jakarta EE modernization |
| **Testing** | JUnit 5, modern testing practices |
| **Build Modernization** | Maven/Gradle configuration updates |

## 📊 Migration Patterns

### Strangler Fig Pattern
Best for: Large monoliths, zero downtime required
- Gradually replace legacy system with new implementation
- Run old and new systems in parallel
- Incrementally route traffic to new system
- Retire legacy components progressively

### Branch by Abstraction
Best for: Internal modules, service layers
- Create abstraction layer over legacy code
- Implement new version behind abstraction
- Switch implementations via configuration
- Remove abstraction once migration complete

### Seam-Based Pattern
Best for: Low test coverage, tightly coupled code
- Identify seams in legacy code
- Insert test points at seams
- Refactor behind seams
- Expand test coverage incrementally

### Parallel Run Pattern
Best for: Mission-critical, financial, healthcare systems
- Run old and new systems simultaneously
- Compare outputs for validation
- Build confidence before cutover
- Maintain rollback capability

## 🐛 Troubleshooting

### Skills don't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Skill is active but Bob doesn't understand requests
1. Be specific in your requests (mention language, framework, or "Maximo")
2. Reference specific features (e.g., "migration plan", "script optimization")
3. Provide context about what you're trying to accomplish
4. Ask Bob to explain the skill's capabilities if unsure

### Maximo API Connection Issues
- **Problem**: "Authentication failed"
  - **Solution**: Verify API key is correct and has proper permissions
- **Problem**: "SSL certificate error"
  - **Solution**: The fetch script handles self-signed certificates automatically
- **Problem**: "No scripts returned"
  - **Solution**: Verify base URL format and endpoint accessibility

### Migration Issues
- **Problem**: "Tests failing after migration"
  - **Solution**: Review characterization tests and validate behavior equivalence
- **Problem**: "Performance degradation"
  - **Solution**: Profile application and optimize hot paths
- **Problem**: "Dependency conflicts"
  - **Solution**: Use dependency analysis tools and resolve version conflicts

## 📚 Related Resources

### Code Modernization
- [Martin Fowler's Refactoring](https://refactoring.com/)
- [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Branch by Abstraction](https://www.branchbyabstraction.com/)

### Maximo Resources
- [IBM Maximo Documentation](https://www.ibm.com/docs/en/maximo-manage)
- [Maximo Automation Scripting Guide](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=scripting-automation)
- [Maximo REST API Documentation](https://www.ibm.com/docs/en/maximo-manage/continuous-delivery?topic=apis-maximo-rest)

### Java Modernization
- [Java Language Updates](https://docs.oracle.com/en/java/javase/)
- [Jakarta EE Documentation](https://jakarta.ee/specifications/)
- [Spring Boot Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)

### Building Blocks
- [Parent Directory README](../README.md) - Complete building block documentation
- [Infrastructure as a Service](../Iaas/README.md) - Deployment automation
- [iPaaS](../ipaas/README.md) - Integration workflows

## 💬 Support

For issues or questions about these skills:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for detailed examples
3. Review each skill's supporting documentation and pattern files
4. Ask Bob directly - the skills include comprehensive knowledge
5. Refer to official documentation for language/framework-specific questions

## 📝 Version Information

### code-modernization-expert
- **Skill Version**: 1.0.0
- **Supported Languages**: Python 2→3, Java 8→17/21, JavaScript ES5→ES6+, TypeScript, PHP 5→8, Ruby 2→3
- **Supported Frameworks**: React, Vue, Angular, Spring Boot, Django, Rails
- **Last Updated**: 2026-06-22
- **Status**: Production Ready ✅

### maximo-code-optimization
- **Skill Version**: 1.0.0
- **Compatible with**: IBM Maximo (all versions with REST API support)
- **Last Updated**: 2026-06-22
- **Status**: Production Ready ✅

### maximo-modernization-java
- **Skill Version**: 1.0.0
- **Compatible with**: Java 8-21, IBM Maximo
- **Last Updated**: 2026-06-22
- **Status**: Production Ready ✅

---

**Note**: These skills require appropriate development environments, access to source code, and proper testing infrastructure. For Maximo-specific skills, ensure you have valid Maximo credentials and API access before starting.

Made with ❤️ for code modernization practitioners