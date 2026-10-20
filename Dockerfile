FROM node:22-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY backend/requirements.txt backend/
RUN python3 -m venv backend/.venv && backend/.venv/bin/pip install --no-cache-dir -r backend/requirements.txt

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

ENV NODE_ENV=production DJANGO_DEBUG=0
EXPOSE 3000

# Django stays private inside the container, Next.js serves the site and forwards /api to it
CMD backend/.venv/bin/gunicorn --chdir backend config.wsgi -b 127.0.0.1:8000 --workers 2 --timeout 90 & \
    npx next start -p ${PORT:-3000}
