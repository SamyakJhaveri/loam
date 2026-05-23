# Language: Shared Vocabulary for Module Design

Use these terms consistently in every suggestion. Do not drift into "component," "service," "API," or "boundary."

## Core Terms

**Module** — anything with an interface and an implementation. Scale-agnostic: function, class, package, or architectural slice.

**Interface** — everything a caller must know to use the module correctly. The type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics.

**Implementation** — the code inside a module. Distinct from Adapter, which describes role rather than substance.

**Depth** — leverage at the interface. The amount of behavior a caller (or test) can exercise per unit of interface they have to learn. **Deep** = high leverage. **Shallow** = interface nearly as complex as the implementation.

**Seam** — a place where you can alter behavior without editing in that place. Borrowed from Michael Feathers.

**Adapter** — a concrete thing satisfying an interface at a seam.

**Leverage** — what callers get from depth. More capability per unit of interface learned.

**Locality** — what maintainers get from depth. Change, bugs, and knowledge concentrated in one place rather than distributed across callers.

## Principles

- Depth emerges from interface design, not implementation complexity. A deep module may internally use small, swappable components invisible to callers.
- **Deletion test**: does complexity disappear with the module, or scatter across callers?
- The interface is the test surface — callers and tests cross the same boundary.
- One adapter means a hypothetical seam. Two adapters means a real one. Don't build seams without two adapters unless you have a concrete reason.
