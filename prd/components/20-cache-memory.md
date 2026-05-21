# Cache Memory

> **CLI class:** `memory`
> **WMI source:** `Win32_CacheMemory`
> **Hardware class:** `CacheMemory`
> **Tree position:** Nested child under `Processor`
> **Generated:** 2026-05-21

## Overview

Reports internal processor cache memory modules (L1, L2, L3 cache). Instead of listing them flat under the motherboard, it nests them underneath their respective `Processor` socket to represent physical layout parity.

## Fields Collected

### From `Win32_CacheMemory`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `DeviceID` | `id` | Cache identifier, sequence parsed as `"cache:N"` |
| `Description` | `description` | Cache level descriptor (e.g. `"L1 Cache"`, `"L2 Cache"`, `"L3 Cache"`) |
| `MaxCacheSize` | `size` | Size of the cache module in bytes |
| `Level` | `configuration.level` | Cache hierarchy tier (e.g., `1`, `2`, `3`) |

## Output Schema

```json
{
  "id": "cache:0",
  "class": "memory",
  "claimed": true,
  "handle": "",
  "description": "L2 Cache",
  "size": 524288,
  "configuration": {
    "level": 2
  }
}
```

## Interactions

### Full Scan (default invocation)

- **Trigger:** `lshw` — nested under individual CPU/`Processor` nodes
- **Behavior:** Queries cache segments via WMI and dynamically attaches them to the matching CPU socket.

### Single Class Query

- **Trigger:** `lshw --class-hw memory`
- **Behavior:** Included as part of the broader memory classification queries.

## Business Rules

- Memory size is converted from kilobytes (returned by WMI `MaxCacheSize`) to bytes by multiplying by `1024` for parity with Linux sizing definitions.
- Hierarchy levels (`Level` property from WMI) are resolved into normalized integer attributes.

## Relationships

- **Parent:** `Processor`
- **Children:** None
