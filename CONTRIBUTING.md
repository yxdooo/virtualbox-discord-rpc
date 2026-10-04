# Contributing to virtualbox-discord-rpc

Thank you for your interest in contributing. This document outlines the development workflow, code standards, and contribution process.

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Oracle VM VirtualBox (for live testing)
- Discord desktop client (for rich presence verification)
- Git

### Initializing Environment

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/yxdooo/virtualbox-discord-rpc.git
cd virtualbox-discord-rpc

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -e ".[dev]"
```

---

## Development Workflow

### Code Quality and Linting

We enforce formatting and linting rules using [Ruff](https://github.com/astral-sh/ruff). All code must satisfy Ruff rules prior to submitting a pull request:

```bash
# Check code formatting
ruff format --check .

# Automatically apply formatting
ruff format .

# Run linter
ruff check .
```

### Running Tests

We maintain high test coverage across core modules. Run the test suite using `pytest`:

```bash
pytest --cov=virtualbox_rpc --cov-report=term-missing
```

Ensure all tests pass across platforms before submitting your changes.

---

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification to keep the Git history structured, readable, and machine-parsable.

### Commit Format

```text
<type>(<scope>): <short description in present tense>

[optional body describing motivation and technical rationale]
```

### Allowed Types

- `feat`: A new feature or capability.
- `fix`: A bug fix.
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `test`: Adding or correcting tests.
- `docs`: Documentation updates.
- `chore`: Maintenance, dependencies, or configuration adjustments.

### Examples

- `feat(tray): add status refresh action`
- `fix(vbox): handle paused state in headless vms`
- `test(config): add unit tests for custom icons`

---

## Pull Request Process

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   ```
2. Implement your changes adhering to existing architectural patterns (type annotations, dataclasses, minimal side-effects).
3. Add unit tests for new functionality in the `tests/` directory.
4. Verify that `ruff format --check .`, `ruff check .`, and `pytest` pass cleanly.
5. Submit your Pull Request against the `main` branch with a clear description of the problem and proposed resolution.
