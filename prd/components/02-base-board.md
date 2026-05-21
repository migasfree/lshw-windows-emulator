# Base Board (Motherboard)

> **CLI class:** `baseboard`
> **WMI source:** `Win32_BaseBoard`
> **Hardware class:** `BaseBoard`
> **Tree position:** Child of `ComputerSystem` — parent of `Firmware`, `Processor`, `PhysicalMemory`, `Pci`
> **Generated:** 2026-05-20

## Overview

Represents the physical motherboard. Provides the board product name, manufacturer, and serial number. In the device tree it acts as the aggregation point for all on-board subsystems: BIOS firmware, CPUs, RAM banks, and PCI buses.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Product` | `product` | Board model name (e.g. `"0KP561"`) |
| `Manufacturer` | `vendor` | Board manufacturer (e.g. `"Dell Inc."`) |
| `SerialNumber` | `serial` | Motherboard serial number |

## Fixed Fields

| Field | Value | Notes |
|-------|-------|-------|
| `id` | `"core"` | Always fixed — represents the core bus |
| `class` | `"bus"` | Fixed hardware class label |
| `claimed` | `true` | Always claimed |
| `description` | `"Motherboard"` | Fixed string |
| `physid` | `"0"` | Fixed physical ID |

## Output Schema

```json
{
  "id": "core",
  "class": "bus",
  "claimed": true,
  "handle": "",
  "description": "Motherboard",
  "product": "0KP561",
  "vendor": "Dell Inc.",
  "physid": "0",
  "serial": "..CNXXXXXXXXXXXXXXXX.",
  "children": [ ... ]
}
```

## Interactions

### Full Scan

- **Trigger:** `lshw` (no arguments) — collected as child of `ComputerSystem`
- **Behavior:** Queries `Win32_BaseBoard` for the three properties above. Then recursively fetches children: `Firmware`, `Processor`, `PhysicalMemory`, and `Pci`.

### Single Class Query

- **Trigger:** `lshw --class-hw baseboard`
- **Behavior:** Returns board data only; no children fetched.
- **On WMI failure:** Exits with error code `2`.

## Relationships

- **Parent:** `ComputerSystem`
- **Children registered:** `Firmware`, `Processor`, `PhysicalMemory`, `Pci`
