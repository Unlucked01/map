"""
Модуль для управления миграциями базы данных карты ПГУ
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Базовый класс для миграций базы данных"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self, cursor: sqlite3.Cursor) -> None:
        """Применить миграцию"""
        raise NotImplementedError
    
    def down(self, cursor: sqlite3.Cursor) -> None:
        """Откатить миграцию"""
        raise NotImplementedError

class Migration001InitialSchema(DatabaseMigration):
    """Начальная схема базы данных"""
    
    def __init__(self):
        super().__init__("001", "Создание начальной схемы базы данных")
    
    def up(self, cursor: sqlite3.Cursor) -> None:
        """Создание таблиц buildings и rooms"""
        
        # Создание таблицы зданий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                description TEXT,
                coordinates_x REAL,
                coordinates_y REAL,
                svg_path TEXT,
                building_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создание таблицы комнат
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                room_number TEXT,
                floor INTEGER,
                room_type TEXT,
                capacity INTEGER,
                description TEXT,
                equipment TEXT,
                responsible_person TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (building_id) REFERENCES buildings (id)
            )
        """)
        
        # Создание индексов
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rooms_building_id ON rooms (building_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rooms_floor ON rooms (floor)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_buildings_type ON buildings (building_type)")
        
        logger.info("Начальная схема базы данных создана")
    
    def down(self, cursor: sqlite3.Cursor) -> None:
        """Удаление таблиц"""
        cursor.execute("DROP TABLE IF EXISTS rooms")
        cursor.execute("DROP TABLE IF EXISTS buildings")
        logger.info("Начальная схема базы данных удалена")

class Migration002AddMigrationTable(DatabaseMigration):
    """Добавление таблицы для отслеживания миграций"""
    
    def __init__(self):
        super().__init__("002", "Добавление таблицы миграций")
    
    def up(self, cursor: sqlite3.Cursor) -> None:
        """Создание таблицы миграций"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Таблица миграций создана")
    
    def down(self, cursor: sqlite3.Cursor) -> None:
        """Удаление таблицы миграций"""
        cursor.execute("DROP TABLE IF EXISTS schema_migrations")
        logger.info("Таблица миграций удалена")

class Migration003AddFullTextSearch(DatabaseMigration):
    """Добавление поддержки полнотекстового поиска"""
    
    def __init__(self):
        super().__init__("003", "Добавление полнотекстового поиска")
    
    def up(self, cursor: sqlite3.Cursor) -> None:
        """Создание FTS индексов"""
        try:
            # Создание FTS индекса для зданий
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS buildings_fts USING fts5(
                    name, address, description, 
                    content='buildings', 
                    content_rowid='id'
                )
            """)
            
            # Создание FTS индекса для комнат
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS rooms_fts USING fts5(
                    name, room_number, description,
                    content='rooms',
                    content_rowid='id'
                )
            """)
            
            # Заполнение FTS индексов существующими данными
            cursor.execute("""
                INSERT INTO buildings_fts(rowid, name, address, description)
                SELECT id, name, address, description FROM buildings
            """)
            
            cursor.execute("""
                INSERT INTO rooms_fts(rowid, name, room_number, description)
                SELECT id, name, room_number, description FROM rooms
            """)
            
            # Создание триггеров для автоматического обновления FTS
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS buildings_ai AFTER INSERT ON buildings BEGIN
                    INSERT INTO buildings_fts(rowid, name, address, description)
                    VALUES (new.id, new.name, new.address, new.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS buildings_ad AFTER DELETE ON buildings BEGIN
                    INSERT INTO buildings_fts(buildings_fts, rowid, name, address, description)
                    VALUES('delete', old.id, old.name, old.address, old.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS buildings_au AFTER UPDATE ON buildings BEGIN
                    INSERT INTO buildings_fts(buildings_fts, rowid, name, address, description)
                    VALUES('delete', old.id, old.name, old.address, old.description);
                    INSERT INTO buildings_fts(rowid, name, address, description)
                    VALUES (new.id, new.name, new.address, new.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS rooms_ai AFTER INSERT ON rooms BEGIN
                    INSERT INTO rooms_fts(rowid, name, room_number, description)
                    VALUES (new.id, new.name, new.room_number, new.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS rooms_ad AFTER DELETE ON rooms BEGIN
                    INSERT INTO rooms_fts(rooms_fts, rowid, name, room_number, description)
                    VALUES('delete', old.id, old.name, old.room_number, old.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS rooms_au AFTER UPDATE ON rooms BEGIN
                    INSERT INTO rooms_fts(rooms_fts, rowid, name, room_number, description)
                    VALUES('delete', old.id, old.name, old.room_number, old.description);
                    INSERT INTO rooms_fts(rowid, name, room_number, description)
                    VALUES (new.id, new.name, new.room_number, new.description);
                END
            """)
            
            logger.info("Полнотекстовый поиск настроен")
            
        except sqlite3.OperationalError as e:
            logger.warning(f"FTS5 недоступен: {e}")
    
    def down(self, cursor: sqlite3.Cursor) -> None:
        """Удаление FTS индексов и триггеров"""
        cursor.execute("DROP TRIGGER IF EXISTS buildings_ai")
        cursor.execute("DROP TRIGGER IF EXISTS buildings_ad")
        cursor.execute("DROP TRIGGER IF EXISTS buildings_au")
        cursor.execute("DROP TRIGGER IF EXISTS rooms_ai")
        cursor.execute("DROP TRIGGER IF EXISTS rooms_ad")
        cursor.execute("DROP TRIGGER IF EXISTS rooms_au")
        cursor.execute("DROP TABLE IF EXISTS buildings_fts")
        cursor.execute("DROP TABLE IF EXISTS rooms_fts")
        logger.info("Полнотекстовый поиск удален")

