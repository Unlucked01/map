.PHONY: help build up down restart logs clean dev dev-up dev-down

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  build     - Собрать все Docker образы"
	@echo "  up        - Запустить приложение в продакшене"
	@echo "  down      - Остановить приложение"
	@echo "  restart   - Перезапустить приложение"
	@echo "  logs      - Показать логи"
	@echo "  clean     - Очистить неиспользуемые образы и контейнеры"
	@echo "  dev       - Запустить в режиме разработки"
	@echo "  dev-down  - Остановить режим разработки"

# Продакшн команды
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

# Разработка
dev:
	docker-compose -f docker-compose.dev.yml up

dev-up:
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Очистка
clean:
	docker system prune -f
	docker image prune -f

clean-all:
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -af
	docker volume prune -f

# ===== ПРОДАКШН ДЕПЛОЙ =====
# Деплой на продакшн сервер
deploy:
	@echo "🚀 Деплой на продакшн сервер..."
	chmod +x deploy.sh
	./deploy.sh

# Продакшн запуск
prod-up:
	@echo "🏭 Запуск продакшн версии..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Продакшн запущен на https://unl-map.duckdns.org"

# Продакшн остановка  
prod-down:
	@echo "🛑 Остановка продакшн версии..."
	docker-compose -f docker-compose.prod.yml down

# Продакшн логи
prod-logs:
	@echo "📋 Логи продакшн версии..."
	docker-compose -f docker-compose.prod.yml logs -f

# Обновление SSL сертификата
renew-ssl:
	@echo "🔒 Обновление SSL сертификата..."
	docker-compose -f docker-compose.prod.yml run --rm certbot renew
	docker-compose -f docker-compose.prod.yml restart nginx
	@echo "✅ SSL сертификат обновлен"

# Быстрые команды
install: build up
dev-install: 
	docker-compose -f docker-compose.dev.yml up --build 