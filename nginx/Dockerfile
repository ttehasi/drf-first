# Используем базовый образ nginx
FROM nginx:latest

# Удаляем стандартный конфиг nginx
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш конфигурационный файл в контейнер
COPY nginx.conf /etc/nginx/conf.d/

# Копируем директорию с сертификатами (HTTPS)
# COPY ./certs /etc/ssl/certs

# Указываем рабочую директорию
WORKDIR /etc/nginx

# Открываем порты для взаимодействия
EXPOSE 80