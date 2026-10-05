# DevLens Comprehensive Security Architecture & Policy

**Document Version:** 1.0.0  
**Effective Date:** Active  
**Scope:** DevLens Backend, Frontend, API Gateway, and AI Pipelines  

---

## Non-Negotiable Security Disclaimer

> **Notice:** DevLens is designed with security best practices and continuously tested for common vulnerabilities. As with all software systems, absolute security cannot be guaranteed. Our security posture relies on a defense-in-depth architecture, rigorous static validation, automated dependency scanning, and adherence to established industry standards.

---

## 1. Security Architecture & Guiding Principles

DevLens implements four foundational security design tenets:
1. **Defense-in-Depth:** Multiple redundant controls validate data at every layer (browser, gateway, schema validation, AST engine, database query).
2. **Principle of Least Privilege (PoLP):** Processes, database connections, and AI integrations operate with the absolute minimum access required to execute their specific responsibilities.
3. **Zero Trust Data Handling:** All user-supplied data—particularly submitted source code—is treated as untrusted input until strictly validated.
4. **Fail-Safe Defaults:** If an analysis task, AST parse, or AI request fails, the system fails closed gracefully without leaking sensitive internal state or system diagnostics.

---

## 2. OWASP Top 10 Compliance Mapping

- **A01: Broken Access Control**: Strict tenant ownership verification on all resource queries (`WHERE id = :id AND user_id = :current_user_id`). IDOR/BOLA attacks return 404 Not Found.
- **A02: Cryptographic Failures**: Passwords hashed using Argon2id or bcrypt (cost >= 12). TLS 1.3 in transit. Refresh tokens in HttpOnly, Secure, SameSite=Strict cookies.
- **A03: Injection**: 100% parameterized SQL via SQLAlchemy 2.0. No dynamic shell execution. Static AST parsing only.
- **A04: Insecure Design**: Pure static analysis and model synthesis; user code is NEVER executed on the host server.
- **A05: Security Misconfiguration**: CORS strictly whitelisted. Defensive security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).
- **A06: Vulnerable Components**: Automated dependency scanning via pip-audit and Dependabot.
- **A07: Identification and Authentication Failures**: Brute-force rate limiting (5 attempts/min on auth endpoints). Short-lived JWT access tokens (15m).
- **A08: Software and Data Integrity Failures**: Strict Pydantic v2 payload validation. No unsafe deserialization (no pickle/unsafe YAML).
- **A09: Security Logging and Monitoring Failures**: Structured JSON logging. Automated redaction of passwords, tokens, and code snippets. Audit event tracking.
- **A10: Server-Side Request Forgery (SSRF)**: Zero external URL fetching allowed in v1. Outbound network egress constrained to authorized AI API endpoints.

---

## 3. Input Validation & AST Sandboxing

| Constraint | Limit | Enforcement Mechanism | Failure Response |
| :--- | :--- | :--- | :--- |
| **Max Payload Size** | 50 KB | Request Body Length Guard | `HTTP 413 Payload Too Large` |
| **Max Line Count** | 1,500 lines | Pydantic Custom Validator | `HTTP 422 Unprocessable Entity` |
| **Encoding** | Valid UTF-8 | Ingress Decoder | `HTTP 400 Bad Request` |
| **AST Recursion Depth** | 50 levels | Node Visitor Traversal Guard | Graceful truncation with warning |
| **AST Parse Timeout** | 5.0 seconds | Worker Execution Timeout | `HTTP 408 Request Timeout` |
| **Rate Limit (Analysis)** | 20 req / min | SlowAPI Rate Limiter | `HTTP 429 Too Many Requests` |
| **Rate Limit (Auth)** | 5 req / min | SlowAPI Rate Limiter | `HTTP 429 Too Many Requests` |

---

## 4. AI & Prompt Injection Hardening

1. **Instruction Segregation**: System instructions strictly separated from user content.
2. **Boundary Delimiters**: User code encapsulated within `<untrusted_source_code>` markers, with pre-sanitization of closing tags.
3. **Structured Response Schemas**: Pydantic schema validation on all model responses; non-conforming responses rejected immediately.
4. **Zero Execution Privileges**: LLMs have no access to shell, filesystem, database, or network tools.
