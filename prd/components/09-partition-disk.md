# Disk Partition

> **CLI class:** `partition`
> **WMI sources:** `Win32_DiskPartition`, `Win32_DiskDriveToDiskPartition`
> **Hardware class:** `PartitionDisk`
> **Tree position:** Child of `PhysicalDisk` — parent of `LogicalDisk`
> **Generated:** 2026-05-20

## Overview

Represents a partition on a physical disk. When used in a full scan, only partitions belonging to the parent disk are returned (filtered via `Win32_DiskDriveToDiskPartition`). When queried standalone, all partitions across all disks are returned.

The class also derives human-readable capability labels from raw boolean WMI flags (bootable, primary/extended).

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Index` | `id` | Partition index, formatted as `"volume:N"` |
| `Description` | `description` | Partition type label (may be overridden for boot partitions; see Business Rules) |
| `Size` | `size` + `capacity` | Partition size in bytes |
| `DeviceID` | `deviceid` | WMI partition identifier (e.g. `"Disk #0, Partition #0"`) |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier |
| `Bootable` | `capabilities.bootable` | Boolean → `"Bootable partition"` / `"No bootable partition"` |
| `BootPartition` | `capabilities.bootable` (appended) | If true, appends `" (active)"` to the bootable label |
| `PrimaryPartition` | `capabilities.primary` + `capabilities.extended` | Boolean → see Capability Labels below |

## Fixed Fields

| Field | Value |
|-------|-------|
| `class` | `"volume"` |
| `claimed` | `true` |
| `vendor` | `"Windows"` (always) |
| `configuration.filesystem` | `"fat"` (placeholder default) |
| `configuration.mount.fstype` | `"fat"` (placeholder default) |
| `configuration.state` | `"mounted"` |

## Capability Labels

| Condition | `capabilities.primary` | `capabilities.extended` |
|-----------|----------------------|------------------------|
| `PrimaryPartition = True` | `"Primary partition"` | `"No extended partition"` |
| `PrimaryPartition = False` | `"No primary partition"` | `"Extended partition"` |

## Output Schema

```json
{
  "id": "volume:0",
  "class": "volume",
  "claimed": true,
  "description": "Installable File System",
  "vendor": "Windows",
  "deviceid": "Disk #0, Partition #0",
  "pnpdeviceid": "...",
  "size": 536870912000,
  "capacity": 536870912000,
  "configuration": {
    "filesystem": "fat",
    "modified": "",
    "mount.fstype": "fat",
    "mount.options": "",
    "mounted": "",
    "state": "mounted"
  },
  "capabilities": {
    "primary": "Primary partition",
    "extended": "No extended partition",
    "bootable": "Bootable partition (active)",
    "extended_attributes": ""
  },
  "children": [ ... LogicalDisk ... ]
}
```

## Interactions

### As Child of PhysicalDisk

- **Primary lookup:** Iterates `Win32_DiskDriveToDiskPartition` associations. For each association where `Antecedent` matches the parent disk's `DeviceID`, extracts the partition `DeviceID` from `Dependent` and queries `Win32_DiskPartition WHERE DeviceID="..."`.
- **Fallback:** If the association-based lookup fails (e.g., on older WMI implementations), falls back to `element.associators('Win32_DiskDriveToDiskPartition')` OOP method.
- Both `Antecedent` and `Dependent` references may be either WMI object references or raw strings; the `_extract_id()` helper parses both formats via regex.

### As Standalone Query

- **Trigger:** `lshw --class-hw partition`
- **Behavior:** Queries all `Win32_DiskPartition` records without disk filtering.
- **On WMI failure:** Exits with error code `8`.

### Children Fetch

- **Trigger:** Full scan (children=True)
- **Behavior:** `_fetch_children()` instantiates `LogicalDisk(deviceid)` for each partition. Logical volumes of each partition become that partition's children.

## Business Rules

- If `Description` is `"Unknown"` **and** `Bootable=True` **and** `BootPartition=True`, the description is overridden to `"Primary. Bootable. Boot partition. FAT32"`.
- `size` and `capacity` are set to the same raw integer value from `Win32_DiskPartition.Size`.
- `configuration.filesystem` and `mount.fstype` are always `"fat"` by default — they are not derived from the partition data. The actual filesystem type is reported at the `LogicalDisk` level.

## Relationships

- **Parent:** `PhysicalDisk`
- **Children:** `LogicalDisk`
