# Firmware (BIOS)

> **CLI class:** `bios`
> **WMI source:** `Win32_Bios`
> **Hardware class:** `Firmware`
> **Tree position:** Child of `BaseBoard` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents the system firmware (BIOS/UEFI). Collects the firmware manufacturer, version string, release date, and serial number. This is a leaf node — it has no sub-components.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Manufacturer` | `vendor` | Firmware vendor (e.g. `"American Megatrends Inc."`) |
| `BIOSVersion[0]` | `version` | First element of the BIOS version array (e.g. `"DELL - 1072009"`) |
| `ReleaseDate` | `date` | Release date in WMI datetime string format (e.g. `"20210315000000.000000+000"`) |
| `SerialNumber` | `serial` | BIOS serial number |

> **Note:** `BIOSVersion` is a WMI array. Only the first element `[0]` is captured.

## Fixed Fields

| Field | Value | Notes |
|-------|-------|-------|
| `id` | `"firmware"` | Always fixed |
| `class` | `"memory"` | Fixed — BIOS is classified as memory in lshw convention |
| `claimed` | `true` | Always claimed |
| `description` | `"BIOS"` | Fixed string |
| `units` | `""` | Empty for firmware |
| `size` | `0` | Always zero |
| `capacity` | `0` | Always zero |

## Output Schema

```json
{
  "id": "firmware",
  "class": "memory",
  "claimed": true,
  "description": "BIOS",
  "vendor": "American Megatrends Inc.",
  "serial": "..CNXXXXXXXXXXXXXXXX.",
  "version": "DELL - 1072009",
  "date": "20210315000000.000000+000"
}
```

## Interactions

### Full Scan

- **Trigger:** `lshw` — collected as child of `BaseBoard`
- **Behavior:** Queries `Win32_Bios` and populates the four fields above.

### Single Class Query

- **Trigger:** `lshw --class-hw bios`
- **Behavior:** Returns firmware data only.
- **On WMI failure:** Exits with error code `2`.

## Business Rules

- The raw WMI `ReleaseDate` format (`YYYYMMDDHHmmss.ffffff+zzz`) is passed through as-is without conversion to a human-readable date.
- If `BIOSVersion` is empty or not present in the WMI result, `version` will contain `"Error getting data"`.

## Relationships

- **Parent:** `BaseBoard`
- **No children.**
