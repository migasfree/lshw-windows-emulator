# Data Model Reference

Complete specification of the `Hardware` dataclass — the universal output unit of every hardware class in the system.

---

## `Hardware` Dataclass

**Source:** `lshw/classes/hardware.py`

Every hardware component (system, CPU, disk partition, USB device, etc.) is represented as a `Hardware` instance. All 30 fields are defined on the dataclass; fields with falsy values are **omitted** from the JSON serialization (`to_dict()`).

---

## Core Fields (always serialized)

These fields appear in **every** `to_dict()` output regardless of value:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"unknown"` | Unique identifier within the parent's children list (e.g. `"cpu:0"`, `"disk"`, `"core"`) |
| `class_` | `str` | `"unknown"` | Hardware class label. Serialized as `"class"` in JSON output. (e.g. `"processor"`, `"disk"`, `"network"`) |
| `claimed` | `bool` | `False` | Whether the device is claimed by the OS/driver. Always `True` for all current classes. |
| `handle` | `str` | `""` | Hardware handle. Always `""` in current implementation — reserved for future use. |
| `description` | `str` | `""` | Human-readable description of the component. |
| `product` | `str` | `"Error getting data"` | Product/model name of the device. |
| `vendor` | `str` | `"Error getting data"` | Vendor/manufacturer name. |
| `physid` | `str` | `"0"` | Physical ID (bus position). Used differently per class. |
| `serial` | `str` | `"Error getting data"` | Serial number. Used for MAC address in `NetworkCard`. |
| `children` | `List[Hardware]` | `[]` | Sub-components. Serialized recursively via `to_dict()`. |

---

## Optional Fields (serialized only if truthy)

These fields are omitted from JSON output if their value is `0`, `""`, `{}`, or `[]`:

| Field | Type | Default | Used By | Description |
|-------|------|---------|---------|-------------|
| `width` | `int` | `0` | Processor (data bus width, bits), Memory (data width, bits), ComputerSystem | Numeric width in bits |
| `size` | `int` | `0` | PhysicalMemory (bytes), PhysicalDisk (bytes) | Size in bytes or units |
| `clock` | `int` | `0` | Processor (MHz), Memory (MHz) | Clock speed |
| `capacity` | `int` | `0` | LogicalDisk (bytes), PartitionDisk (bytes), NetworkCard | Total capacity |
| `units` | `str` | `""` | Processor (`"Hz"`), Memory (`"bytes"`), NetworkCard (`"bit/s"`) | Unit label for size/clock |
| `date` | `str` | `""` | Firmware (WMI datetime string) | Manufacture/release date |
| `version` | `str` | `""` | Firmware (BIOS version) | Version string |
| `logicalname` | `str` | `""` | LogicalDisk (volume label), NetworkCard (connection name), CdRom (drive letter) | OS-assigned logical name |
| `dev` | `str` | `""` | PhysicalDisk, LogicalDisk | Device path (always empty in current implementation) |
| `businfo` | `str` | `""` | Processor (`"cpu@"`), PhysicalDisk (`"scsi@N:0.0.0"`), Pci/Usb | Bus topology string |
| `slot` | `str` | `""` | Processor (socket label), PhysicalMemory (bank/DIMM slot) | Physical slot label |
| `deviceid` | `str` | `""` | PhysicalDisk, PartitionDisk, LogicalDisk, CdRom, SoundDevice | WMI `DeviceID` |
| `pnpdeviceid` | `str` | `""` | NetworkCard, GraphicCard, CdRom, Usb, UsbDevice, PhysicalDisk, PartitionDisk | PnP Device ID |
| `parent_pnpdeviceid` | `str` | `""` | UsbDevice | PNP ID of the parent USB controller |
| `configuration` | `Dict[str, str]` | `{}` | ComputerSystem, NetworkCard, PhysicalDisk, PartitionDisk, LogicalDisk, CdRom, Usb, GraphicCard, SoundDevice | Key-value hardware configuration data |
| `capabilities` | `Dict[str, str]` | `{}` | NetworkCard, PhysicalDisk, PartitionDisk, CdRom, Usb, GraphicCard, SoundDevice | Key-value capability flags |

---

## `to_dict()` Serialization Rules

```python
def to_dict(self):
    data = {
        'id': self.id,
        'class': self.class_,    # 'class_' renamed to 'class'
        'claimed': self.claimed,
        'handle': self.handle,
        'description': self.description,
        'product': self.product,
        'vendor': self.vendor,
        'physid': self.physid,
        'serial': self.serial,
        'children': [child.to_dict() for child in self.children],
    }
    # Optional fields — only included if truthy:
    if self.width:       data['width'] = self.width
    if self.size:        data['size'] = self.size
    if self.clock:       data['clock'] = self.clock
    if self.capacity:    data['capacity'] = self.capacity
    if self.units:       data['units'] = self.units
    if self.date:        data['date'] = self.date
    if self.version:     data['version'] = self.version
    if self.logicalname: data['logicalname'] = self.logicalname
    if self.dev:         data['dev'] = self.dev
    if self.businfo:     data['businfo'] = self.businfo
    if self.slot:        data['slot'] = self.slot
    if self.deviceid:    data['deviceid'] = self.deviceid
    if self.pnpdeviceid: data['pnpdeviceid'] = self.pnpdeviceid
    if self.parent_pnpdeviceid: data['parent_pnpdeviceid'] = self.parent_pnpdeviceid
    if self.configuration: data['configuration'] = self.configuration
    if self.capabilities:  data['capabilities'] = self.capabilities
    return data
