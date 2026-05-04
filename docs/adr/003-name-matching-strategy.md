# ADR 003: Device ID Normalization Strategy for WMI Association Matching

- **Status**: Accepted
- **Date**: 2023-05-20
- **Author**: Jose Antonio Chavarría

## Context

WMI association classes (e.g., `Win32_IDEControllerdevice`, `Win32_DiskDriveToDiskPartition`, `Win32_USBControllerdevice`) link hardware components via `Antecedent`/`Dependent` properties containing device ID strings. These IDs must be matched against PNPDeviceID values from entity queries to build the hardware tree.

WMI returns device IDs with inconsistent formatting:

- Variable backslash escaping: `\\` vs `\\\` vs `\`
- Mixed case: `PCI\VEN_8086` vs `pci\ven_8086`
- Quote-wrapped values in association strings: `"\\\\host\\root\\cimv2:Win32_IDEController.DeviceID=\"PCI\\VEN_8086\""`

A canonical normalization strategy is needed for reliable matching.

## Decision

Apply a two-layer normalization strategy:

### Layer 1: Association String Parsing

```python
value = assoc.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')
```

Extracts the value after the first `=` sign, strips all double quotes, and normalizes `\\\\` (WMI-escaped double backslash) to `\\`.

### Layer 2: Canonical Device ID Normalization

```python
normalized = device_id.strip().replace('\\', '').lower()
```

Three transformations:

1. **`strip()`** — removes leading/trailing whitespace.
2. **`replace('\\', '')`** — collapses all backslash separators. This is lossy but intentional: WMI device paths differ only in enumeration syntax (`PCI\VEN_8086&DEV_1234` vs `PCI\VEN_8086&DEV_1234&SUBSYS_5678`), and the substring after stripping slashes is sufficient for matching parent-child relationships.
3. **`lower()`** — case-insensitive comparison since WMI is case-insensitive.

### Application Sites

| File | Normalization Use |
| --- | --- |
| `ide.py:122,147` | Disk PNP ID cache population and IDE child attachment |
| `partition_disk.py:123` | Disk-drive-to-partition association matching |
| `logical_disk.py:109` | Partition-to-volume mapping |
| `usb_device.py:87-88` | USB controller-to-device association parsing |
| `pci.py:67` | PCI device prefix extraction (`device_id[0:3].lower()`) |

### WQL Injection Protection

All user-controlled strings interpolated into WQL WHERE clauses pass through `_sanitize_wql_value()` before the normalized comparison, preventing WQL injection during the matching step.

## Consequences

### Positive

- **Deterministic matching**: Eliminates false negatives from case or whitespace discrepancies across different WMI calls.
- **Resilient to WMI formatting**: Handles the inconsistent backslash escaping that WMI applies to association property strings.
- **Centralized pattern**: All matching in the codebase follows the same `strip → deslash → lowercase` pipeline, making the behavior predictable during debugging.

### Negative

- **Lossy normalization**: Stripping backslashes removes path hierarchy information. Could theoretically cause false positives if two different devices normalize to the same string. Mitigated by WMI's globally unique PNPDeviceID scheme — collisions are extremely unlikely in practice.
- **No prefix matching**: The full-string comparison after normalization doesn't support hierarchical matching (e.g., matching `PCI\VEN_8086` to `PCI\VEN_8086&DEV_1234`). Each association must explicitly extract and normalize both sides.
- **Maintenance coupling**: Any new hardware class that performs device ID matching must replicate the normalization pipeline and WQL sanitization. The pattern is documented here but not enforced by the type system.

## Alternatives Considered

**Regex-based extraction**: Using `re.search(r"DeviceID=['\"]?([^'\"]+)", ref)` for association string parsing, as used in `partition_disk.py:108-113` as a fallback. Rejected as the primary strategy because it's fragile against WMI formatting changes (different quote styles, attribute ordering).

**Exact string comparison**: Skipping normalization and comparing raw WMI strings. Rejected — WMI's inconsistent casing and escaping produced too many false negatives in testing.
