# Architecture — Core vs Restaurant boundary

This document is the **authoritative boundary** between the horizontal,
reusable **core** of this system and the vertical, restaurant-specific
**module**. It exists so that when we build the next management system
(clinic, LMS, CRM, …) we reuse the core instead of starting over.

> Strategy context: this repo (Mehak's Kitchen RMS) is the **seed** of a
> reusable Management System framework. The full plan is in the
> "Management System Framework Blueprint". This file is the concrete,
> file-by-file version of that plan for *this* codebase.

---

## 1. The layered model

```
┌──────────────────────────────────────────────────────────┐
│  Client instance      client.config.yaml + deploy values  │  ← per client
├──────────────────────────────────────────────────────────┤
│  Restaurant module    menu, orders, POS, kitchen,          │  ← the vertical
│                       inventory, recipes, waste, delivery  │
├──────────────────────────────────────────────────────────┤
│  Core platform        auth, RBAC, users, customers,        │  ← reused everywhere
│                       payments, reports, settings, audit,  │
│                       files, API, admin/portal shells      │
└──────────────────────────────────────────────────────────┘
```

**The dependency rule (one direction only):**

- **Core must never import the restaurant module.** Grep test:
  core files must not reference `menu`, `recipe`, `waste`, `kitchen`, `pos`, `delivery`.
- **The restaurant module depends on core** (uses its models, services, auth).
- **Both read the client profile** (`client.config.yaml`) for configuration.

If you ever need core to "know about" a restaurant concept, that's the signal
to add a **seam** (an event, a hook, or a config field) instead — see §5.

---

## 2. Backend classification

Layers: **Core** (reuse as-is), **Restaurant** (vertical), **Core¹** (a core
primitive that currently carries restaurant flavour — generalise on extraction,
see §5).

| Area | File(s) | Layer | Notes |
|------|---------|-------|-------|
| Config / secrets | `core/config.py` | Core | env + `.env`, single source |
| Client profile | `core/client_config.py`, `client.config.yaml` | Core | loads the per-client profile |
| Security | `core/security.py` | Core | JWT, bcrypt |
| Rate limiting | `core/rate_limit.py` | Core | slowapi limiter |
| DB / session | `database/` | Core | engine, `get_db`, `Base` |
| Auth dependency | `dependencies/auth.py` | Core | `get_current_staff`, `require_admin` |
| Auth API | `routers/auth.py`, `services/staff_service.py` | Core | login, staff CRUD |
| Client-config API | `routers/config.py` | Core | `GET /client-config` |
| Users / staff | `models/staff.py`, `schemas/staff.py` | Core | |
| Customers / CRM | `models/customer.py`, `routers/customers.py`, `services/customer_service.py`* | Core | *(if present) |
| Settings | `models/settings.py`, `routers/settings.py`, `services/settings_service.py` | Core | some fields are restaurant knobs (delivery) |
| Payments + gateway | `models/payment.py`, `routers/payments.py`, `routers/payment_gateway.py`, `services/payment_service.py`, `services/payment_gateway.py` | Core | provider abstraction is fully reusable |
| Advance/pricing rule | `services/pricing.py` | Core | generic advance rule; params from config/settings |
| Audit / logging | (cross-cutting in `main.py`, services) | Core | |
| Tables | `models/table.py`, `routers/tables.py` | Core¹ | dine-in legacy; generic "resource" primitive |
| **Orders** | `models/order.py`, `routers/orders.py`, `services/order_service.py` | **Core¹** | order lifecycle is a core primitive, but it imports `MenuItem` and knows delivery/pickup — the main seam to generalise |
| Reports | `routers/reports.py`, `services/reports_service.py` | **Mixed** | revenue/orders/customers = core; **dish costing** = restaurant |
| Menu (rotating daily) | `models/menu.py`, `routers/menu.py`, `services/menu_service.py` | **Restaurant** | `day_of_week` menu, "today's menu" |
| Inventory | `models/inventory.py` (InventoryItem), `routers/inventory.py` | Core¹ | inventory is semi-generic |
| Recipes / costing | `models/inventory.py` (Recipe, RecipeIngredient), `routers/recipes.py` | **Restaurant** | |
| Waste log | `models/inventory.py` (WasteLog), `routers/waste.py` | **Restaurant** | |
| Feedback | `models/order.py` (OrderFeedback), feedback routes | Core¹ | generic review primitive |
| Seed | `seed.py` | **Restaurant** | seeds the weekly menu (+ core admin) |
| App assembly | `main.py` | Core | wires routers together |

\* Enum note: `models/enums.py` holds both core enums (Role, PaymentStatus…)
and restaurant ones (DayOfWeek, OrderCategory). On extraction, split it the
same core/restaurant way.

---

## 3. Frontend classification

| Area | Files | Layer |
|------|-------|-------|
| API client, auth, theme, error boundary | `services/api.js`, `context/AuthContext`, `context/ThemeContext`, `components/ErrorBoundary`, `components/ProtectedRoute` | Core |
| Admin shell | `components/AdminLayout` | Core |
| Staff/customers/settings admin | `pages/AdminStaff`, `AdminCustomers`, `AdminSettings` | Core |
| Orders + reconciliation admin | `pages/AdminOrders`, `AdminPayments` | Core¹ |
| Login | `pages/Login` | Core |
| Dashboard / reports | `pages/AdminDashboard`, `AdminReports` | Mixed (KPIs + costing are restaurant) |
| Customer website | `components/CustomerLayout`, `pages/Home`, `About`, `Contact`, `CustomerMenu`, `Cart`, `OrderTracking` | Restaurant |
| POS / Kitchen | `pages/POS`, `pages/Kitchen` | Restaurant |
| Menu / recipes / inventory / waste admin | `pages/AdminMenu`, `AdminRecipes`, `AdminInventory`, `AdminWaste` | Restaurant |
| Delivery / WhatsApp / client params | `utils/delivery.js`, `utils/whatsapp.js`, `config.js` | Restaurant |

---

## 4. The client profile — `client.config.yaml`

The per-client **configurable surface** lives in `client.config.yaml` at the
repo root: identity, brand, terminology, roles, enabled modules, payment
methods, delivery/advance parameters and feature flags. It is **client data,
not secrets** — secrets stay in the environment / Kubernetes Secrets.

- Loaded by `backend/core/client_config.py` (path resolved from the file, or
  from `CLIENT_CONFIG_PATH`).
- Non-secret parts served at **`GET /client-config`** for the frontend
  (labels, feature flags, enabled modules, offered payment methods).
- **In Kubernetes:** mount it as a **ConfigMap** and set `CLIENT_CONFIG_PATH`
  to the mount path (the backend image build context doesn't include the
  repo-root file). This is how each client instance supplies its own profile.

> Today the running app still reads live values (delivery fee, advance %, etc.)
> from the DB `settings` table; the profile is the declarative source a new
> client is spun up from and the single place these knobs are described. Making
> `settings` seed from the profile is a planned next step, not done yet.

---

## 5. Known seams (where to generalise on extraction)

These are the coupling points to resolve **when** we extract a real `ms_core`
package (after client #2–3) — not before:

1. **Order → MenuItem.** `order_service` imports `MenuItem`. Generalise to an
   "orderable item" interface so the order lifecycle becomes vertical-agnostic
   (a clinic orders *procedures*, an LMS *enrolments*).
2. **Reports mixing.** Split `reports_service` into core metrics
   (revenue/orders/customers) and a restaurant reports module (dish costing).
3. **Settings fields.** Delivery/advance fields on the core `Settings` model
   are restaurant knobs; move vertical settings into the module on extraction.
4. **Enums file.** Split `enums.py` into core vs restaurant enums.

Until then, the boundary is enforced by **convention + this document + the
one-direction import rule**, which is enough to keep the next project cheap.

---

## 6. Extraction roadmap

- **Done now:** documented boundary (this file), one-direction import rule,
  `client.config.yaml` + loader + `GET /client-config`.
- **After client #2–3:** promote core into a versioned `ms_core` package + a
  `module-restaurant` package; resolve the §5 seams; add a `new-client`
  scaffolder and a private package registry.
- **Not yet (would be over-engineering):** a metadata-driven "everything is
  config" entity engine, a no-code builder, per-tenant runtime module toggling,
  multi-tenant SaaS billing.
