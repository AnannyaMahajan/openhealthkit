# Contributing to OpenHealthKit

First off, thank you for considering contributing to **OpenHealthKit**! It is people like you who make OpenHealthKit a great open-source developer toolkit for public and community health applications.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## How Can I Contribute?

### 1. Reporting Bugs
- Check existing issues before opening a new bug report.
- Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
- Include clear steps to reproduce and environment details (SQLite or PostgreSQL mode).

### 2. Suggesting Features
- Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).
- Clearly describe the problem and the proposed architectural solution.

### 3. Submitting Pull Requests (PRs)
1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-cool-feature
   ```
2. **Set up local development**:
   ```bash
   pip install -e "./packages/openhealthkit[dev]"
   ```
3. **Run tests & linters**:
   ```bash
   pytest
   ruff check packages/openhealthkit/src
   mypy packages/openhealthkit/src/openhealthkit
   ```
4. **Submit PR**: Target the `main` branch using the [PR Template](.github/PULL_REQUEST_TEMPLATE.md).

---

## Development Conventions

- Follow **PEP 8** for Python and **TypeScript** strict mode for dashboard code.
- Use explicit type hints on all public functions.
- Do not commit secrets, private keys, or `.env` files.
