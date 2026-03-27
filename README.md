# LsHw Windows Emulator

[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Windows port of [Hardware Lister (lshw)](https://ezix.org/project/wiki/HardwareLiSter) using WMI.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/migasfree/lshw-windows-emulator.git
cd lshw-windows-emulator

# Install it locally
pip install -e .

# Run a full scan
lshw
```

For detailed installation options and usage, see the [Quick Start Guide](docs/index.md#🚀-quick-start).

## 📖 Documentation

The full documentation is structured according to the **Diátaxis framework** and is available in the `docs/` directory.

- **[Installation Guide](docs/index.md#🚀-quick-start)**: Prerequisites and installation options.
- **[CLI Reference](docs/reference/cli.md)**: Full command list and hardware classes.
- **[Python API](docs/how-to/using-the-python-api.md)**: Guide on using the library programmatically.
- **[WMI Mapping](docs/reference/wmi-mapping.md)**: Techincal reference on WMI source classes.
- **[Architecture Deep-Dive](docs/explanation/architecture.md)**: Internal design and concepts.
- **[Troubleshooting](docs/how-to/troubleshooting.md)**: Fix common WMI and permission issues.

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
