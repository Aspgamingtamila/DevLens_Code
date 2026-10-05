import React, { useState } from 'react';
import {
  BookOpen,
  Shield,
  Layers,
  Cpu,
  Lock,
  Terminal,
  ExternalLink,
  CheckCircle2,
} from 'lucide-react';

export const DocsView: React.FC = () => {
  const [activeSection, setActiveSection] = useState<'architecture' | 'security' | 'languages' | 'dqe'>('architecture');

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 tracking-tight">
          DevLens Documentation & Technical Specifications
        </h2>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Architectural blueprints, security threat modeling, and scoring methodology
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 space-x-2 text-xs font-mono">
        <button
          onClick={() => setActiveSection('architecture')}
          className={`pb-2.5 px-3 border-b-2 font-medium transition-colors ${
            activeSection === 'architecture'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          System Architecture
        </button>

        <button
          onClick={() => setActiveSection('security')}
          className={`pb-2.5 px-3 border-b-2 font-medium transition-colors ${
            activeSection === 'security'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Security & Threat Model
        </button>

        <button
          onClick={() => setActiveSection('dqe')}
          className={`pb-2.5 px-3 border-b-2 font-medium transition-colors ${
            activeSection === 'dqe'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          DQE Quality Score
        </button>

        <button
          onClick={() => setActiveSection('languages')}
          className={`pb-2.5 px-3 border-b-2 font-medium transition-colors ${
            activeSection === 'languages'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Supported Languages
        </button>
      </div>

      {/* Architecture Section */}
      {activeSection === 'architecture' && (
        <div className="space-y-6">
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Clean Architecture & Modular Monolith</span>
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              DevLens is engineered as a clean modular monolith using FastAPI (Python) and React 18 (TypeScript).
              The modular architecture encapsulates analyzers, scoring logic, security controls, and AI abstractions
              behind strict boundaries without the operational overhead and network latency of microservices.
            </p>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs text-slate-300">
              <div className="text-indigo-400 font-semibold mb-2">Code Analysis Pipeline Flow:</div>
              <p className="leading-6">
                1. Request Validation (size caps, MIME checks) <br />
                2. Language Identification & Normalization <br />
                3. Deterministic Static AST Analysis (AST visitors, syntax checking) <br />
                4. Deterministic Complexity Analysis (loop depth, branch factor) <br />
                5. Deterministic Security Rule Checking (SQLi, command injection, buffer overflow) <br />
                6. AI Layer Synthesis (strictly bounded prompt envelope, JSON schema validation) <br />
                7. Findings Combination & Deduplication <br />
                8. Six-Pillar DQE Score Calculation <br />
                9. Framework-Specific Unit Test Generation <br />
                10. Persist and Deliver Structured Response
              </p>
            </div>
          </div>

          <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Zero Host Arbitrary Code Execution
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              A foundational engineering rule of DevLens is that <strong>user code is never executed directly on the host server</strong>.
              All parsing, linting, complexity checks, and test generations are evaluated purely via static AST analysis and
              constrained machine learning models.
            </p>
          </div>
        </div>
      )}

      {/* Security Section */}
      {activeSection === 'security' && (
        <div className="space-y-6">
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
                Security Engineering & Defense-in-Depth
              </h3>
            </div>

            <div className="p-3 bg-slate-950 border border-indigo-500/30 rounded-lg text-xs text-slate-300">
              <span className="font-semibold text-indigo-300">Non-Negotiable Security Policy: </span>
              DevLens is <em>designed with security best practices and continuously tested for common vulnerabilities</em>.
              We reject impossible claims of "100% security" or "unhackability" in favor of rigorous engineering controls.
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-xs font-semibold text-slate-200 font-mono mb-2 flex items-center space-x-1.5">
                  <Lock className="w-3.5 h-3.5 text-indigo-400" />
                  <span>IDOR & Authorization Protection</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Every user resource (analyses, exports, deletion) is strictly validated on the server side against the authenticated user ID.
                  Tampering with analysis IDs in URLs or requests produces an immediate 404/403.
                </p>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-xs font-semibold text-slate-200 font-mono mb-2 flex items-center space-x-1.5">
                  <Shield className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Prompt Injection Boundaries</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Submitted code is enclosed inside strict boundary delimiters (<code className="text-slate-300">&lt;untrusted_source_code&gt;</code>)
                  with escaped closing tags and explicit system instructions to ignore prompt hijacking attempts.
                </p>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-xs font-semibold text-slate-200 font-mono mb-2 flex items-center space-x-1.5">
                  <Terminal className="w-3.5 h-3.5 text-amber-400" />
                  <span>Sliding Window Rate Limiting</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  In-memory and Redis-ready sliding window rate limiters protect the API from brute-force authentication attacks
                  and expensive model exhaustion.
                </p>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-xs font-semibold text-slate-200 font-mono mb-2 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />
                  <span>Automated Log Redaction</span>
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Structured logging filters and masks passwords, JWT tokens, Bearer headers, and secrets before writing to disk.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* DQE Score Section */}
      {activeSection === 'dqe' && (
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
            DevLens Quality Estimate (DQE) Formulation
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            The composite quality score is formulated as a weighted sum of six orthogonal software quality pillars:
          </p>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs text-indigo-300">
            DQE = (0.25 × Correctness) + (0.25 × Security) + (0.15 × Algorithmic Complexity) +
                  (0.15 × Maintainability) + (0.10 × Readability) + (0.10 × Testability)
          </div>

          <div className="space-y-2 text-xs text-slate-300">
            <p>• <strong>Correctness (25%)</strong>: Evaluates absence of runtime faults, syntax errors, and uncaught exceptions.</p>
            <p>• <strong>Security (25%)</strong>: Penalizes OWASP Top 10 vulnerabilities (CWE-89, CWE-78, CWE-120, CWE-79).</p>
            <p>• <strong>Algorithmic Complexity (15%)</strong>: Measures loop nesting depth and asymptotic Big-O execution efficiency.</p>
            <p>• <strong>Maintainability (15%)</strong>: Computed via cyclomatic complexity and Halstead volume heuristics.</p>
            <p>• <strong>Readability (10%)</strong>: Assesses comment ratio, identifier naming conventions, and layout consistency.</p>
            <p>• <strong>Testability (10%)</strong>: Scores modularity and presence of clear functional boundaries amenable to unit testing.</p>
          </div>
        </div>
      )}

      {/* Supported Languages */}
      {activeSection === 'languages' && (
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-mono">
            Initial Supported Language Matrix
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { lang: 'Python', parser: 'Native AST + Regex Heuristics', test: 'pytest' },
              { lang: 'JavaScript', parser: 'Heuristic AST + Regex Rules', test: 'Vitest / Jest' },
              { lang: 'TypeScript', parser: 'Type-Aware Heuristic Parser', test: 'Vitest / Jest' },
              { lang: 'C', parser: 'Safe Memory & Buffer Rules', test: 'Unity / Custom' },
              { lang: 'C++', parser: 'RAII & Pointer Safety Parser', test: 'GoogleTest' },
              { lang: 'Java', parser: 'Class & Exception Analyzer', test: 'JUnit 5' },
            ].map((item) => (
              <div key={item.lang} className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-sm font-bold text-slate-100 font-mono">{item.lang}</h4>
                <p className="text-xs text-slate-400 mt-1">Analyzer: {item.parser}</p>
                <p className="text-xs text-indigo-400 mt-1 font-mono">Test Suite: {item.test}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