```

**Key consequences:**
- A `size` of `0` is **not serialized** (falsy). Check the component's documentation to distinguish "no data" from "truly zero".
- `children: []` is always serialized (it is in the core fields group), even when empty.
- `handle: ""` is always serialized, even though it is always empty.
- `physid: "0"` is always serialized even for classes that don't use it meaningfully.

### Stability Contract

> [!IMPORTANT]
> The `Hardware` dataclass and its `to_dict()` serialization output constitute a **public API contract** consumed by `migasfree-client` for hardware inventory synchronization. Changes to this contract require coordination with the downstream consumer.

**Rules for modifying the `Hardware` dataclass:**

1. **Adding new optional fields** (with falsy defaults that are omitted from JSON): Safe. No downstream impact.
2. **Renaming or removing existing fields**: **Breaking change.** Requires a coordinated release with `migasfree-client`.
3. **Changing the default value of core fields** (e.g. `product`, `vendor`, `serial`): **Behavioral change.** Must be documented and communicated.
4. **Changing `to_dict()` serialization logic** (e.g. which fields are always-present vs. optional): **Breaking change.**

---

## Dynamic Attributes (not in dataclass)

Two classes set additional attributes directly on the `Hardware` object that fall outside the dataclass definition and therefore **do not appear in JSON output**:

| Class | Dynamic Attribute | Purpose |
|-------|------------------|---------|
| `UsbDevice` | `class_guid` | Raw ClassGuid string for device classification logic |
| `UsbDevice` | `service` | WMI Service string for exclusion filtering |

---

## Error Sentinel & Empty Value Strategy (Hybrid Model)

The emulator implements a **hybrid data integrity policy** to handle absent values and query failures, ensuring clean telemetry report files without losing critical system diagnostics:

| Scenario | Value assigned | Serialized JSON behavior | Description |
|---|---|---|---|
| **Absent / Empty Field from Hardware** | `""` (Empty string) / `0` / `None` | **Omitted** or empty | WMI query completed successfully, but the property was empty, null, or unsupported by the hardware OEM (e.g. an unprogrammed battery serial). Avoids false positive errors. |
| **Complete WMI Query Failure** | `"Error getting data"` | **Serialized as string** | The entire WMI query failed (e.g., class not registered `0x80041010` on target OS image, or `Access Denied`). Sentinel fields alert the sysadmin to recolection errors. |
| **Unresolved Fallback Properties** | `"Unknown"` | **Serialized as string** | Default fallback placeholder when structural matching did not map a core attribute. |

This hybrid approach guarantees that actual hardware variations or empty fields do not dirty the report with misleading error strings, while ensuring that infrastructure-level WMI connectivity and authorization failures remain completely transparent and actionable.
