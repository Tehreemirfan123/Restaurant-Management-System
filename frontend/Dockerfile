# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 — build the static assets with Vite.
# ---------------------------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# The API base URL is baked in at build time. In production it is "/api",
# which the runtime nginx reverse-proxies to the internal backend Service —
# so the browser only ever talks to the frontend origin and the backend
# never needs to be publicly exposed.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2 — serve with the UNPRIVILEGED nginx image.
# nginxinc/nginx-unprivileged runs as a non-root user (uid 101) and listens
# on 8080, so it works cleanly with runAsNonRoot + readOnlyRootFilesystem.
# ---------------------------------------------------------------------------
FROM nginxinc/nginx-unprivileged:1.27-alpine

# Non-secret, non-root config: SPA fallback, /api reverse proxy, security headers.
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Already the default user in this image, but be explicit.
USER 101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
