# Developer Onboarding

## Architecture

```
lshw/
├── __init__.py          # Version
├── __main__.py          # CLI entry point
└── classes/
    ├── hardware_class.py    # Base class with factory pattern
    ├── computer_system.py   # Root: system info
    ├── base_board.py        # Motherboard → children: Firmware, Processor, Memory, Pci
    ├── pci.py               # PCI bus → children: Ide, Usb, NetworkCard, GraphicCard, SoundDevice
    ├── physical_disk.py     # HDD/SSD → PartitionDisk → LogicalDisk
    └── ...                  # Other hardware classes
```

## Key Concepts

### Factory Pattern

```python
@HardwareClass.register('NetworkCard')
class NetworkCard(HardwareClass):
    ...

# Usage
cls = HardwareClass.factory('NetworkCard')
data = cls().format_data()
```

### Return Type Convention

- **Singleton components** (one per system) → `dict`: ComputerSystem, BaseBoard, Firmware, PhysicalMemory, Pci
- **Multi-instance** → `list[dict]`: Processor, NetworkCard, PhysicalDisk, etc.

### WMI Utilities

```python
wql = self.build_wql_select('Win32_NetworkAdapter', 'PhysicalAdapter=True')
self.execute_wql_query(wql)
```

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

# Linting
ruff check lshw/
ruff format lshw/
```

## Adding a New Hardware Class

1. Create `lshw/classes/your_device.py`:

```python
from copy import deepcopy
from .hardware_class import HardwareClass

@HardwareClass.register('YourDevice')
class YourDevice(HardwareClass):
    def __init__(self):
        super().__init__()
        self.wmi_method = 'Win32_YourWmiClass'
        self.properties_to_get = ['Property1', 'Property2']
        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()
        return [hw_item for hw_item in self.hardware_set_to_return]
```

2. Add import to `lshw/classes/__init__.py`
3. Add to `AVAILABLE_CLASSES` in `__main__.py` for CLI access

## Resources

- [WMI Classes Reference](https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-provider)
- [Original lshw](https://ezix.org/project/wiki/HardwareLiSter)
