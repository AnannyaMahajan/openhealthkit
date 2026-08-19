# Security & Compliance Guidelines

Security is vital when developing software for community and public-health applications. OpenHealthKit provides foundational technical security building blocks out-of-the-box.

---

## Technical Security Features

- **Password Security**: Passwords are hashed using **Argon2id** (with PBKDF2-HMAC-SHA256 fallback). Plaintext passwords are never stored.
- **JWT Authentication**: Short-lived access tokens (HMAC-SHA256) and refresh tokens.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions enforced at FastAPI dependency layer (`require_permission`).
- **Security Headers**: Standard headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`).
- **Audit Logging**: Structured log entries capturing sensitive actions in `AuditLog`.

---

## Regulatory Compliance Disclaimer

> [!WARNING]
> OpenHealthKit is an open-source technical developer toolkit. Installing or incorporating OpenHealthKit does **NOT** automatically grant HIPAA, GDPR, or local health regulation compliance. Full regulatory compliance depends on deployment infrastructure, organizational operational security, access controls, data encryption at rest/transit, and jurisdictional policies.

---

## Responsible Vulnerability Disclosure

To report security vulnerabilities, please refer to [SECURITY.md](SECURITY.md) in the repository root or contact `security@openhealthkit.org`.
