# Security Policy & Responsible Disclosure

OpenHealthKit takes security and data safety seriously. We appreciate the work of security researchers and open-source contributors in making software safer for everyone.

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

---

## Reporting a Vulnerability

If you discover a security vulnerability in OpenHealthKit, please do **NOT** open a public GitHub issue.

Instead, please send a detailed security report to:
📧 **security@openhealthkit.org**

### Please include:
1. Description of the vulnerability and potential impact.
2. Steps to reproduce or proof-of-concept code.
3. Affected components (e.g. JWT Auth, Sync Engine, REST API).

We will acknowledge receipt of your report within 48 hours and work towards a timely patch and public disclosure notice.

---

## Security Architecture & Best Practices

- **Password Hashing**: Uses **Argon2id** (with PBKDF2-HMAC-SHA256 fallback). Plaintext passwords are never logged or stored.
- **Secret Key Handling**: Uses environment variables (`JWT_SECRET_KEY`). No secrets are committed to the repository.
- **Audit Logging**: Captures administrative and security operations in `AuditLog`.
- **Dependency Scanning**: Automated CI workflow (`.github/workflows/security.yml`) checks for vulnerable dependencies.

---

## Regulatory Compliance Statement

> [!IMPORTANT]
> **OpenHealthKit is a technical building block software library.**
> Incorporating or deploying OpenHealthKit does **not** by itself constitute compliance with HIPAA, GDPR, or local health regulations. 
> Comprehensive compliance depends on your organization's deployment infrastructure, operational access controls, encryption of data at rest and in transit, cloud provider security, and administrative policies.
