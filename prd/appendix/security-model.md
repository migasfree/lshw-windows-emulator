# Security Model

Security architecture, threat mitigations, and permission requirements of the LsHw Windows Emulator.

---

## Threat Model

The tool is a **read-only hardware inventory tool**. It makes no changes to system state. The primary security concerns are:

| Threat | Risk | Mitigation |
|--------|------|-----------|
| WMI injection (unauthorized entity access) | Attacker could exfiltrate sensitive WMI data beyond hardware | Entity allowlist (`_WMI_ENTITY_ALLOWLIST`) |
| WQL value injection | Malicious string in a query parameter alters query semantics | `_sanitize_wql_value()` |
| Privilege escalation | The tool requires admin rights; incorrect use could expose sensitive info | No mitigation beyond standard OS ACLs |
| Sensitive data in output | Serial numbers, MACs, UUIDs appear in output | By design; output must be handled appropriately by callers |

---

## WMI Entity Allowlist

**Source:** `HardwareClass._WMI_ENTITY_ALLOWLIST` (frozenset, immutable at runtime)

All WMI entity access passes through `_validate_entity()`. Any entity name not in the allowlist causes:
1. An `ERROR`-level log message: `"Security Alert: Unauthorized WMI entity access attempted: {entity}"`
2. A `ValueError` raised to the caller

**Validation is case-insensitive** — entity names are lowercased before comparison since WMI itself is case-insensitive.

The allowlist contains exactly 22 entries. See [→ Enum Dictionary: WMI Entity Allowlist](./enum-dictionary.md#wmi-entity-allowlist).

### Where `_validate_entity()` is called

| Class | Entity Validated Before Use |
|-------|---------------------------|
| `HardwareClass.build_wql_select()` | The `table` argument |
| `HardwareClass.get_hardware()` | `self.wmi_method` |
| `Ide.get_hardware()` | `Win32_IDEControllerdevice` |
| `Ide.format_data()` | `Win32_IDEControllerdevice`, `Win32_diskdrive` |
| `Ide._attach_ide_child()` | `Win32_PNPEntity`, `Win32_diskdrive` |
| `LogicalDisk.get_hardware()` | `Win32_LogicalDiskToPartition`, `Win32_LogicalDisk`, `Win32_diskpartition` |
| `PartitionDisk.get_hardware()` | `Win32_DiskDriveToDiskPartition`, `Win32_diskpartition`, `Win32_diskdrive` |
| `NetworkCard.get_hardware()` | `Win32_NetworkAdapter` (via `build_wql_select`) |
| `PhysicalDisk.get_hardware()` | `Win32_diskdrive` (via `build_wql_select`) |

---

## WQL Value Sanitization

**Source:** `HardwareClass._sanitize_wql_value(value)`

Before any user-controlled or WMI-returned string is interpolated into a WQL `WHERE` clause, it passes through the sanitizer:

```python
def _sanitize_wql_value(self, value):
    return str(value).replace('"', '').replace("'", '').replace(';', '')
```

**Characters stripped:** `"` (double quote), `'` (single quote), `;` (semicolon)

This prevents an injected value from:
- Terminating a string literal and injecting additional WQL clauses
- Chaining multiple WQL statements via semicolons

### Sanitized call sites

| Class | Field Sanitized |
|-------|----------------|
| `PhysicalDisk.get_hardware()` | `PNPDeviceID` (from `dev_id`) |
| `CdRom.get_hardware()` | `PNPDeviceID` (from `dev_id`) |
| `Ide.get_hardware()` | `PNPDeviceID` (from associations) |
| `Ide._attach_ide_child()` | `PNPDeviceID` (from PNP entity result) |
| `PartitionDisk.get_hardware()` | `DeviceID` (from disk/partition results) |
| `LogicalDisk.get_hardware()` | `DeviceID` (from association results) |

---

## WMI Connection Security

**Source:** `WMIConnection` (Singleton)

- Uses the default `wmi.WMI()` constructor — connects to the **local** machine only, using the **current user's credentials**.
- No remote WMI connections are initiated.
- No alternative namespaces or elevated impersonation flags are configured.
- The connection is reused across all class instances in a single invocation (singleton pattern), avoiding multiple authentication round-trips.

---

## Permission Requirements

| Operation | Required Privilege |
|-----------|-------------------|
| Running `lshw` on Windows | **Local Administrator** (or member of `Administrators` group) |
| Querying most WMI classes | Standard Admin |
| `Win32_PhysicalMemory` (bank-level detail) | May return no data in restricted environments (VM/RDS) — fallback to `TotalPhysicalMemory` |

**Failure behavior:** If access is denied:
- `wmi.x_access_denied` exception is caught at the CLI dispatch level.
- Error code `1–16` is returned depending on which class failed.
- `"Access denied: {exception}"` is appended to the error message.

---

## Sensitive Data in Output

The tool intentionally outputs the following sensitive fields — callers must handle output appropriately:

| Field | Classes | Data |
|-------|---------|------|
| `serial` | ComputerSystem, BaseBoard, Firmware, NetworkCard | Machine serial number, MAC address |
| `configuration.uuid` | ComputerSystem | System UUID |
| `deviceid` | PhysicalDisk, LogicalDisk, PartitionDisk | WMI device paths |
| `pnpdeviceid` | Multiple | PnP device identifiers (may encode hardware specifics) |

There is **no built-in output redaction or masking** of sensitive fields.

---

## Non-Windows Stub (Cross-Platform Safety)

On non-Windows systems, the `wmi` module is replaced by a minimal stub:

```python
wmi = types.ModuleType('wmi')
wmi.WMI = None
wmi.x_wmi = type('x_wmi', (Exception,), {})
wmi.x_access_denied = type('x_access_denied', (Exception,), {})
```

The `WMIConnection.get_instance()` immediately raises `RuntimeError('WMI is only available on Windows systems')` if `wmi.WMI is None`. This prevents any WMI calls from executing on non-Windows systems without the need for platform guards throughout the codebase.
