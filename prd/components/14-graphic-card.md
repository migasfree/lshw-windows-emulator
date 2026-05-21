# Graphics Card (Video Controller)

> **CLI class:** `video`
> **WMI source:** `Win32_VideoController`
> **Hardware class:** `GraphicCard`
> **Tree position:** Child of `Pci` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents a graphics adapter (integrated or discrete). Multiple GPU entries may appear if the system has both an integrated Intel GPU and a dedicated NVIDIA/AMD card. Each is returned as a separate record.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Description` | `description` | Full adapter description (e.g. `"NVIDIA GeForce RTX 3080"`) |
| `VideoProcessor` | `product` | GPU chip/processor name (e.g. `"GeForce RTX 3080"`) |
| `AdapterCompatibility` | `vendor` | Adapter vendor string (e.g. `"NVIDIA"`) |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier |

Collected but not mapped: `DeviceID`.

## Fixed Fields

| Field | Value |
|-------|-------|
| `id` | `"display"` |
| `class` | `"display"` |
| `claimed` | `true` |
| `businfo` | `""` |
| `version` | `""` |
| `width` | `0` |
| `clock` | `0` |
| `serial` | `""` |
| `configuration` | `{driver: "", latency: ""}` |
| `capabilities` | `{msi:"", pm:"", vga:"", bus_master:"", cap_list:"", rom:""}` |

## Output Schema

```json
{
  "id": "display",
  "class": "display",
  "claimed": true,
  "description": "NVIDIA GeForce RTX 3080",
  "product": "GeForce RTX 3080",
  "vendor": "NVIDIA",
  "pnpdeviceid": "PCI\\VEN_10DE&DEV_2206&...",
  "configuration": {
    "driver": "",
    "latency": ""
  },
  "capabilities": {
    "msi": "",
    "pm": "",
    "vga": "",
    "bus_master": "",
    "cap_list": "",
    "rom": ""
  }
}
```

## Interactions

### Full Scan

- **Trigger:** `lshw` — collected as child of `Pci`
- **Behavior:** Queries `Win32_VideoController`. All video controllers are returned. All share `id = "display"` when returned standalone.

### Single Class Query

- **Trigger:** `lshw --class-hw video`
- **On WMI failure:** Exits with error code `13`.

## Business Rules

- All capability and configuration fields are empty placeholder strings.
- `DeviceID` is fetched from WMI but not mapped.
- If a system has multiple GPUs, all are returned in the list (e.g., integrated Intel + discrete NVIDIA).

## Relationships

- **Parent:** `Pci`
- **No children.**
