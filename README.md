# LsHw Windows Emulator

[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Windows port of [Hardware Lister (lshw)](https://ezix.org/project/wiki/HardwareLiSter) using WMI.

## Installation

```bash
pip install lshw
```

Or from source:

```bash
git clone https://github.com/migasfree/lshw-windows-emulator.git
cd lshw-windows-emulator
pip install .
```

## Usage

```bash
# All hardware info
lshw

# JSON output
lshw --json

# Specific class
lshw -c network

# List available classes
lshw -c list
```

### Available Classes

`system` `baseboard` `bios` `processor` `memory` `pci` `ide` `disk` `partition` `volume` `usb` `usbdevices` `cdrom` `video` `network` `sound`

### Python API

```python
from lshw.classes import HardwareClass

system = HardwareClass.factory('ComputerSystem')()
data = system.format_data(children=True)
```

## Requirements

- Windows 10+
- Python >= 3.6

## 📖 Documentation

Full documentation is available in the `docs/` directory and can be built using [MkDocs](https://www.mkdocs.org/):

- **[Installation Guide](docs/index.md#installation)**: Quick start and requirements.
- **[Architecture Deep-Dive](docs/explanation/architecture.md)**: Understanding the core design and WMI mapping.
- **[Developer Guide](docs/how-to/contributing.md)**: How to set up development environment and submit PRs.
- **[Adding Hardware Support](docs/how-to/adding-hardware-classes.md)**: Step-by-step guide for new hardware classes.
- **[Troubleshooting](docs/how-to/troubleshooting.md)**: Common issues with WMI and Windows permissions.

## 🛠️ Development

Run `mkdocs serve` to view the live documentation site.

## License

[GNU GPL v3](LICENSE)

## Authors

See [AUTHORS](AUTHORS) file.

## Links

- [GitHub](https://github.com/migasfree/lshw-windows-emulator)
- [Issues](https://github.com/migasfree/lshw-windows-emulator/issues)
- [migasfree](https://migasfree.org)
