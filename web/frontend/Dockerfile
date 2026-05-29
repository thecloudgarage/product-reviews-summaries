# Frontend is built entirely inside Docker, so Node/npm are NOT required locally.
FROM node:20-alpine AS build
WORKDIR /app

COPY web/frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY web/frontend/index.html ./index.html
COPY web/frontend/vite.config.js ./vite.config.js
COPY web/frontend/src ./src

ENV CI=true
RUN npm run build

FROM nginx:1.27-alpine
COPY web/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
