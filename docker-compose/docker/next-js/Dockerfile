# syntax=docker/dockerfile:1

# ---- Base: node + pnpm, shared by every stage ----
FROM node:24-alpine AS base
# libc6-compat: native deps (sharp, @swc/core) expect glibc symbols on musl.
RUN apk add --no-cache libc6-compat
# Pin pnpm to the version this repo uses.
RUN corepack enable && corepack prepare pnpm@11.7.0 --activate
# Don't run git hooks during `pnpm install` inside the image.
ENV HUSKY=0
WORKDIR /app

# ---- Dependencies: cached unless lockfile/manifest changes ----
FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# ---- Builder: produce the standalone output ----
FROM base AS builder
# Server-only vars (API_BASE_URL) are read at runtime, not inlined, so a
# placeholder is enough to satisfy build-time env validation. NEXT_PUBLIC_*
# vars ARE inlined at build, so pass the real value for production builds.
ARG API_BASE_URL=http://build.invalid
ARG NEXT_PUBLIC_APP_URL=http://localhost:3000
ENV API_BASE_URL=$API_BASE_URL \
    NEXT_PUBLIC_APP_URL=$NEXT_PUBLIC_APP_URL \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# ---- Runner: minimal image that serves the app ----
FROM base AS runner
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
# Run as an unprivileged user.
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs
# Standalone bundle plus the assets it does not include (static chunks, public/).
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/ >/dev/null 2>&1 || exit 1
CMD ["node", "server.js"]
