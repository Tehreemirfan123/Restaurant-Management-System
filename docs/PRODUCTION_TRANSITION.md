# LATER — Portfolio demo → real business production

What to change **if** the client decides to use the system for her real
business. Nothing here is needed for the portfolio demo. Companion to
`PORTFOLIO_DEPLOYMENT.md` (NOW), `ARCHITECTURE.md` (core vs restaurant),
`production-deployment.yaml` and `backup-cronjob.yaml` (the hardened k8s path).

The good news: the production path is already largely built — hardened
Dockerfiles, `k8s/production-deployment.yaml` (secrets, PVC, NetworkPolicies,
restricted PSS, probes, migration initContainer), `backup-cronjob.yaml`, CI,
rate limiting, structured logging, the `SECRET_KEY` production gate. Going live
is mostly **supplying real values and turning existing pieces on**, not new
engineering.

---

## Demo → Production, at a glance

| Concern | Demo (now) | Production (later) |
|---|---|---|
| Secrets | inline demo values in `portfolio-demo.yaml` | real values in a Secret / secrets manager, rotated |
| Credentials | `admin / admin123` | strong per-person accounts; demo admin deleted |
| Cluster | local `kind`, ephemeral | managed k8s (or k3s VM); use `production-deployment.yaml` |
| Exposure | port-forward + quick tunnel | Ingress + real domain + Let's Encrypt (cert-manager) |
| Data | seeded menu, no transactions | real menu; real orders accumulate; backups on |
| Network | NetworkPolicies omitted | enforced (CNI: Calico/Cilium) |
| Backups | none (ephemeral) | nightly `pg_dump` + off-site + restore drills |

---

## Topic-by-topic

**Production secrets & password rotation** — Generate fresh `SECRET_KEY`
(`openssl rand -hex 32`) and a strong DB password; create the Secret out-of-band
(`kubectl create secret …`) or via Sealed Secrets / External Secrets, never in
git. Delete the demo admin and rotate any credential that ever appeared in a
demo. `APP_ENV=production` already refuses the insecure default key.

**Secure environment variables** — Real `CORS_ORIGINS`, `FRONTEND_URL`,
`API_BASE_URL` for the domain; secrets from the Secret, non-secrets from the
ConfigMap (both already wired in `production-deployment.yaml`).

**Database migration & backup strategy** — Migrations already run as an
initContainer (`alembic upgrade head`). Turn on `backup-cronjob.yaml` (nightly
`pg_dump` → PVC) and add the off-site upload step (S3/GCS) that's stubbed there.
**Run periodic restore drills.**

**Real business data setup** — Replace seeded sample data with the real menu,
tables, inventory and settings via the admin UI (not SQL). Keep no leftover
demo rows.

**User/staff accounts & roles/permissions** — Create real per-person staff
accounts (no shared logins); assign roles from the RBAC matrix. The role→
permission model exists; just populate real people. (Config, per client.)

**Domain & HTTPS** — Point a real domain at the Ingress; enable TLS via
cert-manager + Let's Encrypt (annotations already in `production-deployment.yaml`).
Only the frontend is exposed; backend/DB stay ClusterIP.

**Production PostgreSQL** — Either the in-cluster Postgres + PVC (fine to start)
or a managed Postgres (RDS/Cloud SQL/Neon) for automated backups, HA and
point-in-time recovery. Switching is just `DATABASE_URL`.

**Persistent storage** — Set a real `storageClassName` on the PVC; ensure the
volume is backed by durable cloud storage with snapshots.

**File/media storage** — The file module supports a storage driver; use S3/GCS
in production rather than local disk so uploads survive pod restarts.

**Payment gateway** — Flip `PAYMENT_GATEWAY_ENABLED` on (frontend) and set
`PAYMENT_GATEWAY=jazzcash|easypaisa` + merchant credentials (backend). Confirm
the real callback field names / response codes against the provider before
taking live money. (Core module; per-client credentials.)

