# Physical Memory (RAM)

> **CLI class:** `memory`
> **WMI source:** `Win32_PhysicalMemory` (primary) / `Win32_ComputerSystem.TotalPhysicalMemory` (fallback)
> **Hardware class:** `PhysicalMemory`
> **Tree position:** Child of `BaseBoard` — leaf node (no sub-children)
> **Generated:** 2026-05-20

## Overview

Represents the installed RAM. Unlike most hardware classes that return a flat list, `PhysicalMemory` returns a **container node** (`memory:0`) whose `children` array holds one entry per physical memory bank/DIMM slot. This mirrors how Linux `lshw` presents memory: a top-level memory controller with individual banks as children.

If WMI cannot enumerate individual banks (e.g., virtualized environment), a fallback reads total memory from `Win32_ComputerSystem.TotalPhysicalMemory` and creates a synthetic single bank labeled `"System Board"`.

## Fields — Container Node (`memory:0`)

| Field | Value | Notes |
|-------|-------|-------|
| `id` | `"memory:0"` | Fixed — top-level memory container |
| `class` | `"memory"` | Fixed |
| `claimed` | `true` | Always |
| `description` | `"System Memory"` | Fixed string |

## Fields — Bank Child Nodes

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Tag` | `id` + `description` | Bank identifier (e.g. `"Physical Memory 0"` → id `"bank:0"`) |
| `DeviceLocator` | `slot` | Physical slot label on the board (e.g. `"ChannelA-DIMM0"`) |
| `MemoryType` | `product` | Memory type code integer (see Enum Dictionary) |
| `Capacity` | `size` | Bank capacity in **bytes** |
| `DataWidth` | `width` | Data bus width in bits |
| `Speed` | `clock` | Memory speed in MHz |

Fixed per bank:

- `class`: `"memory"`
- `claimed`: `true`
- `units`: `"bytes"`

## Output Schema

```json
{
  "id": "memory:0",
  "class": "memory",
  "claimed": true,
  "description": "System Memory",
  "children": [
    {
      "id": "bank:0",
      "class": "memory",
      "claimed": true,
      "description": "Physical Memory 0",
      "product": 24,
      "slot": "ChannelA-DIMM0",
      "units": "bytes",
      "size": 8589934592,
      "width": 64,
      "clock": 2666
    }
  ]
}
```

## Interactions

### Full Scan / Single Class Query

- **Trigger:** `lshw` or `lshw --class-hw memory`
- **Primary path:** Queries `Win32_PhysicalMemory` for all installed DIMMs. Each DIMM becomes a child of `memory:0`.
- **Fallback path:** If no DIMMs are returned (e.g., virtual machine with no DIMM-level data), queries `Win32_ComputerSystem.TotalPhysicalMemory` and creates a single synthetic bank:
  - `id`: `"bank:0"`, `slot`: `"System Board"`, `width`: `64`, `clock`: `0`
- **On WMI failure:** Exits with error code `4`.

## Business Rules

- The bank `id` is derived from the last character of the `Tag` field: `"Physical Memory 0"` → `"bank:0"`. If `Tag` is missing, id defaults to `"Error getting data"`.
- `MemoryType` is a WMI integer code (e.g., `24` = DDR4). The raw integer is stored in `product` without string conversion. See [→ Enum Dictionary: MemoryType](../appendix/enum-dictionary.md#memorytype).
- `Capacity` is in bytes (raw WMI value, no unit conversion).
- `Speed` is in MHz (raw WMI value); `units` is `"bytes"` on the bank for the size field only — `clock` has no unit label.

## Relationships

- **Parent:** `BaseBoard`
- **No sub-children** (bank nodes have no further descendants).
