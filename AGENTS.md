# AGENTS.md

> **Context for AI Agents working on `lshw-windows-emulator`**
> This file provides the essential context, commands, and conventions for AI agents to work effectively on this project.

## 1. Project Overview

**LsHw Windows Emulator** is a simplified Windows port of the [Hardware Lister (lshw)](https://ezix.org/project/wiki/HardwareLiSter) project. It uses Windows Management Instrumentation (WMI) to gather hardware information on Windows systems.

- **Language**: Python 3.6+
- **Platform**: Primarilly Windows 10+, but maintains structure for cross-platform utility.
- **Library Reliance**: `WMI` (Windows specific), `psutil`.

## 2. Setup & Commands

Always use a virtual environment (e.g., `.venv`).

- **Install Dependencies**: `pip install -e .[dev]`
- **Run Emulator (CLI)**: `lshw` (or `python -m lshw`)
- **JSON Output**: `lshw --json`
- **Run Tests**: `pytest`
- **Lint Code**: `ruff check .`
- **Format Code**: `ruff format .`

## 3. Code Style & Conventions

- **Compatibility**: Code MUST be compatible with **Python 3.6+**.
- **Linter/Formatter**: Ruff is authoritative.
- **Quote Style**: Single quotes (`'`) are preferred.
- **WMI Mapping**: Hardware information is gathered by mapping WMI classes to internal `HardwareClass` entities. This logic resides in `lshw/classes.py`.

## 4. Architecture Standards

- **`lshw/`**: Main module.
  - `lshw/classes.py`: Logic for hardware class factory and data formatting.
  - `lshw/wmi_utils.py`: Utilities for interacting with the WMI service.
- **`tests/`**: Unit tests using `pytest` and `pytest-mock`.

## 5. Available Skills & Specialized Constraints

This project is supported by specialized AI Skills in `.agent/skills`. **ALWAYS** check and use these skills:

- **Python Language**: `python-expert` (Pythonic patterns, quality)
- **Bash & Scripting**: `bash-expert` (Integration scripts)
- **QA & Testing**: `qa-expert` (Testing patterns, mocks)
- **Documentation**: `docs-expert` (Diátaxis, ADRs)
- **Output Standards**: `output-standard-expert`

## 6. Critical Rules

1. **Python 3.6 Support**: Maintain compatibility with version 3.6 (e.g., use `dataclasses` backport).
2. **WMI Safety**: Be cautious with WMI queries as they can be performance-heavy or platform-specific.
3. **Cross-Platform**: While it's a "Windows Emulator", ensure the code doesn't crash on non-Windows systems when imported (use `sys_platform` checks).
4. **JSON Integrity**: The `--json` output MUST remain consistent and valid for integration with `migasfree-client`.
