FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN printf 'server{\n listen 3000;\n root /usr/share/nginx/html;\n index index.html;\n location / { try_files $uri $uri/ /index.html; }\n gzip on;\n}\n' \
    > /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx","-g","daemon off;"]
