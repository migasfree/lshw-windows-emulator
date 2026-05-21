# WMI Query Reference

Complete reference of all WMI queries executed by the LsHw Windows Emulator, organized by hardware class.

---

## Query Patterns

The system uses two query patterns:

| Pattern | Method | Used By |
|---------|--------|---------|
| **Method call** | `wmi_system.Win32_Entity([field_list])` | Most classes via `wmi_method` + `get_hardware()` |
| **WQL query** | `wmi_system.query("SELECT ... FROM ... WHERE ...")` | Classes with filters (Disk, Partition, Network, etc.) |

All WQL queries are built via `build_wql_select(table, where_clause)` which validates the entity against the allowlist before constructing the string.

---

## Queries by Class

### ComputerSystem

| # | Pattern | Query / Call | Fields |
|---|---------|-------------|--------|
| 1 | Method | `Win32_ComputerSystem(['Model','Name','Description','Manufacturer','NumberOfProcessors'])` | Main system info |
| 2 | Method | `Win32_SystemEnclosure(['ChassisTypes'])` | Chassis type |
| 3 | Method | `Win32_Computersystemproduct(['UUID','IdentifyingNumber'])` | UUID and serial |

---

### BaseBoard

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_BaseBoard(['Model','SerialNumber','Manufacturer','Product'])` |

---

### Firmware

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_Bios(['Manufacturer','BIOSVersion','ReleaseDate','SerialNumber'])` |

---

### Processor

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_Processor(['Manufacturer','Name','Description','SocketDesignation','DataWidth','MaxClockSpeed'])` |

---

### PhysicalMemory

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | Method | `Win32_PhysicalMemory(['Tag','DeviceLocator','Capacity','Speed','MemoryType','DataWidth'])` | Primary path |
| 2 | Method | `Win32_ComputerSystem(['TotalPhysicalMemory'])` | Fallback only (if no DIMMs found) |

---

### Pci

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_Bus(['Caption','Description','DeviceID'])` |

---

### Ide

| # | Pattern | Query / Call | Purpose |
|---|---------|-------------|---------|
| 1 | Method | `Win32_DiskDrive(['PNPDeviceID'])` | Pre-cache disk PNP IDs |
| 2 | Method | `Win32_IDEControllerDevice(['Antecedent','Dependent'])` | Association mapping |
| 3 | WQL | `SELECT Manufacturer,Caption,Description,DeviceID,PNPDeviceID FROM Win32_IDEController WHERE PNPDeviceID="{id}"` | Primary controllers |
| 4 | WQL | `SELECT Manufacturer,Caption,Description,DeviceID,PNPDeviceID FROM Win32_IDEController WHERE PNPDeviceID="{id}"` | Secondary/channel controllers |
| 5 | Method | `Win32_IDEControllerDevice(['Antecedent','Dependent'])` | Re-queried for child attachment |
| 6 | WQL | `SELECT {fields} FROM Win32_PNPEntity WHERE PNPDeviceID="{id}"` | Attached device identification |
| 7 | WQL | `SELECT PNPDeviceID FROM Win32_DiskDrive WHERE PNPDeviceID="{id}"` | Disk vs. CD-ROM classification (fallback) |

---

### PhysicalDisk

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | Method | `Win32_DiskDrive(['Caption','Description','DeviceID','Index','Manufacturer','PNPDeviceID','Size'])` | Standalone (no `dev_id`) |
| 2 | WQL | `SELECT {fields} FROM Win32_DiskDrive WHERE PNPDeviceID LIKE "%{dev_id}%"` | Filtered by PNP ID (from IDE) |

---

### PartitionDisk

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | Method | `Win32_DiskPartition(['Bootable','BootPartition','DeviceID','PNPDeviceID','Index','Type','Size','Description','PrimaryPartition'])` | Standalone (no `dev_id`) |
| 2 | Method | `Win32_DiskDriveToDiskPartition()` | Association walk (primary path, with `dev_id`) |
| 3 | WQL | `SELECT {fields} FROM Win32_DiskPartition WHERE DeviceID="{part_id}"` | Per-partition query (primary path) |
| 4 | WQL | `SELECT DeviceID FROM Win32_DiskDrive WHERE DeviceID="{dev_id}"` | Fallback: find disk by ID |
| 5 | OOP | `element.associators('Win32_DiskDriveToDiskPartition')` | Fallback: associators method |

