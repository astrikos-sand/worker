FROM nginx:1.27.3-alpine

COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

CMD ["nginx", "-g", "daemon off;"]
