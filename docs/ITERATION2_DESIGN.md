# Iteration 2 Design: Event Ticket Sales

Status: **data model and API surface agreed; not yet implemented.**
See [CLAUDE.md](../CLAUDE.md) for the philosophy this design follows
(learning prototype, simple over robust) and [PLAN.md](../PLAN.md) for
where this sits in the overall roadmap.

## Scope

A ticket sales system for a **single venue, multiple events**. Explicitly a
learning prototype: the goal is to learn how a database, multiple Docker
services, and a simple UI work together — not to build a production-grade
ticketing platform. Simplifying assumptions are preferred over modeling the
general case (see CLAUDE.md's Iteration 2 section for the full guidance).

## Data model

**Venue** — `id`, `name`, `address`
Single row in practice; modeled as a table rather than hardcoded.

**Seat** — `id`, `venue_id`, `section`, `row`, `seat_number`
Fixed physical seat catalog, belongs to the venue (not to an event), reused
across every event. Seeded once (migration/seed script) rather than managed
through an API — the venue/seat layout doesn't change.

**Event** — `id`, `venue_id`, `name`, `starts_at`, `status`
(`scheduled` / `cancelled`)

**Ticket** — `id`, `event_id`, `seat_id`, `price`, `status`, `held_until`
(nullable), `cart_id` (nullable FK), `order_id` (nullable FK)
One row per (event, seat) pair, created when an event is set up. This single
entity is the seat inventory, the hold, *and* the sold ticket — its
`status` field carries it through the whole lifecycle:
- `available` — sellable
- `held` — in someone's cart, `held_until` set
- `sold` — purchased, `order_id` set
- `blocked` — admin has taken it off sale (broken seat, reserved outside the
  platform, etc.) — distinct from `held`/`sold` so it doesn't look purchased

**Cart** — `id`, `session_id`, `created_at`
`session_id` is an opaque token issued as a cookie on first visit — no login
system for this prototype.

**Order** — `id`, `buyer_name`, `buyer_email`, `created_at`, `status`
(`pending` / `confirmed` / `cancelled`)

## Concurrency

No background expiry job. Two mechanisms instead:

1. **Add-to-cart is a single conditional update**:
   ```sql
   UPDATE ticket SET status='held', cart_id=?, held_until=?
   WHERE id=? AND status='available'
   ```
   Check the affected-row count; 0 rows means someone else got there first.
   No locks, no version columns — relies on the database's own atomicity.

2. **Expired holds are reclaimed lazily**, not swept proactively. Any query
   that reads ticket availability (the list-available query, and the
   conditional update above) also treats `status='held' AND held_until <
   now()` as available. A ticket only actually flips back to `available` in
   the row itself the next time something tries to act on it — that's fine,
   nothing depends on the stored status being live between reads.

## API surface

Four services, split along these boundaries:

### Browsing (read-only)
- `GET /venue`
- `GET /events` — `status=scheduled` only
- `GET /events/{event_id}`
- `GET /events/{event_id}/tickets`

### Cart
- `POST /cart` — get-or-create for the session cookie (idempotent)
- `GET /cart`
- `POST /cart/items` — `{ticket_id}` → atomic hold
- `DELETE /cart/items/{ticket_id}` — release back to `available`

### Checkout
- `POST /checkout` — `{buyer_name, buyer_email}` → creates Order from the
  session's cart, flips its tickets to `sold`, clears the cart
- `GET /orders/{order_id}`

### Admin
- `POST /events` — creates the event and provisions one `Ticket` row per
  venue `Seat` at a given price
- `PATCH /events/{event_id}` — e.g. `{status: "cancelled"}`
- `POST /events/{event_id}/tickets/{ticket_id}/block` (and `/unblock`)
- `GET /admin/events` — all events regardless of status (unlike public
  Browsing, which only shows `scheduled`)

## Architecture decision: shared database

All four services read/write the **same** Postgres database directly,
rather than each service owning its own tables exclusively. This is a
deliberate simplification for a learning prototype and is *not* how a
"correct" microservices design would do it — recorded here so future-us
doesn't second-guess it without context.

**What "correct" would look like, for reference**: `Ticket`/`Seat` would
need their own service (an Inventory service) since three different
services currently write to `Ticket` (Cart holds, Checkout sells, Admin
blocks) — the rule in real microservices design is one writer per table.
That split introduces two hard problems this prototype deliberately avoids:

- **Checkout would span 3 databases** (Cart, Inventory, Order), so it can't
  be one transaction — it would need a **saga**: explicit compensating
  steps (release ticket A, release ticket B, ...) if a later step fails,
  since there's no `COMMIT` covering all of it.
- **Browsing would need data it doesn't own** — either calling Admin +
  Inventory synchronously on every request (coupling Browsing's uptime to
  theirs), or maintaining its own denormalized, eventually-consistent copy
  fed by events (`EventCreated`, `TicketSold`, ...) — **CQRS**. This is
  where the original PLAN.md sketch's "Azure Service Bus for event
  processing" idea would actually come in.

Worth revisiting if a future iteration specifically wants to learn
saga/event-driven patterns, but out of scope here.

## Not yet decided

- Database/ORM choice (PLAN.md's original sketch says PostgreSQL +
  SQLAlchemy; not confirmed in this design conversation)
- Docker Compose service layout (four service containers + Postgres — exact
  compose file, networking, and how they share the DB connection details
  not yet worked out)
- UI approach/framework
- Payment handling — out of scope per CLAUDE.md's simplification guidance
  unless revisited
