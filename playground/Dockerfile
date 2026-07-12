# syntax=docker/dockerfile:1.6
# =====================================================================
# playground — Next.js standalone runtime.
#
# API_URL is read server-side at REQUEST time (app/api/analyze/route.ts),
# not baked in at build time — safe to point this one image at any
# backend via the container's environment.
# =====================================================================

FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build


FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs \
 && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000 API_URL=http://localhost:8000

CMD ["node", "server.js"]
