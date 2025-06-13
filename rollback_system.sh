#!/bin/bash

# Скрипт восстановления системы карты ПГУ из резервной копии
# Автор: Команда разработки карты ПГУ

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функции для вывода
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

# Конфигурация
BACKUP_DIR="./backups"
DB_FILE="backend/university_map.db"
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo "======================================"
echo "🔄 Скрипт восстановления карты ПГУ"
echo "======================================"

# 1. Поиск доступных резервных копий
log_info "Поиск доступных резервных копий..."

if [ ! -d "$BACKUP_DIR" ]; then
    log_error "Директория резервных копий не найдена: $BACKUP_DIR"
    exit 1
fi

BACKUP_FILES=($(ls -t $BACKUP_DIR/*.db 2>/dev/null))

if [ ${#BACKUP_FILES[@]} -eq 0 ]; then
    log_error "Резервные копии не найдены в $BACKUP_DIR"
    exit 1
fi

# 2. Показываем список доступных копий
echo ""
log_info "Доступные резервные копии:"
for i in "${!BACKUP_FILES[@]}"; do
    BACKUP_FILE="${BACKUP_FILES[$i]}"
    BACKUP_DATE=$(date -r "$BACKUP_FILE" "+%Y-%m-%d %H:%M:%S")
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "  $((i+1)). $(basename "$BACKUP_FILE") - $BACKUP_DATE ($BACKUP_SIZE)"
done

# 3. Выбор резервной копии
echo ""
read -p "Выберите номер резервной копии для восстановления (1-${#BACKUP_FILES[@]}): " CHOICE

if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt ${#BACKUP_FILES[@]} ]; then
    log_error "Неверный выбор"
    exit 1
fi

SELECTED_BACKUP="${BACKUP_FILES[$((CHOICE-1))]}"
log_info "Выбрана резервная копия: $(basename "$SELECTED_BACKUP")"

# 4. Подтверждение
echo ""
log_warning "ВНИМАНИЕ: Эта операция заменит текущую базу данных!"
read -p "Вы уверены, что хотите продолжить? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Операция отменена"
    exit 0
fi

# 5. Остановка сервисов
log_info "Остановка сервисов..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose down
    log_success "Docker контейнеры остановлены"
else
    # Остановка локальных процессов
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_success "Backend процесс остановлен (PID: $BACKEND_PID)"
        fi
        rm -f backend.pid
    fi
fi

# 6. Создание резервной копии текущей базы данных
log_info "Создание резервной копии текущей базы данных..."

if [ -f "$DB_FILE" ]; then
    ROLLBACK_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    ROLLBACK_FILE="$BACKUP_DIR/university_map_before_rollback_$ROLLBACK_TIMESTAMP.db"
    cp "$DB_FILE" "$ROLLBACK_FILE"
    log_success "Текущая база сохранена в $ROLLBACK_FILE"
fi

# 7. Восстановление из резервной копии
log_info "Восстановление базы данных из резервной копии..."

cp "$SELECTED_BACKUP" "$DB_FILE"
log_success "База данных восстановлена из $(basename "$SELECTED_BACKUP")"

# 8. Проверка целостности восстановленной базы данных
log_info "Проверка целостности базы данных..."

if command -v sqlite3 &> /dev/null; then
    # Проверяем, что база данных не повреждена
    if sqlite3 "$DB_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
        log_success "База данных прошла проверку целостности"
    else
        log_error "База данных повреждена!"
        # Восстанавливаем предыдущую версию
        if [ -f "$ROLLBACK_FILE" ]; then
            cp "$ROLLBACK_FILE" "$DB_FILE"
            log_warning "Восстановлена предыдущая версия базы данных"
        fi
        exit 1
    fi
    
    # Показываем статистику
    BUILDING_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM buildings;" 2>/dev/null || echo "0")
    ROOM_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM rooms;" 2>/dev/null || echo "0")
    log_info "Статистика базы данных: $BUILDING_COUNT зданий, $ROOM_COUNT комнат"
else
    log_warning "sqlite3 не установлен, пропускаем проверку целостности"
fi

# 9. Запуск сервисов
log_info "Запуск сервисов..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose up -d
    log_success "Docker контейнеры запущены"
else
    # Запуск локального бекенда
    cd backend
    if [ -d "../venv" ]; then
        source ../venv/bin/activate
    fi
    
    mkdir -p ../logs
    nohup python3 main.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    log_success "Backend запущен (PID: $BACKEND_PID)"
    cd ..
fi

# 10. Ожидание и проверка
log_info "Ожидание запуска сервисов..."
sleep 10

# Проверяем работоспособность API
BACKEND_URL="http://localhost:8000"
if command -v curl &> /dev/null; then
    if curl -f -s "$BACKEND_URL/api/buildings" > /dev/null; then
        log_success "Backend API работает корректно"
    else
        log_error "Backend API не отвечает"
        
        # Показываем логи
        if [ -f "$DOCKER_COMPOSE_FILE" ]; then
            echo "Логи backend:"
            docker-compose logs backend | tail -10
        else
            echo "Логи backend:"
            tail -10 logs/backend.log 2>/dev/null || echo "Логи не найдены"
        fi
        exit 1
    fi
else
    log_warning "curl не установлен, пропускаем проверку API"
fi

# 11. Создание отчета о восстановлении
ROLLBACK_INFO_FILE="last_rollback.info"
cat > $ROLLBACK_INFO_FILE << EOF
Восстановление выполнено: $(date)
Использована резервная копия: $(basename "$SELECTED_BACKUP")
Дата резервной копии: $(date -r "$SELECTED_BACKUP" "+%Y-%m-%d %H:%M:%S")
Предыдущая база сохранена в: $(basename "$ROLLBACK_FILE")
Восстановлено пользователем: $(whoami)
EOF

# 12. Итоговый отчет
echo ""
echo "======================================"
log_success "🎉 ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "======================================"
echo ""
echo "📋 Информация о восстановлении:"
echo "  • Использована копия: $(basename "$SELECTED_BACKUP")"
echo "  • Дата копии: $(date -r "$SELECTED_BACKUP" "+%Y-%m-%d %H:%M:%S")"
echo "  • Предыдущая БД: $(basename "$ROLLBACK_FILE")"
echo "  • Зданий в базе: $BUILDING_COUNT"
echo ""
echo "🌐 Доступ к приложению:"
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "  • Frontend: http://localhost"
    echo "  • Backend API: http://localhost:8000"
else
    echo "  • Backend API: http://localhost:8000"
fi
echo ""
echo "📝 Отчет сохранен в: $ROLLBACK_INFO_FILE"
echo ""

log_success "Система успешно восстановлена!"

exit 0 