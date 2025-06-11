#!/bin/bash

# Исправленный скрипт для деплоя с правильной настройкой SSL
# Использование: ./deploy-ssl-fix.sh [your-email@example.com]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Деплой PGU University Map с исправленной настройкой SSL${NC}"

# Проверяем email для Let's Encrypt
EMAIL=${1:-"unl-map@ddns.com"}
echo -e "${YELLOW}📧 Email для Let's Encrypt: $EMAIL${NC}"

# Останавливаем существующие контейнеры
echo -e "${YELLOW}🛑 Останавливаем существующие контейнеры...${NC}"
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Собираем новые образы
echo -e "${YELLOW}🔨 Собираем образы...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Этап 1: Запуск с временной HTTP конфигурацией
echo -e "${YELLOW}🔧 Этап 1: Запускаем с временной HTTP конфигурацией...${NC}"

# Сохраняем оригинальную конфигурацию
if [ -f "nginx/conf.d/unl-map.conf" ]; then
    mv nginx/conf.d/unl-map.conf nginx/conf.d/unl-map.conf.backup
fi

# Создаем временную конфигурацию только для HTTP
cat > nginx/conf.d/unl-map.conf << 'EOF'
# Временная конфигурация только для HTTP (для получения SSL сертификата)
server {
    listen 80;
    server_name unl-map.duckdns.org;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files $uri =404;
    }

    # Временно отдаем базовый ответ для всех остальных запросов
    location / {
        return 200 'SSL certificate setup in progress...';
        add_header Content-Type text/plain;
    }
}

# Upstream для внутренних сервисов (пока не используются)
upstream frontend {
    server frontend:80;
    keepalive 32;
}

upstream backend {
    server backend:8000;
    keepalive 32;
}
EOF

# Запускаем сервисы
docker-compose -f docker-compose.prod.yml up -d nginx frontend backend

# Ждем запуска nginx
echo -e "${YELLOW}⏳ Ждем запуска Nginx...${NC}"
sleep 15

# Проверяем доступность HTTP
echo -e "${YELLOW}🌐 Проверяем доступность HTTP...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://unl-map.duckdns.org || echo "000")
echo -e "HTTP статус: $HTTP_STATUS"

if [ "$HTTP_STATUS" != "200" ]; then
    echo -e "${RED}❌ HTTP недоступен, проверьте DNS и доступность сервера${NC}"
    echo -e "${YELLOW}Логи nginx:${NC}"
    docker-compose -f docker-compose.prod.yml logs nginx | tail -10
    exit 1
fi

# Этап 2: Получение SSL сертификата
echo -e "${YELLOW}🔒 Этап 2: Получаем SSL сертификат от Let's Encrypt...${NC}"

# Обновляем email в docker-compose если нужно
if [ "$EMAIL" != "unl-map@ddns.com" ]; then
    sed -i.bak "s/unl-map@ddns.com/$EMAIL/g" docker-compose.prod.yml
fi

# Получаем SSL сертификат
docker-compose -f docker-compose.prod.yml run --rm certbot

# Проверяем что сертификат получен
if docker-compose -f docker-compose.prod.yml exec nginx test -f /etc/letsencrypt/live/unl-map.duckdns.org/fullchain.pem; then
    echo -e "${GREEN}✅ SSL сертификат успешно получен${NC}"
else
    echo -e "${RED}❌ SSL сертификат не был получен${NC}"
    echo -e "${YELLOW}Логи certbot:${NC}"
    docker-compose -f docker-compose.prod.yml logs certbot
    exit 1
fi

# Этап 3: Переключение на полную конфигурацию с SSL
echo -e "${YELLOW}🔄 Этап 3: Переключаемся на полную конфигурацию с SSL...${NC}"

# Восстанавливаем полную конфигурацию
if [ -f "nginx/conf.d/unl-map.conf.backup" ]; then
    mv nginx/conf.d/unl-map.conf.backup nginx/conf.d/unl-map.conf
else
    echo -e "${RED}❌ Файл резервной копии не найден!${NC}"
    exit 1
fi

# Перезапускаем nginx с новой конфигурацией
docker-compose -f docker-compose.prod.yml restart nginx

# Ждем перезапуска
sleep 10

# Проверяем финальную доступность
echo -e "${YELLOW}🌐 Проверяем финальную доступность...${NC}"

# Тестируем HTTP (должен перенаправить на HTTPS)
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://unl-map.duckdns.org || echo "000")
echo -e "HTTP статус: $HTTP_STATUS (ожидается 301)"

# Тестируем HTTPS
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://unl-map.duckdns.org || echo "000")
echo -e "HTTPS статус: $HTTPS_STATUS (ожидается 200)"

if [ "$HTTPS_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Деплой успешно завершен!${NC}"
    echo -e "${GREEN}🌐 Сайт доступен по адресу: https://unl-map.duckdns.org${NC}"
else
    echo -e "${RED}❌ Возможны проблемы с HTTPS${NC}"
    echo -e "${YELLOW}📋 Проверьте логи nginx:${NC}"
    docker-compose -f docker-compose.prod.yml logs nginx | tail -20
fi

# Показываем статус сервисов
echo -e "${YELLOW}📊 Статус сервисов:${NC}"
docker-compose -f docker-compose.prod.yml ps

# Полезные команды
echo -e "${YELLOW}📋 Полезные команды:${NC}"
echo -e "   Логи:      docker-compose -f docker-compose.prod.yml logs -f"
echo -e "   Остановка: docker-compose -f docker-compose.prod.yml down"
echo -e "   Перезапуск: docker-compose -f docker-compose.prod.yml restart"
echo -e "   Статус:    docker-compose -f docker-compose.prod.yml ps"

echo -e "${GREEN}🎉 Готово!${NC}" 