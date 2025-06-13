# Этап 1: Сборка приложения
FROM node:18-alpine AS build

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY package*.json ./

# Полная переустановка зависимостей (решение проблемы с rollup)
RUN rm -rf node_modules package-lock.json && \
    npm install --production=false && \
    npm cache clean --force

# Копирование исходного кода
COPY . .

# Сборка приложения для продакшена (быстрая сборка без проверки типов)
RUN npm run build-fast

# Этап 2: Настройка Nginx для раздачи статики
FROM nginx:alpine AS production

# Копирование собранного приложения
COPY --from=build /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открытие порта
EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"] 