# PCI Bus

> **CLI class:** `pci`
> **WMI source:** `Win32_Bus`
> **Hardware class:** `Pci`
> **Tree position:** Child of `BaseBoard` — parent of `Ide`, `GraphicCard`, `SoundDevice`, `NetworkCard`, `Usb`
> **Generated:** 2026-05-20

## Overview

Represents the PCI bus subsystem. Unlike other classes that return a flat list, `Pci` returns a **single top-level container** (`id: "pci"`, `class: "bridge"`) whose `children` array holds individual PCI bridge records — one per bus entry reported by `Win32_Bus`.

USB controllers, discovered separately, are appended at the end of the children list to avoid duplication across bridges.

## Fields Collected

| WMI Property | Hardware Field | Notes |
|---|---|---|
| `DeviceID` | `id` / `description` | Device ID parsed for bus prefix (`isa`, `pci`, `pnp`); suffix digit forms the id (e.g. `"pci:0"`) |
| `Caption` | `product` | Bus caption string |

## Fixed Fields — Container Node

| Field | Value |
|-------|-------|
| `id` | `"pci"` |
| `class` | `"bridge"` |
| `claimed` | `true` |
| `description` | `"Host bridge"` |

## Fixed Fields — Bridge Child Nodes

| Field | Value |
|-------|-------|
| `class` | `"bridge"` |
| `claimed` | `true` |

## ID Parsing Logic

`DeviceID` strings from `Win32_Bus` have a prefix (`ISA\`, `PCI\`, `PnpBus\`). The tool:

1. Takes the first 3 characters of `DeviceID`, lowercases them.
2. If the prefix is `isa`, `pci`, or `pnp`, forms id: `{prefix}:{last_char_of_DeviceID}`.
3. Otherwise leaves `id` empty.

## Output Schema

```json
{
  "id": "pci",
  "class": "bridge",
  "claimed": true,
  "description": "Host bridge",
  "children": [
    {
      "id": "pci:0",
      "class": "bridge",
      "claimed": true,
      "description": "PCI\\PCI_Bus_0",
      "product": "PCI bus",
      "children": [
        { ... GraphicCard ... },
        { ... SoundDevice ... },
        { ... NetworkCard ... }
      ]
    },
    { "id": "usb:0", ... },
    { "id": "usb:1", ... }
  ]
}
```

## Interactions

### Full Scan

- **Trigger:** `lshw` — collected as child of `BaseBoard` with `children=True`
- **Behavior:**
  1. Queries `Win32_Bus` — creates a bridge child per result.
  2. Iterates registered children (`Ide`, `GraphicCard`, `SoundDevice`, `NetworkCard`): each child's results are appended to the **first** bridge's `children`.
  3. `Usb` is handled specially: fetched once regardless of bridge count, USB controllers are appended to the top-level container (not to a bridge), numbered `usb:0`, `usb:1`, etc.
- **USB deduplication:** The `usb_fetched` flag prevents fetching USB controllers more than once when multiple PCI bridges exist.

### Single Class Query

- **Trigger:** `lshw --class-hw pci`
- **Behavior:** Returns the PCI container with bridge children but **without** device children (Ide, GPU, NIC, etc.).
- **On WMI failure:** Exits with error code `5`.

## Business Rules

- If `Win32_Bus` returns no results, the container is returned with an empty `children` list.
- Child classes `Ide`, `GraphicCard`, `SoundDevice`, `NetworkCard` are each instantiated fresh during the children fetch; their results are appended to the **same** first bridge object.
- USB controllers (class `Usb`) are uniquely fetched once and appended directly to the top-level PCI container, not inside a bridge.

## Relationships

- **Parent:** `BaseBoard`
- **Children registered:** `Ide`, `GraphicCard`, `SoundDevice`, `NetworkCard`, `Usb`
