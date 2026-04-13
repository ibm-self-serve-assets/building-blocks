# Security & Threat Modeling Review Skill

## Purpose
Identify security gaps, potential attack vectors, and provide actionable security recommendations.

## Expertise Areas
- OWASP Top 10 vulnerabilities
- STRIDE threat modeling (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- Authentication and authorization mechanisms
- Data protection and encryption
- Network security and segmentation
- Compliance requirements (GDPR, HIPAA, PCI-DSS, SOC2, ISO 27001)
- Security testing and penetration testing
- Secure coding practices
- Zero Trust Architecture

## Review Process

### 1. Authentication & Authorization
- How are users authenticated?
- What authentication mechanisms are used (OAuth, SAML, JWT, etc.)?
- How are passwords/secrets stored and managed?
- Is multi-factor authentication (MFA) implemented?
- How is authorization enforced (RBAC, ABAC, etc.)?
- Are there proper session management controls?

### 2. Data Protection
- What data is considered sensitive?
- How is data encrypted at rest?
- How is data encrypted in transit (TLS/SSL)?
- Are encryption keys properly managed?
- Is there data masking/tokenization for sensitive data?
- How is data backup secured?
- What is the data retention policy?

### 3. Network Security
- What is the network architecture?
- Are there proper network segmentation and isolation?
- Are firewalls and security groups configured correctly?
- Is there a DMZ for public-facing services?
- How is internal vs. external traffic controlled?
- Are there intrusion detection/prevention systems?

### 4. STRIDE Threat Modeling
Analyze each threat category:

**Spoofing Identity**
- Can attackers impersonate legitimate users?
- Are there weak authentication mechanisms?
- Is there proper identity verification?

**Tampering with Data**
- Can data be modified in transit or at rest?
- Are there integrity checks?
- Is there audit logging for data changes?

**Repudiation**
- Can users deny performing actions?
- Is there comprehensive audit logging?
- Are logs tamper-proof?

**Information Disclosure**
- Can sensitive information be exposed?
- Are there proper access controls?
- Is there data leakage through logs or errors?

**Denial of Service**
- Can the system be overwhelmed?
- Are there rate limiting and throttling?
- Is there DDoS protection?

**Elevation of Privilege**
- Can users gain unauthorized access?
- Are there privilege escalation vulnerabilities?
- Is the principle of least privilege enforced?

### 5. OWASP Top 10 Assessment
Check for:
1. **Broken Access Control**: Unauthorized access to resources
2. **Cryptographic Failures**: Weak encryption, exposed secrets
3. **Injection**: SQL, NoSQL, OS command injection
4. **Insecure Design**: Missing security controls in design
5. **Security Misconfiguration**: Default configs, unnecessary features
6. **Vulnerable Components**: Outdated dependencies
7. **Authentication Failures**: Weak authentication mechanisms
8. **Software and Data Integrity**: Unsigned code, insecure CI/CD
9. **Logging and Monitoring Failures**: Insufficient logging
10. **Server-Side Request Forgery (SSRF)**: Unvalidated URLs

### 6. Compliance Requirements
Assess compliance with:
- **GDPR**: Data privacy, consent, right to be forgotten
- **HIPAA**: Healthcare data protection
- **PCI-DSS**: Payment card data security
- **SOC2**: Security, availability, confidentiality
- **ISO 27001**: Information security management

### 7. Security Testing
- Are there automated security scans (SAST, DAST)?
- Is there regular penetration testing?
- Are there security code reviews?
- Is there dependency vulnerability scanning?
- Are there security regression tests?

## Output Format

### ✅ Achieved
- List security controls in place
- Highlight strong authentication/authorization
- Note compliance requirements met
- Identify good security practices

### ⚠️ Concerns
- Potential security gaps
- Areas needing hardening
- Compliance risks
- Security technical debt

### ❌ Not Achieved
- Critical security vulnerabilities
- Missing security controls
- Unaddressed threat vectors
- Compliance violations

### 🔒 Threat Model Summary
| Threat Category | Likelihood | Impact | Current Mitigation | Status |
|----------------|-----------|--------|-------------------|--------|
| Spoofing | High/Med/Low | High/Med/Low | [Description] | ✅/⚠️/❌ |
| Tampering | High/Med/Low | High/Med/Low | [Description] | ✅/⚠️/❌ |
| Repudiation | High/Med/Low | High/Med/Low | [Description] | ✅/⚠️/❌ |
| Info Disclosure | High/Med/Low | High/Med/Low | [Description] | ✅/⚠️/❌ |
| DoS | High/Med/Low | High/Med/Low | [Description] | ✅/⚠️/❌ |
| Privilege Escalation | High/Med/Low | High/Med/Low | [Description] | ✅/⚠️/❌ |

### 💡 Recommendations
For each security issue:
- **Priority**: Critical/High/Medium/Low
- **Attack Vector**: How the vulnerability can be exploited
- **Impact**: Potential damage if exploited
- **Mitigation**: Specific remediation steps
- **Effort**: Implementation complexity
- **References**: OWASP, CWE, CVE numbers

## Key Questions to Answer
1. What are the most critical security risks?
2. Are authentication and authorization robust?
3. Is sensitive data properly protected?
4. Are there compliance gaps?
5. Is the system resilient to common attacks?
6. Are security controls tested regularly?
7. Is there a security incident response plan?

## Security Checklist
- [ ] Strong authentication mechanisms
- [ ] Proper authorization controls
- [ ] Data encryption at rest and in transit
- [ ] Secure secret management
- [ ] Input validation and sanitization
- [ ] Output encoding
- [ ] Secure session management
- [ ] Comprehensive audit logging
- [ ] Rate limiting and throttling
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Dependency vulnerability scanning
- [ ] Regular security testing
- [ ] Incident response plan
- [ ] Security training for developers