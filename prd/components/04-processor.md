# Processor (CPU)

> **CLI class:** `processor`
> **WMI source:** `Win32_Processor`
> **Hardware class:** `Processor`
> **Tree position:** Child of `BaseBoard` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents one physical processor socket. If the system has multiple physical CPUs, one record is returned per socket, numbered sequentially (`cpu:0`, `cpu:1`, …). Reports the CPU name, vendor, socket identifier, data bus width, and maximum clock speed.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Manufacturer` | `vendor` | CPU vendor (e.g. `"GenuineIntel"`, `"AuthenticAMD"`) |
| `Name` | `product` | Full processor name string (e.g. `"Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz"`) |
| `Description` | `description` | Processor family description from WMI |
| `SocketDesignation` | `slot` | Physical socket label (e.g. `"U3E1"`, `"CPU 0"`) |
| `DataWidth` | `width` | Data bus width in bits (e.g. `64`) |
| `MaxClockSpeed` | `clock` | Maximum clock speed in MHz |

## Fixed / Computed Fields

| Field | Value | Notes |
|-------|-------|-------|
| `id` | `"cpu:N"` | N is a zero-indexed counter incremented per processor found |
| `class` | `"processor"` | Fixed hardware class label |
| `claimed` | `true` | Always |
| `businfo` | `"cpu@"` | Fixed bus info prefix |
| `units` | `"Hz"` | Frequency unit |
| `serial` | `""` | Always empty (WMI does not expose CPU serial) |
| `physid` | `""` | Empty |

## Output Schema

```json
{
  "id": "cpu:0",
  "class": "processor",
  "claimed": true,
  "description": "Central Processor",
  "product": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
  "vendor": "GenuineIntel",
  "slot": "U3E1",
  "businfo": "cpu@",
  "units": "Hz",
  "width": 64,
  "clock": 2904
}
```

## Interactions

### Full Scan / Single Class Query

- **Trigger:** `lshw` or `lshw --class-hw processor`
- **Behavior:** Queries `Win32_Processor`. Returns one `Hardware` record per socket, with `id` incrementing from `cpu:0`.
- **Multiple CPUs:** Counter `_cpu_id` persists across `_populate_hardware()` calls within a single invocation. Each socket gets a unique sequential ID.
- **On WMI failure:** Exits with error code `3`.

## Business Rules

- `clock` value from WMI is in **MHz**; the `units` field is set to `"Hz"` for lshw compatibility but the raw integer value is MHz. Consumers of the JSON output should be aware of this labeling discrepancy.
- `size` is always `0` for this class (lshw Linux convention reserves it for current frequency; WMI does not provide this).
- `version` is always an empty string.

## Relationships

- **Parent:** `BaseBoard`
- **No children.**