class MigrationManager:
    """Менеджер миграций базы данных"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations = [
            Migration001InitialSchema(),
            Migration002AddMigrationTable(),
            Migration003AddFullTextSearch(),
        ]
    
    def get_connection(self) -> sqlite3.Connection:
        """Получить соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def get_applied_migrations(self) -> List[str]:
        """Получить список примененных миграций"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
                return [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                # Таблица миграций еще не создана
                return []
    
    def mark_migration_applied(self, migration: DatabaseMigration) -> None:
        """Отметить миграцию как примененную"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO schema_migrations (version, description) VALUES (?, ?)",
                (migration.version, migration.description)
            )
            conn.commit()
    
    def mark_migration_reverted(self, migration: DatabaseMigration) -> None:
        """Удалить запись о примененной миграции"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM schema_migrations WHERE version = ?",
                (migration.version,)
            )
            conn.commit()
    
    def migrate_up(self, target_version: str = None) -> None:
        """Применить миграции"""
        applied = set(self.get_applied_migrations())
        
        for migration in self.migrations:
            if migration.version in applied:
                continue
            
            if target_version and migration.version > target_version:
                break
            
            logger.info(f"Применение миграции {migration.version}: {migration.description}")
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    migration.up(cursor)
                    conn.commit()
                    
                    # Отмечаем миграцию как примененную только после успешного выполнения
                    if migration.version != "002":  # Кроме миграции создания таблицы миграций
                        self.mark_migration_applied(migration)
                    
                    logger.info(f"Миграция {migration.version} применена успешно")
                    
                except Exception as e:
                    logger.error(f"Ошибка при применении миграции {migration.version}: {e}")
                    conn.rollback()
                    raise
        
        # Отмечаем миграцию создания таблицы миграций после всех остальных
        migration_002 = next((m for m in self.migrations if m.version == "002"), None)
        if migration_002:
            self.mark_migration_applied(migration_002)
        
        logger.info("Все миграции применены")
    
    def migrate_down(self, target_version: str) -> None:
        """Откатить миграции до указанной версии"""
        applied = set(self.get_applied_migrations())
        
        # Откатываем в обратном порядке
        for migration in reversed(self.migrations):
            if migration.version not in applied:
                continue
            
            if migration.version <= target_version:
                break
            
            logger.info(f"Откат миграции {migration.version}: {migration.description}")
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    migration.down(cursor)
                    conn.commit()
                    self.mark_migration_reverted(migration)
                    logger.info(f"Миграция {migration.version} откатана успешно")
                    
                except Exception as e:
                    logger.error(f"Ошибка при откате миграции {migration.version}: {e}")
                    conn.rollback()
                    raise
        
        logger.info(f"Откат завершен до версии {target_version}")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Получить статус миграций"""
        applied = set(self.get_applied_migrations())
        
        status = {
            "database_path": self.db_path,
            "database_exists": os.path.exists(self.db_path),
            "migrations": []
        }
        
        for migration in self.migrations:
            status["migrations"].append({
                "version": migration.version,
                "description": migration.description,
                "applied": migration.version in applied
            })
        
        return status
    
    def create_database(self) -> None:
        """Создать новую базу данных с последней схемой"""
        logger.info("Создание новой базы данных")
        self.migrate_up()
        logger.info("База данных создана")

def main():
    """Основная функция для запуска миграций из командной строки"""
    import sys
    
    db_path = "university_map.db"
    manager = MigrationManager(db_path)
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python migrations.py status    - показать статус миграций")
        print("  python migrations.py up        - применить все миграции")
        print("  python migrations.py down <version> - откатить до версии")
        print("  python migrations.py create    - создать новую базу данных")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        status = manager.get_migration_status()
        print(f"База данных: {status['database_path']}")
        print(f"Существует: {status['database_exists']}")
        print("\nМиграции:")
        for migration in status["migrations"]:
            applied = "✓" if migration["applied"] else "✗"
            print(f"  {applied} {migration['version']}: {migration['description']}")
    
    elif command == "up":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        manager.migrate_up(target)
    
    elif command == "down":
        if len(sys.argv) < 3:
            print("Укажите версию для отката")
            return
        target = sys.argv[2]
        manager.migrate_down(target)
    
    elif command == "create":
        manager.create_database()
    
    else:
        print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main() 