# 🛠️ How to Add a New Hardware Class

This guide walks you through the steps required to implement a new hardware component in `lshw-windows-emulator`.

## 📦 Implementation Steps

Follow these steps to ensure your hardware class integrates correctly with the factory pattern and the discovery tree.

### 1. Create the Module

Create a new file in `lshw/classes/` named after your device (e.g., `lshw/classes/your_device.py`).

### 2. Implement the Class

Inherit from `HardwareClass` and use the `@HardwareClass.register` decorator to link it to its parent in the hardware tree.

```python
from .hardware_class import HardwareClass

@HardwareClass.register('YourDevice', parent='ParentName')
class YourDevice(HardwareClass):
    """
    Retrieves information about YourDevice using WMI.
    """

    def __init__(self):
        super().__init__()
        # 1. Define the WMI method to call
        self.wmi_method = 'Win32_YourWmiClass'
        
        # 2. List the properties you want to fetch
        self.properties_to_get = ['Caption', 'Description', 'DeviceID']
        
        # 3. Synchronize properties with return dictionary
        self._update_properties_to_return()

    def format_data(self, children=False):
        """
        Standardizes the raw WMI data into the expected format.
        """
        # Execute the WQL query
        self.get_hardware()
        
        # Return the processed data
        return [hw_item for hw_item in self.hardware_set_to_return]
```

### 3. Register the Class

Import your new class in `lshw/classes/__init__.py` to ensure the `@register` decorator is executed during discovery.

```python
# lshw/classes/__init__.py
from .your_device import YourDevice
```

### 4. Enable CLI Access

If you want the class to be accessible directly via the CLI, add it to the `AVAILABLE_CLASSES` list in `lshw/__main__.py`.

```python
# lshw/__main__.py
AVAILABLE_CLASSES = [
    ...,
    'yourdevice',
]
```

## 🧪 Testing Your Implementation

Before submitting, verify your change with the built-in test suite:

1. Run the CLI directly: `python -m lshw --class yourdevice --json`
2. Add a new test file in `tests/test_your_device.py` using `pytest-mock` to simulate WMI responses.

---
> [!TIP]
> Always check the [WMI Class Reference](https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-provider) to identify the correct properties.

> [!NOTE]
> This guide follows the **Diátaxis How-To Quadrant**, focusing on specific goal-oriented steps.
