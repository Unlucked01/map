#!/bin/bash

# Скрипт для обновления фронтенда с исправленными URL API
set -e

echo "🔄 Обновляем фронтенд с исправленными API URL..."

# Останавливаем контейнеры
echo "🛑 Останавливаем контейнеры..."
docker-compose -f docker-compose.prod.yml down

# Пересобираем только фронтенд
echo "🔨 Пересобираем фронтенд..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Запускаем все сервисы
echo "🚀 Запускаем сервисы..."
docker-compose -f docker-compose.prod.yml up -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 15

# Проверяем доступность
echo "🌐 Проверяем доступность..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://unl-map.duckdns.org || echo "000")
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://unl-map.duckdns.org || echo "000")

echo "HTTP статус: $HTTP_STATUS"
echo "HTTPS статус: $HTTPS_STATUS"

if [ "$HTTPS_STATUS" == "200" ]; then
    echo "✅ Обновление успешно завершено!"
    echo "🌐 Сайт доступен: https://unl-map.duckdns.org"
else
    echo "❌ Проблемы с доступностью"
    echo "📋 Логи последних 10 строк:"
    docker-compose -f docker-compose.prod.yml logs --tail=10
fi

echo "📊 Статус сервисов:"
docker-compose -f docker-compose.prod.yml ps 