FROM node:22-alpine AS build

WORKDIR /workspace/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
COPY docs/images/ /workspace/docs/images/
RUN npm run build

FROM nginx:1.27-alpine

ENV NGINX_ENVSUBST_FILTER="^(PORT|API_HOSTPORT)$"

COPY frontend/nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /workspace/frontend/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider "http://127.0.0.1:${PORT:-80}/" || exit 1

CMD ["nginx", "-g", "daemon off;"]
