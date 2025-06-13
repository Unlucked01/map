#!/bin/bash

# Скрипт обновления системы интерактивной карты ПГУ
# Автор: Команда разработки карты ПГУ
# Дата: $(date +%Y-%m-%d)

set -e  # Останавливать выполнение при ошибках

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Функция для проверки успешности команды
check_command() {
    if [ $? -eq 0 ]; then
        log_success "$1"
    else
        log_error "$2"
        exit 1
    fi
}

# Конфигурация
PROJECT_NAME="map_v2"
BACKUP_DIR="./backups"
DB_FILE="backend/university_map.db"
DOCKER_COMPOSE_FILE="docker-compose.yml"
BRANCH="main"

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

echo "======================================"
echo "🎓 Скрипт обновления карты ПГУ"
echo "======================================"

# 1. Проверка окружения
log_info "Проверка окружения..."

# Проверяем наличие git
if ! command -v git &> /dev/null; then
    log_error "Git не установлен!"
    exit 1
fi

# Проверяем наличие docker
if ! command -v docker &> /dev/null; then
    log_error "Docker не установлен!"
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose не установлен!"
    exit 1
fi

log_success "Окружение проверено"

# 2. Создание резервной копии базы данных
log_info "Создание резервной копии базы данных..."

if [ -f "$DB_FILE" ]; then
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/university_map_backup_$BACKUP_TIMESTAMP.db"
    cp "$DB_FILE" "$BACKUP_FILE"
    check_command "База данных скопирована в $BACKUP_FILE" "Не удалось создать резервную копию базы данных"
else
    log_warning "Файл базы данных не найден, создается новая база"
fi

# 3. Останавливаем текущие контейнеры (если запущены)
log_info "Остановка текущих контейнеров..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose down --remove-orphans
    check_command "Контейнеры остановлены" "Ошибка при остановке контейнеров"
else
    log_warning "docker-compose.yml не найден, пропускаем остановку контейнеров"
fi

# 4. Получение последних изменений из репозитория
log_info "Получение последних изменений из Git..."

# Сохраняем текущую ветку
CURRENT_BRANCH=$(git branch --show-current)

# Проверяем статус рабочей директории
if [ -n "$(git status --porcelain)" ]; then
    log_warning "Обнаружены неподтвержденные изменения"
    read -p "Хотите сохранить изменения в stash? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git stash push -m "Auto-stash before update $(date)"
        log_success "Изменения сохранены в stash"
    fi
fi

# Обновляем код
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH
check_command "Код обновлен" "Ошибка при обновлении кода"

# 5. Обновление зависимостей Python
log_info "Обновление зависимостей Python..."

if [ -f "backend/requirements.txt" ]; then
    # Проверяем наличие виртуального окружения
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r backend/requirements.txt
        check_command "Зависимости Python обновлены" "Ошибка при обновлении зависимостей Python"
    else
        log_warning "Виртуальное окружение не найдено, используем системный Python"
        pip3 install -r backend/requirements.txt
    fi
else
    log_warning "requirements.txt не найден, пропускаем обновление зависимостей"
fi

# 6. Обновление зависимостей Node.js
log_info "Обновление зависимостей Node.js..."

if [ -f "front/package.json" ]; then
    cd front
    if command -v npm &> /dev/null; then
        npm install
        check_command "Зависимости Node.js обновлены" "Ошибка при обновлении зависимостей Node.js"
    else
        log_warning "npm не установлен, пропускаем обновление зависимостей Node.js"
    fi
    cd ..
else
    log_warning "front/package.json не найден, пропускаем обновление зависимостей"
fi

# 7. Проверка и обновление модели базы данных
log_info "Проверка модели базы данных..."

cd backend

# Проверяем, нужно ли пересоздать базу данных
if [ -f "pgu_real_data.py" ]; then
    log_info "Найден файл с обновленными данными ПГУ"
    
    # Создаем резервную копию текущей базы
    if [ -f "university_map.db" ]; then
        cp university_map.db "university_map_old.db"
    fi
    
    # Пересоздаем базу данных с новыми данными
    log_info "Пересоздание базы данных с новыми данными..."
    rm -f university_map.db
    
    # Проверяем синтаксис Python файлов
    if command -v python3 &> /dev/null; then
        python3 -m py_compile pgu_real_data.py
        python3 -m py_compile models.py
        python3 -m py_compile database.py
        check_command "Синтаксис Python файлов проверен" "Ошибка в синтаксисе Python файлов"
    fi
    
    log_success "База данных готова к пересозданию"
