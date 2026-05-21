# Component Relationships

Visual map of the hardware device tree, dependency graph between classes, and data coupling rules.

---

## Device Tree (Full Scan)

When `lshw` is invoked without `--class-hw`, the tool builds a complete recursive tree rooted at `ComputerSystem`:

```
ComputerSystem  [system]
└── BaseBoard  [baseboard]
    ├── Firmware  [bios]
    ├── Processor  [processor]  (one entry per physical socket)
    ├── PhysicalMemory  [memory]  (container "memory:0")
    │   └── bank:0 … bank:N  (one per DIMM)
    └── Pci  [pci]  (container "pci")
        ├── pci:0 … pci:N  (one bridge per Win32_Bus entry)
        │   ├── Ide  [ide]  (ide:0, ide:1 … primary controllers)
        │   │   ├── channel:0 … channel:N  (secondary controllers)
        │   │   │   ├── PhysicalDisk  [disk]  (one per physical drive)
        │   │   │   │   └── PartitionDisk  [partition]  (one per partition)
        │   │   │   │       └── LogicalDisk  [volume]  (one per drive letter)
        │   │   │   └── CdRom  [cdrom]  (one per optical drive)
        │   ├── GraphicCard  [video]  (one per GPU)
        │   ├── SoundDevice  [sound]  (one per audio device)
        │   └── NetworkCard  [network]  (one per physical NIC)
        ├── usb:0 … usb:N  (one per USB host controller — appended last)
        │   └── UsbDevice  [usbdevices]  (filtered, one per attached device)
```

> **Important:** USB controllers are appended to the **top-level PCI container**, not inside a specific bridge. This is a deliberate special-case in `Pci.format_data()`.

---

## Parent → Child Registration Table

Registration is declared via `@HardwareClass.register(entity, parent=...)` decorators and stored in `HardwareClass._children_`.

| Parent Entity | Registered Children |
|--------------|---------------------|
| `ComputerSystem` | `BaseBoard` |
| `BaseBoard` | `Firmware`, `Processor`, `PhysicalMemory`, `Pci` |
| `Pci` | `Ide`, `GraphicCard`, `SoundDevice`, `NetworkCard`, `Usb` |
| `Ide` | `PhysicalDisk`, `CdRom` |
| `PhysicalDisk` | `PartitionDisk` |
| `PartitionDisk` | `LogicalDisk` |
| `Usb` | `UsbDevice` |
| `Firmware` | *(none)* |
| `Processor` | *(none)* |
| `PhysicalMemory` | *(none — banks are internal, not registered children)* |
| `GraphicCard` | *(none)* |
| `SoundDevice` | *(none)* |
| `NetworkCard` | *(none)* |
| `CdRom` | *(none)* |
| `LogicalDisk` | *(none)* |
| `UsbDevice` | *(none)* |

---

## `--class-hw` CLI Class → Factory Entity Mapping

The `--class-hw` argument uses user-facing class names that map to internal factory keys:

| CLI Class | Factory Entity | Error Exit Code |
|-----------|---------------|----------------|
| `system` | `ComputerSystem` | `1` |
| `baseboard` | `BaseBoard` | `2` |
| `bios` | `Firmware` | `2` |
| `processor` | `Processor` | `3` |
| `memory` | `PhysicalMemory` | `4` |
| `pci` | `Pci` | `5` |
| `ide` | `Ide` | `6` |
| `disk` | `PhysicalDisk` | `7` |
| `partition` | `PartitionDisk` | `8` |
| `volume` | `LogicalDisk` | `9` |
| `usb` | `Usb` | `10` |
| `usbdevices` | `UsbDevice` | `11` |
| `cdrom` | `CdRom` | `12` |
| `video` | `GraphicCard` | `13` |
| `network` | `NetworkCard` | `14` |
| `sound` | `SoundDevice` | `15` |

---

## Cross-Class Data Coupling

Some classes are instantiated *by other classes* with a specific `dev_id` argument to filter results. This is the parent-driven query pattern:

| Instantiating Class | Instantiated Class | Filter Applied |
|--------------------|--------------------|---------------|
| `Ide._attach_ide_child()` | `PhysicalDisk(pnp_id)` | `PNPDeviceID LIKE "%{pnp_id}%"` |
| `Ide._attach_ide_child()` | `CdRom(pnp_id)` | `PNPDeviceID LIKE "%{pnp_id}%"` |
| `PhysicalDisk._fetch_children()` | `PartitionDisk(deviceid)` | Association via `Win32_DiskDriveToDiskPartition` |
| `PartitionDisk._fetch_children()` | `LogicalDisk(deviceid)` | Association via `Win32_LogicalDiskToPartition` |
| `Usb._fetch_children()` | `UsbDevice(dev_id=[pnpdeviceid])` | Filtered by controller PNP ID |

---

## Singleton & Shared State

| Component | Singleton / Shared State |
|-----------|--------------------------|
| `WMIConnection` | **Singleton** — one `wmi.WMI()` connection shared across all class instances in a single `lshw` invocation |
| `HardwareClass._entities_` | **Global dict** — populated at import time by `@register` decorators; shared across all instances |
| `HardwareClass._children_` | **Global dict** — parent-child registry; populated at import time |
| `Ide._cached_disk_pnp_ids` | **Instance-level cache** — pre-fetched disk PNP IDs for fast is-disk classification |

---

## Import & Auto-Discovery

The `lshw/classes/__init__.py` module uses `pkgutil.iter_modules()` to automatically import all Python modules in the `classes/` package (except `hardware_class.py` itself). This import triggers each module's `@HardwareClass.register()` decorator, populating the global registry.

**Consequence:** Adding a new hardware class requires only:
1. Creating a new `.py` file in `lshw/classes/`
2. Defining the class with `@HardwareClass.register('ClassName', parent='ParentName')`

No manual registration in `__init__.py` or `__main__.py` is needed. The CLI's `AVAILABLE_CLASSES` dict in `__main__.py` must also be updated to expose the new class via `--class-hw`.
