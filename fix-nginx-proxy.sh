#!/bin/bash

# Скрипт для исправления nginx proxy конфигурации
set -e

echo "🔧 Исправляем конфигурацию nginx proxy для API..."

# Создаем резервную копию
echo "📋 Создаем резервную копию конфигурации..."
cp nginx/conf.d/unl-map.conf nginx/conf.d/unl-map.conf.backup.$(date +%Y%m%d_%H%M%S)

# Исправляем proxy_pass - убираем слеш в конце
echo "⚡ Исправляем proxy_pass для сохранения /api/ префикса..."
sed -i 's|proxy_pass http://backend/;|proxy_pass http://backend;|g' nginx/conf.d/unl-map.conf

# Проверяем изменения
echo "🔍 Проверяем изменения:"
grep -A5 -B5 "proxy_pass http://backend" nginx/conf.d/unl-map.conf

# Перезапускаем nginx
echo "🔄 Перезапускаем nginx..."
docker-compose -f docker-compose.prod.yml restart nginx

# Ждем перезапуска
echo "⏳ Ждем перезапуска nginx..."
sleep 10

# Проверяем доступность API
echo "🌐 Проверяем API после исправления..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://unl-map.duckdns.org/api/buildings || echo "000")

echo "API статус: $API_STATUS"

if [ "$API_STATUS" == "200" ]; then
    echo "✅ API работает корректно!"
else
    echo "❌ API все еще недоступен"
    echo "📋 Логи nginx:"
    docker-compose -f docker-compose.prod.yml logs nginx | tail -10
    echo "📋 Логи backend:"
    docker-compose -f docker-compose.prod.yml logs backend | tail -10
fi

echo "🎉 Готово!" 