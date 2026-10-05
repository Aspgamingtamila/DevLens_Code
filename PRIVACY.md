# DevLens Privacy Policy

**Effective Date:** 2026-10-05  
**Version:** 1.0.0

---

## 1. Information We Collect

1. **Account Information**: When registering an account, we collect your email address, hashed password (using bcrypt), and optional full name.
2. **Analysis Data**: Source code snippets and language metadata submitted to DevLens for static and AI analysis.
3. **Usage & Diagnostic Metrics**: Anonymous timestamps, hashed client IP addresses (anonymized via salted cryptographic hashes), and HTTP request latency.

---

## 2. How Your Code is Handled

- **Zero Unsanctioned Retention**: We do not sell, rent, or distribute your source code.
- **AI Processing**: If you select "AI Explanations", your code is sent securely via TLS to the selected LLM provider (e.g. Google Gemini API) solely to generate structural recommendations, test cases, and bug explanations. We do not use your source code to train third-party models.
- **Offline / Hermetic Mode**: When using the hermetic mock engine, code never leaves your local or self-hosted deployment.

---

## 3. Data Deletion & User Rights (GDPR / CCPA)

You maintain complete ownership of your data:

- **Delete Individual Analyses**: Remove any saved analysis report instantly from the History tab.
- **Account & History Purge**: Under Settings > Danger Zone, click "Delete Account" to permanently cascade-delete your user record, credentials, all historical analyses, findings, metrics, and generated tests.

---

## 4. Contact

For privacy inquiries, please contact `privacy@devlens.local`.
