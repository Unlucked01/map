#!/bin/bash

# Скрипт для деплоя PGU University Map на сервер
# Использование: ./deploy.sh [your-email@example.com]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Деплой PGU University Map на unl-map.duckdns.org${NC}"

# Проверяем email для Let's Encrypt
EMAIL=${1:-"your-email@example.com"}
if [ "$EMAIL" == "your-email@example.com" ]; then
    echo -e "${YELLOW}⚠️  Используйте: ./deploy.sh your-email@example.com${NC}"
    echo -e "${YELLOW}   Или измените email в docker-compose.prod.yml${NC}"
fi

echo -e "${YELLOW}📧 Email для Let's Encrypt: $EMAIL${NC}"

# Останавливаем существующие контейнеры
echo -e "${YELLOW}🛑 Останавливаем существующие контейнеры...${NC}"
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Собираем новые образы
echo -e "${YELLOW}🔨 Собираем образы...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Обновляем email в docker-compose
if [ "$EMAIL" != "your-email@example.com" ]; then
    sed -i.bak "s/your-email@example.com/$EMAIL/g" docker-compose.prod.yml
fi

# Запускаем сервисы без certbot для первоначальной настройки
echo -e "${YELLOW}🔧 Запускаем сервисы для получения SSL сертификата...${NC}"
docker-compose -f docker-compose.prod.yml up -d nginx frontend backend

# Ждем запуска nginx
echo -e "${YELLOW}⏳ Ждем запуска Nginx...${NC}"
sleep 10

# Получаем SSL сертификат
echo -e "${YELLOW}🔒 Получаем SSL сертификат от Let's Encrypt...${NC}"
docker-compose -f docker-compose.prod.yml run --rm certbot

# Перезапускаем nginx с SSL
echo -e "${YELLOW}🔄 Перезапускаем Nginx с SSL...${NC}"
docker-compose -f docker-compose.prod.yml restart nginx

# Проверяем статус
echo -e "${YELLOW}📊 Проверяем статус сервисов...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Проверяем доступность
echo -e "${YELLOW}🌐 Проверяем доступность сайта...${NC}"
sleep 5

# Тестируем HTTP (должен перенаправить на HTTPS)
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://unl-map.duckdns.org || echo "000")
echo -e "HTTP статус: $HTTP_STATUS"

# Тестируем HTTPS
HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://unl-map.duckdns.org || echo "000")
echo -e "HTTPS статус: $HTTPS_STATUS"

if [ "$HTTPS_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Деплой успешно завершен!${NC}"
    echo -e "${GREEN}🌐 Сайт доступен по адресу: https://unl-map.duckdns.org${NC}"
else
    echo -e "${RED}❌ Возможны проблемы с деплоем${NC}"
    echo -e "${YELLOW}📋 Проверьте логи:${NC}"
    echo -e "   docker-compose -f docker-compose.prod.yml logs nginx"
    echo -e "   docker-compose -f docker-compose.prod.yml logs certbot"
fi

# Показываем полезные команды
echo -e "${YELLOW}📋 Полезные команды:${NC}"
echo -e "   Логи:      docker-compose -f docker-compose.prod.yml logs -f"
echo -e "   Остановка: docker-compose -f docker-compose.prod.yml down"
echo -e "   Перезапуск: docker-compose -f docker-compose.prod.yml restart"
echo -e "   Статус:    docker-compose -f docker-compose.prod.yml ps"

# Создаем cron job для обновления SSL
echo -e "${YELLOW}🔄 Настройка автоматического обновления SSL сертификата...${NC}"
echo -e "Добавьте в crontab (crontab -e):"
echo -e "0 0 1 * * cd $(pwd) && docker-compose -f docker-compose.prod.yml run --rm certbot renew && docker-compose -f docker-compose.prod.yml restart nginx" 