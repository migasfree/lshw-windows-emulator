# ADR 001: Factory + Registry Pattern for Hardware Class Dispatch

- **Status**: Accepted
- **Date**: 2021-07-15
- **Author**: Jose Antonio Chavarría

## Context

The project needs to expose a CLI (`lshw --class-hw <name>`) that dispatches to one of ~15 hardware-specific classes. Each class queries a different set of WMI entities and maps results to the `Hardware` dataclass. The set of hardware classes must be extensible without modifying the CLI entry point or the base class.

Two patterns were considered:

1. **Simple dictionary mapping** (`if name == 'memory': return PhysicalMemory()`) — requires updating the dispatch table for every new class.
2. **Plugin-based auto-discovery** — all class modules self-register, and the factory resolves by name at runtime.

## Decision

Use the **Factory + Registry** pattern via class-level dictionaries and a decorator:

```python
@classmethod
def factory(cls, entity):
    return cls._entities_[entity]

@classmethod
def register(cls, entity, parent=None):
    def decorator(subclass):
        cls._entities_[entity] = subclass
        subclass._entity_ = entity
        # ... parent-child tree registration
        return subclass
    return decorator
```

Each hardware subclass is decorated with `@HardwareClass.register('ComputerSystem')`.

Module auto-discovery in `classes/__init__.py` uses `pkgutil.iter_modules()` to import all modules in the package, triggering the decorators at import time. The CLI then dispatches via `HardwareClass.factory(name)()`.

## Consequences

### Positive

- **Zero-configuration extension**: Adding a new hardware class requires only a new `.py` file in `classes/` with the `@register` decorator. No changes to core files.
- **Tree hierarchy**: The `parent` parameter in `register()` builds a parent-child graph, enabling `children=True` recursive traversal without hardcoding the tree structure.
- **Type safety**: `factory()` returns the subclass directly — no `isinstance` casting needed.
- **Single source of truth**: The registry is the canonical list of supported hardware classes.

### Negative

- **Implicit registration**: The decorator has side effects at import time. If a module is added but `iter_modules` fails to load it (e.g., due to a syntax error), the class silently won't register — no compile-time error.
- **Global mutable state**: `_entities_` and `_children_` are class-level dictionaries, shared across all instances. Tests must not mutate the registry concurrently.
- **No duplicate detection**: Registering the same entity name twice overwrites the previous entry without warning.

## Alternatives Considered

**Enum-based dispatch**: An `IntEnum` mapping class names to constructors. Rejected because it requires modifying the enum for every new class and doesn't support the parent-child hierarchy.