---

### LogicalDisk

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | Method | `Win32_LogicalDisk(['Caption','Name','ProviderName','Description','FileSystem','MediaType','VolumeName','Size','FreeSpace','DeviceID','DriveType'])` | Standalone (no `dev_id`) |
| 2 | Method | `Win32_LogicalDiskToPartition()` | Association walk (primary path, with `dev_id`) |
| 3 | WQL | `SELECT {fields} FROM Win32_LogicalDisk WHERE DeviceID="{ld_id}"` | Per-volume query (primary path) |
| 4 | WQL | `SELECT DeviceID FROM Win32_DiskPartition WHERE DeviceID="{dev_id}"` | Fallback: find partition |
| 5 | OOP | `element.associators('Win32_LogicalDiskToPartition', wmi_result_class='Win32_LogicalDisk')` | Fallback: associators method |

---

### Usb

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_USBController(['PNPDeviceID','DeviceID','Description','Manufacturer'])` |

---

### UsbDevice

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | Method | `Win32_USBControllerDevice(['Antecedent','Dependent'])` | Association mapping |
| 2 | WQL | `SELECT {fields} FROM Win32_PNPEntity WHERE PNPDeviceID="{dep_id}"` | Per-device query |

---

### CdRom

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | Method | `Win32_CDROMDrive(['DeviceID','PNPDeviceID','Manufacturer','Name','Caption','MediaType','SCSIBus','SCSILogicalUnit','SCSIPort','Description','MediaLoaded','Drive'])` | Standalone (no `dev_id`) |
| 2 | WQL | `SELECT {fields} FROM Win32_CDROMDrive WHERE PNPDeviceID LIKE "%{dev_id}%"` | Filtered by PNP ID (from IDE) |

---

### GraphicCard

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_VideoController(['AdapterCompatibility','Description','DeviceID','PNPDeviceID','VideoProcessor'])` |

---

### NetworkCard

| # | Pattern | Query / Call | Condition |
|---|---------|-------------|-----------|
| 1 | WQL | `SELECT {fields} FROM Win32_NetworkAdapter WHERE (NOT PNPDeviceID LIKE "%ROOT%")` | Windows 10 < 10.0.18362 |
| 2 | WQL | `SELECT {fields} FROM Win32_NetworkAdapter WHERE (PhysicalAdapter=True)` | Windows 10 ≥ 10.0.18362 |

Fields queried: `Speed`, `SystemCreationClassName`, `AdapterType`, `Autosense`, `Caption`, `MACAddress`, `ProductName`, `Manufacturer`, `NetConnectionID`, `Description`, `PNPDeviceID`.

### SoundDevice

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_SoundDevice(['PNPDeviceID','DeviceID','Manufacturer'])` |

---

### Power

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | WQL | `SELECT * FROM Win32_Battery` |
| 2 | WQL | `SELECT * FROM Win32_PortableBattery` |
| 3 | WQL | `SELECT * FROM Win32_UninterruptiblePowerSupply` |

---

### Printer

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | WQL | `SELECT * FROM Win32_Printer` |

---

### Communication

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | WQL | `SELECT * FROM Win32_SerialPort` |
| 2 | WQL | `SELECT * FROM Win32_POTSModem` |

---

### CacheMemory

| # | Pattern | Query / Call |
|---|---------|-------------|
| 1 | Method | `Win32_CacheMemory(['DeviceID','Description','MaxCacheSize','Level'])` |

---

## WQL Field Selection & Robust Querying

Most WQL queries use explicit field lists (`SELECT field1, field2 FROM ...`) to minimize data transfer overhead and optimize performance.

However, classes that are subject to hardware driver differences, missing optional properties, or virtualized environments (such as **`Power`**, **`Printer`**, and **`Communication`**) systematically use **`SELECT *`** queries. WMI parses `SELECT *` without throwing OLE errors (like `0x80041017`) when properties are absent on the host drivers, and the framework resolves missing properties in the Python layer via clean `AttributeError` handling. This guarantees 100% crash resilience across all VM, Server, and customized Windows installations.
