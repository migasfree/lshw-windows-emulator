# Logical Disk (Volume)

> **CLI class:** `volume`
> **WMI sources:** `Win32_LogicalDisk`, `Win32_LogicalDiskToPartition`
> **Hardware class:** `LogicalDisk`
> **Tree position:** Child of `PartitionDisk` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents a mounted logical volume (Windows drive letter: `C:`, `D:`, etc.). It is the deepest level of the storage hierarchy. When used in a full scan, only volumes associated with the parent partition are returned (via `Win32_LogicalDiskToPartition`). When queried standalone, all logical disks on the system are returned.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `DeviceID` | `deviceid` + `id` | Drive letter (e.g. `"C:"`); id is computed as `"logicalvolume:N"` where N = alphabetical index of the drive letter |
| `VolumeName` | `logicalname` | Volume label (user-defined name) |
| `FileSystem` | `configuration.mount.fstype` | Filesystem type (e.g. `"NTFS"`, `"FAT32"`) |
| `Size` | `capacity` | Total volume size in bytes |
| `FreeSpace` | *(not captured)* | Available but not mapped to a field [TBC — future enhancement] |
| `Description` | `description` | WMI description enriched with Name, VolumeName, and FileSystem |
| `Name` | embedded in `description` | Drive letter path |
| `DriveType` | *(not captured)* | Raw drive type integer; not currently mapped [TBC] |
| `MediaType` | *(not captured)* | Media type integer; not currently mapped [TBC] |

## ID Computation

The `id` field uses an alphabetical index of the drive letter:

```txt
A: → logicalvolume:0
B: → logicalvolume:1
C: → logicalvolume:2
D: → logicalvolume:3
...
```

If the first character of `DeviceID` is not an ASCII letter, `id` defaults to `"Error getting data"`.

## Description Format

The `description` field is a composite string:

```txt
{WMI_Description}. Volume name: [{Name}]. Label: {VolumeName}. Filesystem: {FileSystem}
```

Example: `"Local Fixed Disk. Volume name: [C:]. Label: Windows. Filesystem: NTFS"`

## Fixed Fields

| Field | Value |
|-------|-------|
| `class` | `"volume"` |
| `claimed` | `true` |
| `product` | `""` |
| `vendor` | `""` |
| `configuration.state` | `"mounted"` |

## Output Schema

```json
{
  "id": "logicalvolume:2",
  "class": "volume",
  "claimed": true,
  "description": "Local Fixed Disk. Volume name: [C:]. Label: Windows. Filesystem: NTFS",
  "deviceid": "C:",
  "logicalname": "Windows",
  "capacity": 499958865920,
  "configuration": {
    "mount.fstype": "NTFS",
    "mount.options": "",
    "state": "mounted"
  }
}
```

## Interactions

### As Child of PartitionDisk

- **Primary lookup:** Iterates `Win32_LogicalDiskToPartition` associations. For each association where `Antecedent` matches the parent partition's `DeviceID`, extracts the logical disk `DeviceID` from `Dependent` and queries `Win32_LogicalDisk WHERE DeviceID="{ld_id}"`.
- **Fallback:** Uses `element.associators('Win32_LogicalDiskToPartition', wmi_result_class='Win32_LogicalDisk')` on older WMI implementations.

### As Standalone Query

- **Trigger:** `lshw --class-hw volume`
- **Behavior:** Queries all `Win32_LogicalDisk` records without partition filtering.
- **On WMI failure:** Exits with error code `9`.

## Business Rules

- `FreeSpace` and `DriveType` and `MediaType` are fetched from WMI (included in `properties_to_get`) but are **not mapped** to any `Hardware` field. They are available in the raw WMI result but discarded.
- If a drive letter cannot be indexed (e.g., a UNC path volume), the `id` defaults to `"Error getting data"`.
- `capacity` stores `Size` (total volume size). There is no field for free space in the current data model.

## Relationships

- **Parent:** `PartitionDisk`
- **No children.**