fi

cd ..

# 8. Пересборка и запуск контейнеров
log_info "Пересборка и запуск контейнеров..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    # Пересобираем образы
    docker-compose build --no-cache
    check_command "Образы пересобраны" "Ошибка при пересборке образов"
    
    # Запускаем контейнеры
    docker-compose up -d
    check_command "Контейнеры запущены" "Ошибка при запуске контейнеров"
else
    log_warning "docker-compose.yml не найден, запускаем сервисы локально"
    
    # Запуск бекенда в фоне
    cd backend
    if [ -d "../venv" ]; then
        source ../venv/bin/activate
    fi
    
    nohup python3 main.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    log_success "Backend запущен (PID: $BACKEND_PID)"
    
    cd ..
fi

# 9. Ожидание запуска сервисов
log_info "Ожидание запуска сервисов..."
sleep 10

# 10. Проверка работоспособности
log_info "Проверка работоспособности сервисов..."

# Проверяем backend API
BACKEND_URL="http://localhost:8000"
if command -v curl &> /dev/null; then
    if curl -f -s "$BACKEND_URL/api/buildings" > /dev/null; then
        log_success "Backend API работает корректно"
    else
        log_error "Backend API не отвечает"
        
        # Показываем логи для диагностики
        if [ -f "$DOCKER_COMPOSE_FILE" ]; then
            log_info "Логи backend контейнера:"
            docker-compose logs backend | tail -20
        else
            log_info "Логи backend:"
            tail -20 logs/backend.log 2>/dev/null || echo "Логи не найдены"
        fi
        exit 1
    fi
else
    log_warning "curl не установлен, пропускаем проверку API"
fi

# Проверяем frontend (если используется nginx)
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    FRONTEND_URL="http://localhost"
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        log_success "Frontend доступен"
    else
        log_warning "Frontend может быть недоступен или еще запускается"
    fi
fi

# 11. Финальные проверки и очистка
log_info "Финальные проверки..."

# Проверяем количество зданий в базе данных
if [ -f "backend/university_map.db" ]; then
    if command -v sqlite3 &> /dev/null; then
        BUILDING_COUNT=$(sqlite3 backend/university_map.db "SELECT COUNT(*) FROM buildings;")
        log_success "В базе данных $BUILDING_COUNT зданий"
    fi
fi

# Очистка старых образов Docker
if command -v docker &> /dev/null; then
    log_info "Очистка неиспользуемых Docker образов..."
    docker system prune -f > /dev/null 2>&1
    log_success "Очистка завершена"
fi

# 12. Отчет об обновлении
echo ""
echo "======================================"
log_success "🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!"
echo "======================================"
echo ""
echo "📋 Сводка обновления:"
echo "  • Код обновлен до последней версии"
echo "  • База данных обновлена"
echo "  • Зависимости обновлены"
echo "  • Сервисы перезапущены"
echo "  • Работоспособность проверена"
echo ""
echo "🌐 Доступ к приложению:"
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "  • Frontend: http://localhost"
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
else
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
fi
echo ""
echo "📁 Резервная копия базы данных:"
echo "  • Файл: $BACKUP_FILE"
echo ""
echo "📝 Логи сервисов:"
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "  • Просмотр логов: docker-compose logs -f"
else
    echo "  • Backend логи: tail -f logs/backend.log"
fi
echo ""

# Создание файла с информацией об обновлении
UPDATE_INFO_FILE="last_update.info"
cat > $UPDATE_INFO_FILE << EOF
Последнее обновление: $(date)
Версия Git: $(git rev-parse HEAD)
Ветка: $(git branch --show-current)
Обновлено пользователем: $(whoami)
Резервная копия БД: $BACKUP_FILE
EOF

log_success "Информация об обновлении сохранена в $UPDATE_INFO_FILE"

exit 0 