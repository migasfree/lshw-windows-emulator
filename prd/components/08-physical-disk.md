# Physical Disk

> **CLI class:** `disk`
> **WMI source:** `Win32_DiskDrive`
> **Hardware class:** `PhysicalDisk`
> **Tree position:** Child of `Ide` — parent of `PartitionDisk`
> **Generated:** 2026-05-20

## Overview

Represents a physical storage device (HDD, SSD, NVMe). When attached as a child of the IDE controller during a full scan, only disks associated with a specific controller PNP ID are fetched. When queried standalone, all physical disks are returned.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Description` | `description` | Drive description (e.g. `"Disk drive"`) |
| `Caption` | `product` | Drive model name (e.g. `"Samsung SSD 870 EVO 1TB"`) |
| `Manufacturer` | `vendor` | Drive manufacturer |
| `DeviceID` | `deviceid` | WMI device path (e.g. `"\\.\PHYSICALDRIVE0"`) |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier (used for partition association) |
| `Index` | `businfo` | Disk index; formatted as `"scsi@N:0.0.0"` |
| `Size` | `size` | Total disk size in **bytes** (integer) |

## Fixed Fields

| Field | Value | Notes |
|-------|-------|-------|
| `id` | `"disk"` | Fixed — all physical disks share this id when standalone |
| `class` | `"disk"` | Fixed |
| `claimed` | `true` | Always |
| `units` | `"bytes"` | For the `size` field |
| `configuration` | `{ansiversion: "", signature: ""}` | Placeholders |
| `capabilities` | `{partitioned: "", "partitioned:dos": ""}` | Placeholders |

## Output Schema

```json
{
  "id": "disk",
  "class": "disk",
  "claimed": true,
  "description": "Disk drive",
  "product": "Samsung SSD 870 EVO 1TB",
  "vendor": "(Standard disk drives)",
  "deviceid": "\\\\.\\PHYSICALDRIVE0",
  "pnpdeviceid": "SCSI\\DISK&VEN_SAMSUNG&...",
  "businfo": "scsi@0:0.0.0",
  "units": "bytes",
  "size": 1000204886016,
  "configuration": {
    "ansiversion": "",
    "signature": ""
  },
  "capabilities": {
    "partitioned": "",
    "partitioned:dos": ""
  },
  "children": [ ... PartitionDisk ... ]
}
```

## Interactions

### As Child of IDE (Full Scan)

- **Trigger:** `lshw` via `_attach_ide_child()`
- **Instantiation:** `PhysicalDisk(pnp_device_id)` where `pnp_device_id` is taken from the IDE association. Queries `Win32_DiskDrive WHERE PNPDeviceID LIKE "%{dev_id}%"`.

### As Standalone Query

- **Trigger:** `lshw --class-hw disk`
- **Instantiation:** `PhysicalDisk()` (no dev_id). Queries all `Win32_DiskDrive` records.

### Children Fetch

- **Trigger:** Full scan or `--class-hw disk` when `children=True` internally
- **Behavior:** `_fetch_children()` instantiates `PartitionDisk(deviceid)` for each disk. Partitions of each disk become that disk's `children`.
- **On failure:** Logs `WARNING`, disk children remain empty.

### Error Handling

- `Size` parsing: tries `int(hw_item['Size'])`. On `ValueError`/`TypeError`/`KeyError`, logs `WARNING` and sets `size = 0`.
- On WMI failure via `--class-hw`: exits with error code `7`.

## Business Rules

- `businfo` is always formatted as `"scsi@{Index}:0.0.0"` regardless of the actual interface type (SATA, NVMe, USB).
- `serial` is always empty (`""`) — `Win32_DiskDrive` does report `SerialNumber`, but the current implementation does not capture it.
- The `logicalname` and `dev` fields are initialized to empty strings and never populated from WMI.

## Relationships

- **Parent:** `Ide` (in full scan) or standalone
- **Children:** `PartitionDisk`
