# ADR 002: WMI Entity Allowlist for Security Hardening

- **Status**: Accepted
- **Date**: 2023-02-10
- **Author**: Jose Antonio Chavarría

## Context

The `HardwareClass` base class builds WMI queries (WQL) and calls WMI methods to retrieve hardware information. Without a validation layer, a bug or malicious input could construct queries against arbitrary WMI entities — potentially accessing sensitive system information beyond hardware enumeration, or triggering WMI methods with side effects.

The system must:

1. Prevent WQL injection attacks via user-controlled strings (e.g., from CLI arguments or config files).
2. Limit WMI access to only the entities needed for hardware reporting.
3. Log unauthorized access attempts for forensic audit.

## Decision

Implement a **WMI Entity Allowlist** (`_WMI_ENTITY_ALLOWLIST`) as an immutable `frozenset` on the abstract base class, paired with a `_validate_entity()` gate and `_sanitize_wql_value()` for WQL injection defense.

### Allowlist

```python
_WMI_ENTITY_ALLOWLIST = frozenset({
    'Win32_baseboard',
    'Win32_ComputerSystem',
    'Win32_Processor',
    'Win32_PhysicalMemory',
    # ... 22 more entities
})
```

The `frozenset` is immutable post-definition — no runtime mutation is possible, preventing privilege escalation via list injection.

### Validation Gate

```python
def _validate_entity(self, entity):
    if entity not in self._WMI_ENTITY_ALLOWLIST:
        logger.error(f'Security Alert: Unauthorized WMI entity: {entity}')
        raise ValueError(f'Unauthorized WMI entity: {entity}')
```

Called before any WMI access. Rejects unknown entities with a logged security alert.

### WQL Sanitization

```python
def _sanitize_wql_value(self, value):
    return str(value).replace('"', '').replace("'", '').replace(';', '')
```

Strips double quotes, single quotes, and semicolons from values interpolated into WQL WHERE clauses — the three characters that could alter WQL query semantics.

## Consequences

### Positive

- **Defense in depth**: Even if a caller bypasses `_validate_entity`, the hardcoded `frozenset` is immutable — no `list.append` attack possible.
- **Audit logging**: Every rejected entity access is logged as `ERROR` with `Security Alert` prefix, enabling SIEM integration.
- **WQL injection prevention**: `_sanitize_wql_value` strips statement terminators and quote delimiters, mirroring SQL injection defenses.

### Negative

- **Case sensitivity**: The allowlist uses exact string matching. WMI is case-insensitive (`Win32_Processor` equals `win32_processor`), so the allowlist must include multiple case variants for entities accessed with inconsistent casing (e.g., `Win32_diskdrive`, `Win32_Diskdrive`, `Win32_DiskDrive`). This creates maintenance burden and the risk of missing a variant.
- **Validation coverage gap**: `_validate_entity` is not uniformly called before every WMI access. Some methods (e.g., `ide.py:129` accessing `Win32_IDEControllerdevice`) rely on the entity being in the allowlist without explicit validation at the call site.
- **No runtime normalization**: The allowlist doesn't normalize case at comparison time, so a misspelled variant in source code would be rejected even if the correct one exists.

## Alternatives Considered

**Wildcard-based allowlist** (e.g., `Win32_*`): Rejected — too permissive. WMI namespace includes administrative and destructive entities that should never be accessed.

**No allowlist, audit-only mode**: Rejected — passive logging without blocking doesn't prevent information disclosure. The system must fail closed.
