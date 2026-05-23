# DOMAIN.md Format

The domain glossary lives in `DOMAIN.md` (NOT `CONTEXT.md`, which is reserved for ICM L1 routing). This file captures the project's ubiquitous language — the terms that mean something specific in this codebase.

## Structure

```md
# Domain Language — {Project Name}

{One or two sentence description of what domain this covers.}

## Language

**Order**:
A confirmed purchase request from a customer, containing one or more line items.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account

## Flagged Ambiguities

- **"Event"** — currently used for both domain events (OrderPlaced) and UI events (onClick). Needs disambiguation.

## Example Dialogue

> **Dev:** "When a customer cancels, do we void the invoice?"
> **Domain expert:** "Only if it hasn't been sent. Once sent, we issue a credit note instead."
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list others as _Avoid_.
- **Flag conflicts explicitly.** If a term is used ambiguously, call it out in "Flagged Ambiguities."
- **Keep definitions tight.** One or two sentences max. What it IS, not what it does.
- **Only include terms specific to this project's domain.** General programming concepts don't belong.
- **Group terms under subheadings** when natural clusters emerge.
- **Write an example dialogue** demonstrating how terms interact.

## Single vs Multi-Domain Repos

**Single domain (most repos):** One `DOMAIN.md` at the repo root.

**Multiple domains:** A `DOMAIN-MAP.md` at the repo root lists the domains and their relationships:

```md
# Domain Map

## Domains

- [Ordering](./src/ordering/DOMAIN.md) — receives and tracks customer orders
- [Billing](./src/billing/DOMAIN.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/DOMAIN.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched`; Billing generates invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

The skill infers which structure applies:
- If `DOMAIN-MAP.md` exists, read it to find domains
- If only a root `DOMAIN.md` exists, single domain
- If neither exists, create a root `DOMAIN.md` lazily when the first term is resolved
