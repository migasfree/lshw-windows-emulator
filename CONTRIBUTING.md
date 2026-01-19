# Contributing to lshw-windows-emulator

Thank you for considering contributing to `lshw-windows-emulator`! We welcome contributions from everyone.

## Getting Started

1.  **Read the Onboarding Guide**: Please start by reading [ONBOARDING.md](ONBOARDING.md). It contains essential information about the project architecture, environment setup, and development workflow.
2.  **Fork the Repository**: Create a fork of the project on GitHub.
3.  **Clone your Fork**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/lshw-windows-emulator.git
    cd lshw-windows-emulator
    ```
4.  **Set up the Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .[dev]
    ```

## Development Workflow

1.  **Create a Branch**: Always work on a new branch for your changes.
    ```bash
    git checkout -b features/my-new-feature
    ```
2.  **Make Changes**: Implement your feature or fix.
3.  **Run Tests**: Ensure all tests pass.
    ```bash
    pytest
    ```
4.  **Lint Your Code**: Ensure your code meets quality standards.
    ```bash
    ruff check .
    ruff format .
    ```

## Coding Standards

- **Python Version**: Code must be compatible with **Python 3.6+**.
- **Style**: We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. configuration is in `pyproject.toml`.
- **Type Hints**: While not strictly enforced everywhere yet, we encourage using type hints for new code.

## Submitting a Pull Request

1.  Push your branch to your fork.
2.  Open a Pull Request against the `master` branch.
3.  Provide a clear description of your changes.
4.  WaitFor review and address any feedback.

## Reporting Issues

If you find a bug or have a suggestion, please open an issue in the [GitHub Issue Tracker](https://github.com/migasfree/lshw-windows-emulator/issues).
