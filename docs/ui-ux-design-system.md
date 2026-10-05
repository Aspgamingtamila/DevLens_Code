# DevLens Design System & UI/UX Specification

**Document Version:** 1.0.0  
**Target Path:** `docs/ui-ux-design-system.md`  
**Status:** Approved for Implementation  

---

# 1. Executive Summary & Aesthetic Philosophy

DevLens is an engineering-grade code quality, static analysis, and intelligent remediation workbench.

### Core Design Tenets
1. **Utility-First & Dense Information Architecture**: Inspired by GitHub Code Review, VS Code, Linear, and Sentry. Every pixel communicates status, data, or actionable code.
2. **Anti-Gimmick Strictness**:
   - **STRICTLY FORBIDDEN**: Neon glows, multi-color rainbow gradient meshes, floating purple sparkle icons for AI, pseudo-terminal scanlines, artificial typewriter animation delays.
   - **MANDATED**: Flat surfaces with subtle 1px border contrast, crisp monospace typography, instantaneous UI transitions (150ms-200ms ease), and deterministic diagnostic feedback.
3. **Default Dark Surface with Seamless Light Toggle**: Optimized for long coding sessions (Slate-950/Slate-900 foundation), backed by high-contrast daylight theme (Slate-50/White foundation).
4. **Transparent Provenance**: Zero confusion between deterministic engine facts (AST/regex/compiler lints) and probabilistic LLM outputs. Every finding features explicit provenance badging.

---

# 2. Design Tokens Specification

### Color Tokens
- **Canvas / Background**: `slate-950` (`#020617`) (Dark) / `slate-50` (`#f8fafc`) (Light)
- **Primary Surface / Cards**: `slate-900` (`#0f172a`) (Dark) / `white` (`#ffffff`) (Light)
- **Secondary Surface / Nav**: `slate-800` (`#1e293b`) (Dark) / `slate-100` (`#f1f5f9`) (Light)
- **Borders**: `slate-800` (subtle) / `slate-700` (contrast)
- **Primary Brand / Action**: `indigo-500` / `indigo-600`
- **Severity Colors**:
  - **Critical**: `rose-500` / `rose-400`
  - **High**: `amber-500` / `amber-400`
  - **Medium**: `yellow-500` / `yellow-400`
  - **Low / Info**: `sky-500` / `sky-400`
  - **Success**: `emerald-500` / `emerald-400`

### Provenance Badges
- `[DETERMINISTIC FINDING]`: Slate badge, high-contrast monospace label.
- `[AI SUGGESTION]`: Indigo tint badge, high-contrast monospace label.

---

# 3. Dual-Pane Code Analyzer Architecture

```
+---------------------------------------------------+----------------------------------------------------+
| LEFT PANE: CODE INPUT (50%)                       | RIGHT PANE: ANALYSIS RESULTS (50%)                 |
| [Lang: Python v] [Load Sample v] [Clear]          | [Advisory Disclaimer Banner                       ]|
|---------------------------------------------------| [Overview][Bugs (3)][Security (1)][Complexity]...  |
| 1 | def calculate_tax(subtotal, rate):            |----------------------------------------------------|
| 2 |     if rate < 0:                              | [Score: 78/100]  Time: O(N)   Space: O(1)          |
| 3 |         raise ValueError("Invalid tax")       | Category Scores:                                   |
| 4 |     return subtotal * rate                    | Reliability: [========  ] 80%                      |
|   |                                               | Security:    [======    ] 65%                      |
|---------------------------------------------------|----------------------------------------------------|
| [ Reset ]               [ Analyze Code (Ctrl+Enter) ] | [Issues List]                                      |
+---------------------------------------------------+----------------------------------------------------+
```

### Advisory Banner Requirement
```
DevLens Quality Estimate is an advisory heuristic. AI suggestions are automated recommendations
and must be critically reviewed and validated by engineering staff prior to production deployment.
```
