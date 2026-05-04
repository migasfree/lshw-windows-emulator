# How to Add a New Hardware Class

This guide walks through implementing a new hardware component in `lshw-windows-emulator`.

## Implementation Steps

### 1. Create the Module

Create a new file in `lshw/classes/` named after your device (e.g., `lshw/classes/your_device.py`).

### 2. Implement the Class

Inherit from `HardwareClass` and use the `@HardwareClass.register` decorator to link it to its parent in the hardware tree. Override `_populate_hardware()` to map WMI data to `Hardware` fields.

```python
import logging

from .hardware import Hardware
from .hardware_class import HardwareClass

logger = logging.getLogger(__name__)


@HardwareClass.register('YourDevice', parent='ParentName')
class YourDevice(HardwareClass):

    def __init__(self):
        super().__init__()
        self.wmi_method = 'Win32_YourWmiClass'
        self.properties_to_get = ['Caption', 'Description', 'DeviceID']
        self._update_properties_to_return()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.id = hw_item.get('DeviceID', self.__ERROR__)
        item_ret.description = hw_item.get('Caption', self.__DESC__)
        return item_ret
```

### 3. Registration (Automatic)

The package `__init__.py` uses `pkgutil.iter_modules()` to auto-discover all `.py` files in the `lshw/classes/` directory. The `@HardwareClass.register` decorator is triggered at import time — **no manual import registration is required**. Simply placing the file in the package is sufficient.

### 4. Enable CLI Access

Add the class to `AVAILABLE_CLASSES` in `lshw/__main__.py`:

```python
AVAILABLE_CLASSES = {
    ...,
    'yourdevice': ['YourDevice', 17],
}
```

The integer is the exit code used when the class fails to retrieve data (must be unique, `2`–`15` range).

### 5. Ensure WMI Entity is Registered

Verify the WMI entity your class uses is in `_WMI_ENTITY_ALLOWLIST` in `lshw/classes/hardware_class.py`. The allowlist gates all WMI access — unknown entities are rejected with a `Security Alert` log and `ValueError`. Entity names are compared case-insensitively.

## Testing

1. Add a test file at `tests/test_your_device.py` using `pytest-mock` to simulate WMI responses.
2. The `conftest.py` mock injects a fake `wmi` module into `sys.modules`, allowing tests to run on Linux.
3. Run: `pytest tests/test_your_device.py`

## WMI Entity Security

All WMI access is protected by:

- **`_validate_entity(entity)`** — Case-insensitive allowlist check. Raises `ValueError` for unauthorized entities.
- **`_sanitize_wql_value(value)`** — Strips `"`, `'`, `;` from WQL WHERE clause values to prevent injection.

See [ADR 002: WMI Entity Allowlist](../adr/002-wmi-entity-allowlist.md) for the full security rationale.