**Email/SMS/WhatsApp** — Add provider credentials for the notification channels
the client uses; templates are per-client config. (Core adapters; client creds.)

**Monitoring & logging / error tracking** — Ship structured logs to a log
store; add uptime monitoring on `/health`; wire an error tracker (Sentry) into
backend and frontend. (Core capability; per-client DSN.)

**Kubernetes production considerations & scaling** — Use
`production-deployment.yaml`: resource requests/limits (set), multiple backend/
frontend replicas (set to 2), add a HorizontalPodAutoscaler and
PodDisruptionBudgets if load warrants; a single Postgres writer stays 1 replica
(scale reads via a managed DB if needed).

**Database security** — Strong password, DB reachable only from the backend
(NetworkPolicy already restricts it), TLS to a managed DB, least-privilege DB
user, no public exposure.

**Auth/security hardening** — Already done: bcrypt, JWT with iss/aud, rate
limiting, security headers (HSTS/CSP), read-only root FS, non-root, dropped
caps, restricted PSS. Optionally shorten token TTL + add refresh tokens if the
client wants tighter sessions (currently 7-day by design).

**Backups & disaster recovery** — Nightly dumps off-site (CronJob), documented
restore procedure, periodic restore tests, and a managed-DB PITR option for RPO
near zero.

**CI/CD** — Extend the existing GitHub Actions (tests + build) to build & push
images to a registry and deploy on tag/release; keep migrations in the deploy
step. Add a staging environment before prod.

**Updates & rollback** — Versioned images; `kubectl rollout undo` for app
rollback; DB rollback via restore (why restore drills matter). Deploy behind a
staging check.

**Client-specific configuration** — Brand, terminology, roles, enabled modules,
payment methods, delivery/advance params live in `client.config.yaml`, mounted
as a ConfigMap (`CLIENT_CONFIG_PATH`). One file per client.

**Data privacy & access control** — The system stores customer name/phone/
address: add a privacy policy + terms, restrict PII to authorised roles (RBAC
already gates the orders/customers lists), set audit-log retention, and honour
deletion requests. Comply with local data-protection rules.

---

## Before go-live: changes to make in the current code/config

- Delete the demo admin; create real accounts; rotate every demo secret.
- Move from `portfolio-demo.yaml` to `production-deployment.yaml` (real images, real Secret, storageClass, domain, TLS).
- Provide `client.config.yaml` as a ConfigMap; set `CLIENT_CONFIG_PATH`.
- Turn on backups (`backup-cronjob.yaml`) + off-site upload; do a restore drill.
- Wire error tracking + uptime monitoring.
- If taking online payments: enable + configure the gateway and verify callbacks.
- Add privacy policy / terms.

None of these require architecture changes — they're configuration, secrets and
turning on already-built capabilities.

---

## Core framework vs client-specific

Use this to decide where a change lives (see `ARCHITECTURE.md` for the full map).

| Change | Belongs in… |
|---|---|
| Secret management, RBAC engine, auth hardening, rate limiting, security headers | **Core framework** — every client benefits |
| Backup CronJob, migration initContainer, health probes, K8s hardening patterns | **Core framework** |
| Notification adapters, payment gateway abstraction, file storage drivers, error-tracking + monitoring hooks | **Core framework** (the mechanism) |
| CI/CD pipeline templates, deployment manifests | **Core framework** (templated), values per client |
| Actual secret values, domain, TLS cert, DB endpoint | **Client-specific** |
| Real menu/data, staff accounts, role assignments | **Client-specific** |
| Provider credentials (payment/SMS/WhatsApp/Sentry DSN) | **Client-specific** |
| `client.config.yaml` (brand, terminology, features, params) | **Client-specific** |
| Bespoke screens or industry logic a single client requests | **Client-specific module** (unless it recurs → promote to core) |

Rule of thumb: **mechanisms and hardening → core; values, credentials, data and
one-off requests → client.** A client need that recurs across two or three
clients is promoted into core behind a version bump.
