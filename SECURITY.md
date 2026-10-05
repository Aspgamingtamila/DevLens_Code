# Security Policy & Vulnerability Reporting

## 1. Security Philosophy & Realistic Posture

DevLens is **designed with security best practices and continuously tested for common vulnerabilities**.

In compliance with our engineering standards, we make no impossible claims such as "100% secure", "unhackable", or "zero vulnerabilities". All software systems have an attack surface; our commitment is to defense-in-depth, rapid remediation, and transparent disclosure.

---

## 2. Core Architectural Security Controls

1. **Zero Host Execution Policy**:
   - DevLens strictly parses and analyzes source code via Abstract Syntax Trees (AST) and static heuristic rules.
   - User-submitted source code is **never executed directly** on the application host or inside server worker processes.

2. **Prompt Injection Containment**:
   - When educational AI explanations are requested, user code is isolated inside structured XML/tag boundaries (`<untrusted_source_code>`) with escaped terminating tags.
   - LLM responses are strictly validated against strongly-typed Pydantic schemas. Unrecognized or malformed outputs are automatically discarded.

3. **Authentication & Session Security**:
   - Passwords hashed using industry-standard `bcrypt` with adaptive cost factors.
   - Ephemeral JWT access tokens (30-minute expiration) paired with rotating refresh tokens stored as secure, cryptographic hashes.
   - Sliding-window rate limiting on all authentication routes to prevent credential-stuffing and brute-force attacks.

4. **Insecure Direct Object Reference (IDOR) Protection**:
   - Every single database lookup (`GET /api/v1/analyses/{id}`, `DELETE /api/v1/analyses/{id}`) explicitly verifies that `analysis.user_id == current_user.id`. Modifying analysis IDs returns an immediate 404 or 403.

5. **Data Minimization & Automated Log Sanitization**:
   - Passwords, bearer tokens, API keys, and sensitive headers are automatically redacted from application log files using regex masking patterns before persistence.
   - IP addresses stored in audit trails are hashed with a daily salt to protect user privacy.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability within DevLens, please do not open a public GitHub issue. Instead, report it privately via email:

- **Security Contact**: `security@devlens.local` (or file a GitHub Security Advisory)
- **Response SLA**: Initial acknowledgement within 48 hours; status update and remediation timeline within 5 business days.

### Please include in your report:
- Step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
- The affected component, endpoint, or language analyzer.
- Estimated severity and impact on confidentiality, integrity, or availability.

---

## 4. Supported Versions

| Version | Supported | Notes |
| :--- | :--- | :--- |
| `1.0.x` | Yes | Active production release |
| `< 1.0` | No | Prototype / Development builds |
