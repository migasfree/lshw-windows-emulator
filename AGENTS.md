# AGENTS.md

> **Context for AI Agents working on `lshw-windows-emulator`**
> This file provides the essential context, commands, and conventions for AI agents to work effectively on this project.

## 1. Project Overview

**LsHw Windows Emulator** is a simplified Windows port of the [Hardware Lister (lshw)](https://ezix.org/project/wiki/HardwareLiSter) project. It uses Windows Management Instrumentation (WMI) to gather hardware information on Windows systems.

- **Language**: Python 3.6+
- **Platform**: Primarily Windows 10+, but maintains structure for cross-platform utility.
- **Library Reliance**: `WMI` >= 1.5.1 (Windows-only), `psutil` >= 6.0.0.

## 2. Setup & Commands

Always use a virtual environment (e.g., `.venv`).

- **Install Dependencies**: `pip install -e .[dev]`
- **Run Emulator (CLI)**: `lshw` (or `python -m lshw`)
- **JSON Output**: `lshw --json`
- **Run Tests**: `pytest`
- **Lint Code**: `ruff check .`
- **Format Code**: `ruff format .`
- **Run Coverage**: `pytest --cov=lshw` (gate at 70%)

## 3. Code Style & Conventions

- **Compatibility**: Code MUST be compatible with **Python 3.6+**.
- **Linter/Formatter**: Ruff is authoritative. Rules: `E`, `W`, `F`, `I`, `N`, `UP`, `B`, `C4`, `SIM`, `RUF`.
- **Quote Style**: Single quotes (`'`) are preferred.
- **Line Length**: 120 characters.
- **Security**: All WMI access is gated by `_validate_entity()` against `_WMI_ENTITY_ALLOWLIST` (frozenset, case-insensitive). WQL injection is prevented via `_sanitize_wql_value()`.

## 4. Architecture Standards

The project uses three design patterns: **Factory + Registry**, **Template Method**, and **Singleton**.

- **`lshw/__main__.py`**: CLI entry point. Parses `--json`/`-j` and `--class-hw`/`-c` arguments. Dispatches via `HardwareClass.factory()`.
- **`lshw/classes/hardware_class.py`**: Abstract base class. Contains `WMIConnection` singleton, `_WMI_ENTITY_ALLOWLIST` (22 entities, normalized lowercase), `factory()`/`register()`/`get_children()` class methods, `_validate_entity()` security gate, `_sanitize_wql_value()` WQL injection defense, `format_data()` template method.
- **`lshw/classes/hardware.py`**: `@dataclass` with 30 fields and `to_dict()` serialization.
- **`lshw/classes/__init__.py`**: Auto-discovers all modules via `pkgutil.iter_modules()`, triggering `@HardwareClass.register()` decorators.
- **`lshw/classes/*.py`**: 17 hardware subclasses, each mapping one WMI entity to the `Hardware` dataclass. Form a tree: `ComputerSystem → BaseBoard → {Firmware, Processor, PhysicalMemory, Pci → {Ide, Usb, GraphicCard, SoundDevice, NetworkCard}, ...}`.
- **`tests/`**: 17 test files using `pytest` and `pytest-mock`. `conftest.py` injects a mock `wmi` module for cross-platform testing.

**Architecture Decision Records** in `docs/adr/`:
- [001](docs/adr/001-factory-registry-pattern.md) — Factory + Registry Pattern
- [002](docs/adr/002-wmi-entity-allowlist.md) — WMI Entity Allowlist Security
- [003](docs/adr/003-name-matching-strategy.md) — Device ID Normalization

## 5. Available Skills & Specialized Constraints

This project is supported by specialized AI Skills in `.agent/skills`. **ALWAYS** check and use these skills:

- **Python Language**: `python-expert` (Pythonic patterns, quality)
- **Bash & Scripting**: `bash-expert` (Integration scripts)
- **Security**: `security-expert` (AppSec, allowlist, injection defense)
- **QA & Testing**: `qa-expert` (Testing patterns, mocks)
- **CI/CD**: `cicd-expert` (GitHub Actions, pip-audit)
- **Documentation**: `docs-expert` (Diátaxis, ADRs)

## 6. Critical Rules

1. **Python 3.6 Support**: Maintain compatibility with version 3.6. Use `dataclasses` backport for Python < 3.7.
2. **WMI Allowlist**: Every new WMI entity must be added to `_WMI_ENTITY_ALLOWLIST` in lowercase. The allowlist is a `frozenset` — immutable at runtime.
3. **WMI Safety**: All `except Exception:` blocks should include `logger.debug()` for operational visibility. WMI queries can fail silently on different Windows versions.
4. **Cross-Platform**: Non-Windows systems inject a stub `wmi` module. Tests run on Linux via the mock in `conftest.py`.
5. **Coverage Gate**: Tests must maintain >= 70% coverage (`--cov-fail-under=70` in `pyproject.toml`).
6. **JSON Integrity**: The `--json` output must remain consistent for integration with `migasfree-client`.
