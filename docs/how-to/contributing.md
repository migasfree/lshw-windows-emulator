# 🤝 Contributing to lshw-windows-emulator

Thank you for considering contributing to `lshw-windows-emulator`! We welcome contributions from everyone.

## 🚀 Getting Started

1. **Read the Architecture Overview**: Please start by reading the [Architecture](explanation/architecture.md) documentation.
2. **Fork the Repository**: Create a fork of the project on GitHub.
3. **Clone your Fork**:

    ```bash
    git clone https://github.com/YOUR_USERNAME/lshw-windows-emulator.git
    cd lshw-windows-emulator
    ```

## 🛠️ Development Workflow

1. *Set up the local Environment**:

    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux
    source .venv/bin/activate

    pip install -e ".[dev]"
    ```

2. *Create a Branch**: Always work on a new branch for your changes.

    ```bash
    git checkout -b features/my-new-feature
    ```

3. *Make Changes**: Implement your feature or fix.
4. *Run Tests**: Ensure all tests pass.

    ```bash
    pytest
    ```

5. *Lint Your Code**: Ensure your code meets quality standards using [Ruff](https://docs.astral.sh/ruff/).

    ```bash
    ruff check .
    ruff format .
    ```

## 📋 Coding Standards

- **Python Compatibility**: Code MUST be compatible with **Python 3.6+**. Avoid features introduced in later versions (e.g., structural pattern matching, f-string `=` specifiers).
- **Style**: We use Ruff for linting and formatting. configuration is in `pyproject.toml`.
- **Type Hints**: We encourage using type hints for new code to improve reliability and IDE support.

## 🚀 Submitting a Pull Request

1. ush your branch to your fork.
2. pen a Pull Request against the `master` branch.
3. rovide a clear description of your changes.
4. wait review and address any feedback.

---
> [!NOTE]
> This guide follows the **Diátaxis How-To Quadrant**, focusing on specific goal-oriented steps.
