# 🔍 LsHw Windows Emulator Documentation

Welcome to the official documentation for the **LsHw Windows Emulator**, a specialized tool designed to gather comprehensive hardware information on Windows systems, mimicking the standard `lshw` tool found in Linux environments.

## 🚀 Quick Start

Get started with the emulator in seconds.

### Installation

```bash
# Clone the repository
git clone https://github.com/migasfree/lshw-windows-emulator.git
cd lshw-windows-emulator

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode
pip install -e .
```

### Basic Usage

```bash
# Run the full system scan
lshw

# Output as JSON for integration
lshw --json

# Query a specific hardware class (e.g., Network Card)
lshw --class network
```

## 🗺️ Documentation Roadmap

Explore the documentation through its four **Diátaxis quadrants**:

| Quadrant | Focus | Explore |
| :--- | :--- | :--- |
| **📘 Tutorials** | Learning-oriented help for beginners. | [Quick Start](#-quick-start) |
| **🛠️ How-to Guides** | Goal-oriented steps for specific tasks. | [Add Hardware Classes](how-to/adding-hardware-classes.md), [Python API](how-to/using-the-python-api.md) |
| **📋 Reference** | Technical descriptions (CLI, WMI Mapping). | [CLI Usage](reference/cli.md), [WMI Mapping](reference/wmi-mapping.md) |
| **💡 Explanation** | Understanding-oriented background & concepts. | [Architecture](explanation/architecture.md) |

---
> [!TIP]
> This documentation is a "Living Document" and is updated with every architectural change.

---
*Maintained by the Migasfree Team.*
