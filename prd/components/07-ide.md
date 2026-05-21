# IDE Controller

> **CLI class:** `ide`
> **WMI sources:** `Win32_IDEController`, `Win32_IDEControllerDevice`, `Win32_PNPEntity`, `Win32_DiskDrive`
> **Hardware class:** `Ide`
> **Tree position:** Child of `Pci` — parent of `PhysicalDisk`, `CdRom`
> **Generated:** 2026-05-20

## Overview

Represents the storage controller subsystem (despite the name, it handles modern SATA/AHCI and NVMe controllers too, as WMI reports all under `Win32_IDEController`). The class builds a two-level controller tree: **primary controllers** at the top, with **secondary/channel controllers** as their children.

Devices (physical disks or CD-ROMs) are discovered through the `Win32_IDEControllerDevice` association table and attached to the appropriate controller level.

## Fields Collected

For each controller:

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Caption` | `product` | Controller model string |
| `Description` | `description` | Controller description |
| `Manufacturer` | `vendor` | Controller vendor |
| `PNPDeviceID` | `pnpdeviceid` | PnP device identifier (used for association lookup) |

## ID Scheme

| Level | ID Format | Example |
|-------|-----------|---------|
| Primary controller | `ide:N` (N = 0-indexed) | `"ide:0"` |
| Secondary / channel | `channel:X` (X = last digit of `PNPDeviceID`) | `"channel:1"` |

## Discovery Algorithm

1. Query all associations from `Win32_IDEControllerDevice` to extract `Antecedent → Dependent` pairs.
2. Collect unique **primary** controller PNP IDs (those starting with `PCI\`).
3. For each primary controller, query `Win32_IDEController` by `PNPDeviceID`.
4. For each primary, find associated secondary controllers from the association set and query them similarly.
5. Secondary controllers become children of their primary.
6. When `children=True`, walk all associations again and call `_attach_ide_child()` for each matching pair.

## Child Attachment Logic (`_attach_ide_child`)

For each device in `Win32_IDEControllerDevice`:
1. Query the device via `Win32_PNPEntity` using its `PNPDeviceID`.
2. Check if the device PNP ID appears in the pre-cached set of disk PNP IDs (from `Win32_DiskDrive`).
3. If it **is** a disk → instantiate `PhysicalDisk(PNPDeviceID)` → attach as child.
4. If it is **not** a disk → instantiate `CdRom(PNPDeviceID)` → attach as child.
5. Errors during attachment are logged at `WARNING` and skipped.

## Output Schema

```json
[
  {
    "id": "ide:0",
    "class": "",
    "claimed": true,
    "description": "Standard SATA AHCI Controller",
    "product": "Standard SATA AHCI Controller",
    "vendor": "Standard",
    "pnpdeviceid": "PCI\\VEN_8086&DEV_A382&...",
    "children": [
      {
        "id": "channel:0",
        "class": "",
        "claimed": true,
        "description": "ATA Channel 0",
        "children": [
          { ... PhysicalDisk ... }
        ]
      }
    ]
  }
]
```

## Interactions

### Full Scan

- **Trigger:** `lshw` — collected as child of `Pci`
- **Disk PNP cache:** Before querying controllers, the class pre-fetches all `PNPDeviceID` values from `Win32_DiskDrive` into a set (`_cached_disk_pnp_ids`) for O(1) device-type classification later.
- **On critical WMI failure:** Returns an empty list `[]` instead of raising, so the parent PCI scan can continue.
- **On WMI failure:** Exits with error code `6` when invoked via `--class-hw ide`.

### Single Class Query

- **Trigger:** `lshw --class-hw ide`
- **Behavior:** Returns controller hierarchy without attaching disk/CD children.

## Business Rules

- `class` for controller nodes is always an **empty string** `""` — intentional; the Linux `lshw` convention for storage controllers uses no class label here.
- The disk vs. CD-ROM classification is first attempted via the pre-cached set (fast path), then falls back to a live `Win32_DiskDrive` WQL query (slow path) if the cached check is ambiguous.
- All PNP ID comparisons are case-insensitive and strip backslash characters for normalization.
- If `format_data()` encounters any exception, it returns `[]` rather than propagating the error.

## Relationships

- **Parent:** `Pci`
- **Children:** `PhysicalDisk`, `CdRom`
