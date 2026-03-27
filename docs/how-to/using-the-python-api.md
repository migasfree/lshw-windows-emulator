# 🐍 Using the Python API

While `lshw-windows-emulator` is primarily used as a CLI tool, you can also integrate it directly into your Python projects.

## Basic Integration

The core of the library is the `HardwareClass` factory. You can request any supported hardware class and fetch its data.

```python
from lshw.classes import HardwareClass

# Get the main ComputerSystem object
system = HardwareClass.factory('ComputerSystem')()

# Format the data (children=True will perform a full recursive scan)
formatted_data = system.format_data(children=True)

# Each element in the list is a Hardware object
for item in formatted_data:
    # Convert to a dictionary for easy processing or JSON export
    data_dict = item.to_dict()
    print(f"Vendor: {data_dict.get('vendor')}")
    print(f"Product: {data_dict.get('product')}")
```

## Extracting Specific Classes

You can also target specific hardware classes if you don't need a full system scan:

```python
from lshw.classes import HardwareClass

# Target only network cards
network = HardwareClass.factory('NetworkCard')()
cards = network.format_data()

for card in cards:
    print(f"Interface: {card.logicalname}")
    print(f"MAC: {card.serial}")
```

## Error Handling

When using the API, be aware that WMI queries can fail due to permissions or system-specific errors:

```python
import sys
from lshw.classes import HardwareClass

try:
    processor = HardwareClass.factory('Processor')()
    data = processor.format_data()
except Exception as e:
    print(f"Error gathering CPU info: {e}")
```

For more details on available classes, see the [WMI Mapping Reference](../reference/wmi-mapping.md).
