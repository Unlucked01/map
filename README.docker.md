# 🐳 Docker Setup для ПГУ Интерактивная Карта

## Быстрый старт

### Продакшн

```bash
# Собрать и запустить
make install

# Или вручную
docker-compose build
docker-compose up -d
```

Приложение будет доступно по адресу: http://localhost

### Разработка

```bash
# Запустить в режиме разработки
make dev

# Или вручную
docker-compose -f docker-compose.dev.yml up
```

- Frontend (Vue.js): http://localhost:5173
- Backend (FastAPI): http://localhost:8000
- API документация: http://localhost:8000/docs

## Структура

```
├── docker-compose.yml          # Продакшн конфигурация
├── docker-compose.dev.yml      # Разработка конфигурация
├── Makefile                    # Удобные команды
├── front/
│   ├── Dockerfile             # Frontend контейнер
│   ├── nginx.conf             # Nginx конфигурация
│   └── .dockerignore          # Исключения для Docker
└── backend/
    ├── Dockerfile             # Backend контейнер
    └── .dockerignore          # Исключения для Docker
```

## Команды

### Основные команды

```bash
make help          # Показать все доступные команды
make build         # Собрать образы
make up            # Запустить в продакшене
make down          # Остановить
make restart       # Перезапустить
make logs          # Показать логи
```

### Разработка

```bash
make dev           # Запустить разработку (с логами)
make dev-up        # Запустить разработку в фоне
make dev-down      # Остановить разработку
make dev-logs      # Показать логи разработки
```

### Очистка

```bash
make clean         # Очистить неиспользуемые образы
make clean-all     # Полная очистка (включая volumes)
```

## Сервисы

### Frontend (Nginx + Vue.js)
- **Порт**: 80 (продакшн) / 5173 (разработка)
- **Технологии**: Vue.js 3, TypeScript, Tailwind CSS
- **Особенности**: 
  - Hot reload в разработке
  - Gzip сжатие в продакшне
  - Проксирование API на backend
  - SPA роутинг

### Backend (FastAPI)
- **Порт**: 8000
- **Технологии**: FastAPI, SQLite, SQLAlchemy
- **Особенности**:
  - Auto-reload в разработке
  - Health checks
  - Persistent storage для БД

## Volumes

- `backend_data` - Данные SQLite базы
- `backend_dev_data` - Данные для разработки

## Сети

- `pgu-network` - Продакшн сеть
- `pgu-dev-network` - Разработка сеть

## Health Checks

Контейнеры включают health checks:

```bash
# Проверить состояние
docker-compose ps

# Детальная информация о health
docker inspect pgu-map-backend | grep -A 5 Health
```

## Логи

```bash
# Все логи
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend

# С ограничением количества строк
docker-compose logs --tail=100 backend
```

## Отладка

### Подключение к контейнеру

```bash
# Backend
docker exec -it pgu-map-backend bash

# Frontend (для разработки)
docker exec -it pgu-map-frontend-dev sh
```

### Просмотр файлов

```bash
# Список файлов в backend
docker exec pgu-map-backend ls -la /app

# Содержимое nginx конфига
docker exec pgu-map-frontend cat /etc/nginx/conf.d/default.conf
```

## Troubleshooting

### Порты заняты

```bash
# Найти процесс на порту 80
sudo lsof -i :80

# Остановить и очистить все
make clean-all
```

### Проблемы с permissions

```bash
# Исправить права на файлы
sudo chown -R $USER:$USER .
```

### База данных не работает

```bash
# Проверить volume
docker volume ls
docker volume inspect map_v2_backend_data

# Пересоздать базу
docker-compose down -v
docker-compose up -d
```

### Обновление зависимостей

```bash
# Пересобрать без кэша
docker-compose build --no-cache

# Или для конкретного сервиса
docker-compose build --no-cache backend
```

## Мониторинг

### Ресурсы

```bash
# Использование ресурсов
docker stats

# Размер образов
docker images

# Размер volumes
docker system df
```

### Производительность

- Frontend optimized с Nginx gzip
- Backend с uvicorn в production mode
- SQLite с WAL mode для concurrent access
- Static файлы кэшируются на 1 год

## Backup

### База данных

```bash
# Создать backup
docker exec pgu-map-backend cp /app/data/university_map.db /app/backup.db
docker cp pgu-map-backend:/app/backup.db ./backup-$(date +%Y%m%d).db

# Восстановить backup
docker cp ./backup-20241201.db pgu-map-backend:/app/data/university_map.db
```

## Deployment

### Продакшн сервер

1. Скопировать файлы на сервер
2. Установить Docker и Docker Compose
3. Запустить:

```bash
git clone <repository>
cd map_v2
make install
```

### Environment Variables

Создать `.env` файл для кастомизации:

```env
# Backend
DATABASE_URL=sqlite:///data/university_map.db
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=80
API_URL=http://backend:8000
```

## Security

- Nginx с security headers
- Non-root пользователь в контейнерах  
- Минимальные базовые образы (alpine)
- .dockerignore для исключения чувствительных файлов 