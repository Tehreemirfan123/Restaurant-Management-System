# Deployment plan & go-live runbook — Mehak's Kitchen

A concrete plan for taking the first system to production. Work top to bottom;
tick the checklist before you flip DNS.

> Scope: this is the **launch** path for the real business (one home kitchen).
> The Kubernetes manifests in `k8s/` are the **enterprise-client** path and are
> intentionally *not* used here — they'd be over-provisioned and costly for a
> single kitchen. Same app, right-sized host.

---

## 1. Hosting decision

**Chosen: a single small VM running Docker Compose behind Caddy (auto-TLS),
with nightly `pg_dump` to object storage.**

| Option | Effort | Monthly cost | When to use |
|--------|--------|--------------|-------------|
| **VM + Docker Compose + Caddy** ✅ | Low | ~$6–12 | This launch. One kitchen, low traffic, you already have the compose file. |
| PaaS (Render / Railway / Fly) | Lowest setup | ~$15–30 (+ managed Postgres) | If you'd rather not manage a server at all; slightly pricier. |
| Kubernetes (`k8s/`) | High | $$$ (cluster + LB) | Reserve for enterprise clients who need HA/scale. |

Why the VM: your `docker-compose.yml` already runs db + backend + frontend; the
frontend's nginx already reverse-proxies `/api` to the backend, so the browser
only ever hits one origin. Adding Caddy for TLS and closing the internal ports
is the whole delta.

---

## 2. Target launch architecture

```
Internet ──▶ Caddy (:443, auto-TLS)
                 └─▶ frontend (nginx :8080)  ── /api ─▶ backend (:8000) ─▶ postgres (:5432)
                                                                     │
                                          nightly pg_dump ──▶ object storage (off-site)
```

- Only Caddy is exposed publicly (443/80). **backend and postgres publish NO
  host ports** — they're reachable only on the compose network.
- Postgres data on a named Docker volume; nightly dump copied off the box.

---

## 3. Decisions to make first

- [ ] **Domain name** (e.g. `mehakskitchen.pk` / a subdomain) + DNS access.
- [ ] **VM provider & size** — DigitalOcean / Hetzner / Linode; 1 vCPU / 2 GB is plenty to start.
- [ ] **Off-site backup target** — an S3-compatible bucket (Backblaze B2, DO Spaces, etc.).
- [ ] **WhatsApp number** and **payment account details** to enter in Settings.
- [ ] **Admin credentials** for the owner.

---

## 4. Pre-launch checklist

**Infrastructure**
- [ ] Provision the VM, create a non-root sudo user, enable the firewall (allow 22, 80, 443 only).
- [ ] Install Docker + Docker Compose plugin.
- [ ] Point the domain's A record at the VM IP.

**Compose for production** (adjust the existing `docker-compose.yml`)
- [ ] Add a **Caddy** service (auto-TLS for the domain) in front of `frontend`.
- [ ] Remove the public port mappings on `backend` (`8000`) and `db` (`5432`) — internal only.
- [ ] Set `frontend` to build with `VITE_API_BASE_URL=/api` (already the default).
- [ ] Move all env values into a server-side `.env` file (not committed): strong `POSTGRES_PASSWORD`, `SECRET_KEY` (`openssl rand -hex 32`), `APP_ENV=production`, real `CORS_ORIGINS`/`FRONTEND_URL`/`API_BASE_URL` for the domain, `BUSINESS_UTC_OFFSET=5`.
- [ ] Confirm `APP_ENV=production` (the app refuses to boot on the insecure default SECRET_KEY — verify it starts).

**Data**
- [ ] Run migrations (`alembic upgrade head`) — the backend image/init does this.
- [ ] Seed the admin, then **change that password**.
- [ ] Enter the **real weekly menu**, delivery params, advance %, WhatsApp number and payment account details in Admin → Settings.
- [ ] Confirm the database is otherwise clean (no test orders) — `clean_data.py` if needed (it refuses in production, so run before flipping `APP_ENV`, or temporarily).

**Security**
- [ ] TLS working (https, valid cert, http→https redirect via Caddy).
- [ ] Security headers present (nginx already sends HSTS + CSP).
- [ ] `/orders`, `/reports`, `/payments`, `/settings` require auth; `/health` returns 200.
- [ ] Rate limiting active on `/auth/login` (429 after the cap).
- [ ] No secrets in git; `.env` only on the server.

**Backups**
- [ ] Nightly `pg_dump | gzip` cron (or a small backup container) → off-site bucket.
- [ ] **Do a restore drill**: pull last night's dump into a throwaway DB and confirm it loads. A backup you haven't restored isn't a backup.

**Observability**
- [ ] Error tracking (Sentry free tier) wired into backend + frontend.
- [ ] Uptime monitor hitting `/health` (UptimeRobot / BetterStack).
- [ ] Know how to read logs (`docker compose logs -f`).

**Legal-lite** (you collect customer name/phone/address)
- [ ] A short privacy note + basic terms on the site footer.

---

## 5. Go-live steps (in order)

1. Build & start the stack on the VM: `docker compose up -d --build`.
2. Verify containers healthy; `/health` = 200; site loads over https.
3. Log in as admin, set the menu + settings, place a **test order end-to-end** (order → status → record payment → reconcile), then remove the test order.
4. Verify the first nightly backup lands off-site (or run it manually once).
5. Announce / share the link. Watch logs and error tracking for the first day.

---

## 6. Post-launch & ops

- **Weekly:** check backups are landing; skim error tracker; review reconciliation.
- **Updates:** `git pull` → `docker compose up -d --build` (migrations run on start). Consider a staging copy before updates once there's real data.
- **Owner runbook:** one page on taking orders, updating the menu, and reconciling payments (write this before handoff).

## 7. Rollback

- Keep the previous image/commit. To roll back: `git checkout <prev>` → `docker compose up -d --build`.
- If a migration goes wrong: restore the latest dump into the DB, then redeploy the previous version. (This is why the restore drill matters.)

---

## 8. Rough cost

VM (~$6–12) + object storage for backups (~$1–5) + domain (~$10–15/yr) +
Sentry/uptime free tiers ≈ **under ~$15/month** to run the live business.

---

## 9. Enterprise-client path (for later)

When a client needs HA, scale, or strict isolation, deploy with the `k8s/`
manifests instead: namespace-per-client, secrets, PVC, network policies,
`pg_dump` CronJob, and the client's own `client.config.yaml` as a ConfigMap.
Same app, same images — a different, heavier host.
