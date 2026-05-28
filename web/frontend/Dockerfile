FROM node:20-alpine AS build
WORKDIR /app
COPY web/frontend/package.json /app/package.json
COPY web/frontend/vite.config.js /app/vite.config.js
COPY web/frontend/index.html /app/index.html
COPY web/frontend/src /app/src
RUN npm install && npm run build

FROM nginx:1.27-alpine
COPY web/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
