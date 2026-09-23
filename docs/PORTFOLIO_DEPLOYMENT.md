# NOW — Portfolio deployment (kind + Kubernetes)

Deploy the current RMS **unchanged** as a containerised app on a local
Kubernetes (`kind`) cluster, then expose it with a Cloudflare quick tunnel for
a live, public walkthrough. The app is not modified for this; only packaging.

> Goal: demonstrate "I can containerise a full-stack management system and run
> it on Kubernetes", with a clean demo database (Mehak's menu + settings +
> admin, **no transactional data**). This is a demo, not a production launch.

---

## What you need (all free, on your machine)

| Tool | Why | Install |
|------|-----|---------|
| Docker Desktop | build images, run the kind node | docker.com |
| kind | the local Kubernetes cluster | `go install` or `choco install kind` / `brew install kind` |
| kubectl | apply manifests, inspect | `choco install kubernetes-cli` / `brew install kubectl` |
| cloudflared | free public tunnel to the demo | `choco install cloudflared` / `brew install cloudflared` |

No container registry, cloud account, or domain is required — kind loads the
images you build locally, and Cloudflare's quick tunnel gives a free public
`https://…trycloudflare.com` URL with TLS at the edge.

---

## Steps

Run from the repo root. (Commands work in PowerShell and bash.)

**1. Build the two images**
```
docker build -t mehak-backend:demo ./backend
docker build -t mehak-frontend:demo ./frontend
```
The frontend build bakes `VITE_API_BASE_URL=/api` by default, so the browser
talks to the frontend only and nginx proxies `/api` to the backend in-cluster.

**2. Create the cluster and load the images into it**
```
kind create cluster --name mehak-demo
kind load docker-image mehak-backend:demo --name mehak-demo
kind load docker-image mehak-frontend:demo --name mehak-demo
```
(Postgres is pulled from Docker Hub by the node automatically. To pre-load it:
`docker pull postgres:16-alpine` then `kind load docker-image postgres:16-alpine --name mehak-demo`.)

**3. Deploy**
```
kubectl apply -f k8s/portfolio-demo.yaml
kubectl -n mehak-demo get pods -w
```
Wait until `database`, `backend` and `frontend` are `Running`/`Ready`. The
backend's init container runs `alembic upgrade head && python seed.py`, so the
DB comes up migrated and seeded (admin + menu + settings) with no orders.

**4. Expose it (two terminals)**
```
# terminal A — forward the frontend service to your machine
kubectl -n mehak-demo port-forward svc/frontend 8080:80

# terminal B — public https URL for the demo
cloudflared tunnel --url http://localhost:8080
```
cloudflared prints a `https://<random>.trycloudflare.com` link — that's your
public demo URL.

**5. Walk through / record** (the tunnel is temporary — record a screen capture
as the durable portfolio artifact):
- Customer site: Home, **Menu** (Mehak's weekly menu shows), add to cart, place an order, order tracking.
- Staff login: `admin / admin123` → Admin console: Dashboard, Orders, **Payments** (record a payment → reconciliation), Reports, Settings, dark-mode toggle; POS and Kitchen.
- Optionally show `kubectl -n mehak-demo get pods,svc` on screen to prove it's really on Kubernetes.

**6. Tear down when done**
```
kind delete cluster --name mehak-demo
```

---

## What is intentionally DEMO-ONLY (documented)

- **Credentials:** `admin / admin123`, and the `SECRET_KEY` / DB password are
  simple values inlined in `k8s/portfolio-demo.yaml`. Fine for a throwaway
  public demo; **never** for production (Phase 2 rotates all of these).
- **Networking:** no Ingress/cert-manager; access is via `port-forward` + a
  Cloudflare quick tunnel. TLS is provided by Cloudflare at the edge.
- **NetworkPolicies omitted:** kind's default CNI doesn't enforce them, so the
  demo leaves them out. The hardened `k8s/production-deployment.yaml` includes
  them for a real cluster.
- **Ephemeral:** a single-node cluster; `kind delete` removes everything,
  including the PVC data. The quick-tunnel URL changes each run and stops when
  cloudflared/your machine stops — it is for a live demo/recording, not 24/7.
- **Payments:** online gateway is off by design; ordering is COD / WhatsApp.

## Want an always-on public link instead?
Use the same images + `k8s/portfolio-demo.yaml` on a free **Oracle Cloud
Always Free** VM running **k3s** (4 ARM cores/24 GB, free forever). You'd then
push the images to a registry (GHCR/Docker Hub) instead of `kind load`, and
expose via k3s's built-in Traefik ingress with a free `nip.io` host. More setup,
but a permanent URL. Ask and I'll write that variant.

## Troubleshooting
- `ErrImageNeverPull` / `ImagePullBackOff` on backend/frontend → the image
  wasn't loaded; re-run the `kind load` step (the manifest uses
  `imagePullPolicy: IfNotPresent`).
- Backend init `CrashLoopBackOff` → check `kubectl -n mehak-demo logs deploy/backend -c migrate-and-seed`; usually the DB isn't ready yet — it retries once the `database` pod is up.
- Blank page → confirm `port-forward` is running and pointing at `svc/frontend`.
