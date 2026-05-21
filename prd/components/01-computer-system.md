# Computer System

> **CLI class:** `system`
> **WMI source:** `Win32_ComputerSystem` + `Win32_ComputerSystemProduct` + `Win32_SystemEnclosure`
> **Hardware class:** `ComputerSystem`
> **Tree position:** Root — parent of `BaseBoard`
> **Generated:** 2026-05-20

## Overview

Represents the top-level physical machine. Collects the model name, manufacturer, number of processors, chassis type, system UUID, and serial number. This is always the entry point for a full hardware scan.

When the user runs `lshw` with no arguments, the tool starts here and recursively collects all children. When invoked with `--class-hw system`, only this node is returned (no children).

## Fields Collected

### From `Win32_ComputerSystem`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Name` | `id` | Computer hostname / name |
| `Description` | `description` | WMI system description, appended with chassis type |
| `Model` | `product` | Machine model identifier (e.g. `"OptiPlex 7090"`) |
| `Manufacturer` | `vendor` | OEM manufacturer (e.g. `"Dell Inc."`) |
| `NumberOfProcessors` | `configuration.cpus` | Count of physical processor sockets |

### From `Win32_ComputerSystemProduct`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `UUID` | `configuration.uuid` | Universally Unique Identifier for the system |
| `IdentifyingNumber` | `serial` | Manufacturer serial number of the machine |

### From `Win32_SystemEnclosure`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `ChassisTypes[0]` | `configuration.chassis` + `description` | Chassis form factor; see Enum Dictionary |

## Output Schema

```json
{
  "id": "DESKTOP-ABC123",
  "class": "system",
  "claimed": true,
  "handle": "",
  "description": "AT/AT COMPATIBLE, Desktop",
  "product": "OptiPlex 7090",
  "vendor": "Dell Inc.",
  "physid": "0",
  "serial": "5CG1234XYZ",
  "width": 0,
  "configuration": {
    "boot": "",
    "chassis": "Desktop",
    "cpus": 1,
    "family": "",
    "sku": "",
    "uuid": "4C4C4544-0044-xxxx-xxxx-xxxxxxxxxxxx"
  },
  "children": [ ... ]
}
```

## Interactions

### Full Scan (default invocation)

- **Trigger:** `lshw` (no arguments)
- **Behavior:** Instantiates `ComputerSystem`, calls `format_data(children=True)`. Recursively collects all registered child classes via `_fetch_children()`.
- **Output:** Complete device tree printed as indented key-value pairs.

### Single Class Query

- **Trigger:** `lshw --class-hw system`
- **Behavior:** Instantiates `ComputerSystem`, calls `format_data(children=False)`. No child classes are queried.
- **On WMI failure:** Exits with error code `1`, message: `[err #1] there was an error getting "ComputerSystem" information`.

### JSON Output

- **Trigger:** `lshw --json` or `lshw --class-hw system --json`
- **Behavior:** All `Hardware` objects are serialized to dictionaries via `.to_dict()`, then rendered with `json.dumps(indent=2)`.

## Business Rules

- The `description` field combines `Win32_ComputerSystem.Description` and the chassis type string, separated by `, `.
- If `ChassisTypes` is `None` or out of bounds (1–23), the chassis falls back to `"Unknown"`.
- If `UUID` or `IdentifyingNumber` are empty strings from WMI, the fallback is `"Unknown"`.
- The `configuration.boot`, `configuration.family`, and `configuration.sku` fields are always empty strings in the current implementation — they are reserved placeholders for future WMI properties.
- `width` is always `0` for this class.

## Relationships

- **Children:** `BaseBoard` (registered parent=`'ComputerSystem'`)
- **No inbound links** — this is the tree root.

## Chassis Type Enum

See [→ Enum Dictionary: ChassisTypes](../appendix/enum-dictionary.md#chassistypes).
