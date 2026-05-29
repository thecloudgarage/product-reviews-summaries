# Frontend is built entirely inside Docker, so Node/npm are NOT required locally.
FROM node:20-alpine AS build
WORKDIR /app

COPY web/frontend/package.json /app/package.json
COPY web/frontend/vite.config.js /app/vite.config.js
COPY web/frontend/index.html /app/index.html
COPY web/frontend/src /app/src

RUN npm install
RUN npm run build

FROM nginx:1.27-alpine
COPY web/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
