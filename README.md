# DevLens: Production-Grade Code Intelligence, Debugging & Learning Platform

[![CI/CD Pipeline](https://github.com/your-org/devlens/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/devlens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)

> **DevLens** is a transparent, developer-grade code analysis and debugging platform engineered to inspect source code, detect critical security vulnerabilities, estimate asymptotic algorithmic complexity, formulate unit tests, and provide actionable educational remediations.
>
> *Designed as a flagship portfolio project for a Computer Science & Engineering (AI/ML) student, adhering to strict enterprise software engineering standards.*

---

## ⚠️ Important Engineering & Security Disclaimers

### 1. Realistic Security Posture
DevLens is **designed with security best practices and continuously tested for common vulnerabilities**.  
We reject impossible marketing claims such as *"100% secure"*, *"unhackable"*, or *"zero vulnerabilities"*. All software possesses an attack surface; our architecture prioritizes defense-in-depth, least privilege, and transparent risk boundaries.

### 2. Advisory Quality Heuristic & Human-in-the-Loop
The **DevLens Quality Estimate (DQE)** and all AI-generated suggestions are **strictly advisory recommendations**. Automated findings and generated test suites must be critically verified by software engineers before deploying to production environments.

### 3. Transparent Intelligence Architecture
DevLens is **not** a black-box wrapper around an LLM. It operates an integrated pipeline combining **deterministic AST static analysis**, **heuristic complexity parsers**, and **bounded AI model synthesis**.

### 4. Zero Host Arbitrary Code Execution
User-submitted source code is **never compiled or executed on the host server**. All diagnostics and tests are formulated via static AST tree parsing and model inference.

---

## 🚀 Key Features

- **Multi-Language Static & Semantic Analysis**:
  - Out-of-the-box support for **Python**, **JavaScript**, **TypeScript**, **C**, **C++**, and **Java** with an extensible analyzer registry.
- **OWASP & CWE Vulnerability Mapping**:
  - Deterministic detection of SQL Injection (`CWE-89`), Command Injection (`CWE-78`), Buffer Overflow (`CWE-120`), Format String Vulnerabilities (`CWE-134`), and Insecure Deserialization (`CWE-502`).
- **Big-O Complexity Estimation**:
  - Theoretical Upper Bounds for Time Complexity (e.g. $\mathcal{O}(1)$, $\mathcal{O}(N)$, $\mathcal{O}(N^2)$) and Auxiliary Space Complexity derived via AST loop depth and recursion heuristics.
- **Automated Unit Test Generation**:
  - Generates framework-tailored unit test suites (`pytest` for Python, `vitest`/`jest` for JS/TS, `JUnit 5` for Java, `GoogleTest` for C++).
- **Six-Pillar DevLens Quality Estimate (DQE)**:
  - Transparent 0–100 composite score based on: Correctness (25%), Security (25%), Algorithmic Complexity (15%), Maintainability (15%), Readability (10%), and Testability (10%).
- **Interactive Dual-Pane Workbench**:
  - Left pane code editor with line gutter, syntax presets, and `Ctrl+Enter` trigger.
  - Right pane tabbed diagnostic workbench with clear provenance badging: `[DETERMINISTIC RULE]` vs `[AI SUGGESTION]`.
- **User Authentication & Privacy**:
  - Passwords hashed with `bcrypt`. Short-lived JWT access tokens and rotating refresh tokens.
  - Insecure Direct Object Reference (IDOR) prevention across all analysis routes.
  - One-click account and history deletion (GDPR/CCPA compliant).
  - Safe export as Markdown and JSON.

---

## 🏗️ Architecture & Pipeline Flow

DevLens is built as a **clean modular monolith** to balance high performance and low operational complexity without premature microservice overhead.

```
                    User Submits Code
                           │
                           ▼
               1. Request Validation & Size Caps
                           │
                           ▼
               2. Language Normalization & Routing
                           │
                           ▼
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
3. Deterministic AST Engine           4. Heuristic Complexity Analyzer
   (AST visitors, regex linter,          (Loop depth, recursion detector,
   CWE security rules)                    space allocation heuristics)
       │                                       │
       └───────────────────┬───────────────────┘
                           │
                           ▼
               5. Bounded AI Synthesis
                  (Strict XML envelope: <untrusted_source_code>,
                  structured JSON schema validation, fallback)
                           │
                           ▼
               6. Findings Combiner & Deduplication
                           │
                           ▼
               7. Six-Pillar DQE Score Calculation
                           │
                           ▼
               8. Framework-Specific Test Generation
                           │
                           ▼
               9. Persist Result & Return Structured Report
```

---

## 🛠️ Technology Stack

| Layer | Technologies | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript 5, Vite 6, Tailwind CSS, Lucide Icons | Responsive, accessible, type-safe developer workbench. |
| **Backend** | Python 3.11/3.12, FastAPI, Pydantic v2 | High-throughput asynchronous API, automatic OpenAPI schemas, type validation. |
| **Database** | SQLAlchemy 2.0 (Sync), SQLite (Dev/Test) / PostgreSQL (Prod) | Portable, zero-dependency local testing with seamless production scale. |
| **Security** | Bcrypt, PyJWT, Sliding-Window Rate Limiting, Sanitized Logging | Defense-in-depth, IDOR mitigation, secret masking. |
| **AI / ML** | Pluggable `AIProvider` (Mock Provider + Google Gemini API) | Flexible offline hermetic development with production AI synthesis. |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Reproducible multi-stage container builds and continuous testing. |

---

## ⚡ Quickstart & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### 1. Clone & Configure Environment
```bash
git clone https://github.com/your-org/devlens.git
cd devlens

# Copy environment variables template
cp .env.example .env
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend development server (defaults to SQLite: devlens.db)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The interactive Swagger API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🐳 Docker Container Deployment

Run both frontend and backend in production-ready isolated containers:

```bash
docker-compose up --build
```
- Frontend UI: [http://localhost:80](http://localhost:80)
- Backend API & Healthcheck: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🧪 Testing & Verification

DevLens includes comprehensive automated unit, integration, and security tests:

```bash
# Run complete test suite with coverage
python -m pytest -v tests/
```

### Test Coverage Highlights:
- **Unit Tests**:
  - `tests/unit/test_analyzers.py`: Deterministic AST and regex pattern detection for Python, JS, TS, C, C++, and Java.
  - `tests/unit/test_scoring.py`: Mathematical verification of the 6-pillar DQE formula across flawless, buggy, and vulnerable code.
  - `tests/unit/test_security.py`: Input length caps, prompt injection boundary escaping, and sensitive log redaction.
- **Integration Tests**:
  - `tests/integration/test_auth_api.py`: User registration, login, token refresh rotation, and profile retrieval.
  - `tests/integration/test_analyses_api.py`: Code analysis workflow, IDOR authorization validation, and deletion cascading.

---

## 📚 API Reference Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health and engine status | No |
| `POST` | `/api/v1/auth/register` | Register a new developer account | No |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access & refresh tokens | No |
| `POST` | `/api/v1/auth/refresh` | Rotate expired access token | No |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes |
| `DELETE` | `/api/v1/auth/account` | Permanently delete account and all history | Yes |
| `POST` | `/api/v1/analyses/` | Submit code snippet for complete analysis | Optional |
| `GET` | `/api/v1/analyses/` | List user analysis history with pagination | Yes |
| `GET` | `/api/v1/analyses/{id}` | Retrieve full report by ID (IDOR protected) | Yes |
| `DELETE` | `/api/v1/analyses/{id}` | Delete analysis record | Yes |
| `GET` | `/api/v1/analyses/{id}/export` | Export report as JSON or Markdown | Yes |

---

## 🔒 Security & Privacy Commitments

- **Zero Host Arbitrary Code Execution**: User code is strictly parsed via AST and regex rules.
- **Strict IDOR Prevention**: Users can only query and mutate their own analyses.
- **Prompt Injection Boundary Protection**: Untrusted user code is escaped and quarantined within `<untrusted_source_code>` boundary tags.
- **Automatic Secret Redaction**: Application logs filter and mask tokens, passwords, and sensitive headers.
- **Right to Erasure**: Complete account and data deletion via `/api/v1/auth/account`.

For full details, review [SECURITY.md](SECURITY.md) and [PRIVACY.md](PRIVACY.md).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
