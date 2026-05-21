# USB Controller

> **CLI class:** `usb`
> **WMI source:** `Win32_USBController`
> **Hardware class:** `Usb`
> **Tree position:** Child of `Pci` — parent of `UsbDevice`
> **Generated:** 2026-05-20

## Overview

Represents a USB host controller (UHCI, OHCI, EHCI, or xHCI). One record is returned per USB controller chip detected. Each controller then fetches its associated USB devices as children.

In the full-scan tree, USB controllers are appended at the end of the PCI container's children list (not inside a specific PCI bridge), numbered sequentially as `usb:0`, `usb:1`, etc. The numbering is applied by the `Pci` class during its child-fetch pass.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier (used to filter child USB devices) |
| `DeviceID` | *(used internally)* | WMI device ID |
| `Description` | `description` | Controller description (e.g. `"USB Enhanced Host Controller"`) |
| `Manufacturer` | `vendor` | Controller manufacturer |

## Fixed Fields

| Field | Value |
|-------|-------|
| `class` | `"bus"` |
| `claimed` | `true` |
| `product` | `""` |
| `serial` | `""` |
| `businfo` | `""` |
| `version` | `""` |
| `width` | `0` |
| `clock` | `0` |
| `configuration` | `{driver: "", latency: ""}` |
| `capabilities` | `{uhci: "", bus_master: ""}` |

> **Note:** `id` is initialized to `""` by the class; the final sequential id (`usb:N`) is assigned by the `Pci` class during child collection.

## Output Schema

```json
{
  "id": "usb:0",
  "class": "bus",
  "claimed": true,
  "description": "USB Enhanced Host Controller",
  "vendor": "Intel Corporation",
  "pnpdeviceid": "PCI\\VEN_8086&DEV_A36D&...",
  "configuration": {
    "driver": "",
    "latency": ""
  },
  "capabilities": {
    "uhci": "",
    "bus_master": ""
  },
  "children": [ ... UsbDevice ... ]
}
```

## Interactions

### Full Scan

- **Trigger:** `lshw` — collected as part of the PCI children pass
- **Behavior:** Queries `Win32_USBController` for all USB host controllers. Returns each as a `Hardware` instance. The `Pci` class then numbers them `usb:0`, `usb:1`, etc.

### Children Fetch

- **Trigger:** Full scan with `children=True`
- **Behavior:** `_fetch_children()` instantiates `UsbDevice(dev_id=[self.pnpdeviceid])`. Only USB devices connected to this specific controller are returned and set as `children`.
- **On failure:** Logs `WARNING`, controller children remain empty.

### Single Class Query

- **Trigger:** `lshw --class-hw usb`
- **Behavior:** Returns all USB controllers. IDs will be `""` since numbering is done by `Pci`.
- **On WMI failure:** Exits with error code `10`.

## Business Rules

- `product` is always `""` — `Win32_USBController` does not report a product/model name separately from `Description`.
- `capabilities.uhci` and `capabilities.bus_master` are always empty strings — they are placeholder keys for lshw format compatibility.

## Relationships

- **Parent:** `Pci` (numbered by Pci during full scan)
- **Children:** `UsbDevice`
