import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from models import Building

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "university_map.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_initial_data()
    
    def get_connection(self):
        """Получение соединения с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для получения данных как dict
        return conn
    
    def init_database(self):
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS buildings (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    coordinates TEXT,  -- JSON строка
                    floor_count INTEGER,
                    year_built INTEGER,
                    departments TEXT,  -- JSON строка
                    amenities TEXT     -- JSON строка
                )
            """)
            conn.commit()
            logger.info("База данных инициализирована")
    
    def populate_initial_data(self):
        """Заполнение начальными данными"""
        # Проверяем, есть ли уже данные
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM buildings")
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info(f"База уже содержит {count} зданий")
                return
        
        # Тестовые данные зданий ПГУ
        initial_buildings = [
            {
                "id": "1",
                "name": "Главный корпус",
                "type": "academic",
                "description": "Главный учебный корпус университета с административными службами",
                "image_url": "/images/main-building.jpg",
                "coordinates": {"x": 100, "y": 150},
                "floor_count": 4,
                "year_built": 1916,
                "departments": ["Ректорат", "Приемная комиссия", "Деканаты"],
                "amenities": ["Wi-Fi", "Кафе", "Банкомат", "Медпункт", "Библиотека"]
            },
            {
                "id": "3",
                "name": "Корпус 3", 
                "type": "academic",
                "description": "Учебный корпус с аудиториями и лабораториями",
                "image_url": "/images/building-3.jpg",
                "coordinates": {"x": 150, "y": 200},
                "floor_count": 4,
                "year_built": 1975,
                "departments": ["Физический факультет", "Математический факультет"],
                "amenities": ["Лаборатории", "Компьютерные классы", "Wi-Fi"]
            },
            {
                "id": "4",
                "name": "Корпус 4",
                "type": "academic", 
                "description": "Современный учебный корпус",
                "coordinates": {"x": 180, "y": 120},
                "floor_count": 5,
                "year_built": 1985,
                "departments": ["Химический факультет", "Биологический факультет"],
                "amenities": ["Лаборатории", "Аудитории", "Библиотека"]
            },
            {
                "id": "6",
                "name": "Корпус 6",
                "type": "academic",
                "description": "Гуманитарный корпус",
                "coordinates": {"x": 220, "y": 180},
                "floor_count": 3,
                "year_built": 1980,
                "departments": ["Филологический факультет", "Исторический факультет"],
                "amenities": ["Аудитории", "Конференц-залы", "Wi-Fi"]
            },
            {
                "id": "7",
                "name": "Корпус 7",
                "type": "academic",
                "description": "Корпус экономического факультета",
                "coordinates": {"x": 250, "y": 140},
                "floor_count": 4,
                "year_built": 1990,
                "departments": ["Экономический факультет", "Юридический факультет"],
                "amenities": ["Аудитории", "Компьютерные классы", "Мультимедиа"]
            },
            {
                "id": "8", 
                "name": "Корпус 8",
                "type": "academic",
                "description": "Новый учебный корпус",
                "coordinates": {"x": 280, "y": 200},
                "floor_count": 6,
                "year_built": 2005,
                "departments": ["IT факультет", "Инженерный факультет"],
                "amenities": ["Современные аудитории", "IT лаборатории", "Коворкинг"]
            },
            {
                "id": "О-1",
                "name": "Общежитие №1",
                "type": "living",
                "description": "Студенческое общежитие для первокурсников",
                "coordinates": {"x": 300, "y": 250},
                "floor_count": 9,
                "year_built": 1970,
                "amenities": ["Прачечная", "Кухня", "Комната отдыха", "Интернет", "Охрана"]
            },
            {
                "id": "О-2",
                "name": "Общежитие №2", 
                "type": "living",
                "description": "Общежитие для студентов старших курсов",
                "coordinates": {"x": 320, "y": 280},
                "floor_count": 9,
                "year_built": 1975,
                "amenities": ["Прачечная", "Кухня", "Спортзал", "Интернет"]
            },
            {
                "id": "О-4",
                "name": "Общежитие №4",
                "type": "living", 
                "description": "Общежитие семейного типа",
                "coordinates": {"x": 340, "y": 260},
                "floor_count": 5,
                "year_built": 1985,
                "amenities": ["Детская площадка", "Прачечная", "Кухня", "Парковка"]
            },
            {
                "id": "О-5",
                "name": "Общежитие №5",
                "type": "living",
                "description": "Современное общежитие",
                "coordinates": {"x": 360, "y": 240},
                "floor_count": 12,
                "year_built": 2000,
                "amenities": ["Фитнес-зал", "Кафе", "Прачечная", "Wi-Fi", "Лифты"]
            },
            {
                "id": "C",
                "name": "Стадион",
                "type": "sports", 
                "description": "Университетский стадион для занятий спортом",
                "coordinates": {"x": 50, "y": 300},
                "floor_count": 1,
                "year_built": 1965,
                "amenities": ["Футбольное поле", "Беговые дорожки", "Трибуны", "Раздевалки"]
            },
            {
                "id": "СК",
                "name": "Спорт Кафедра",
                "type": "academic",
                "description": "Кафедра физической культуры и спорта",
                "coordinates": {"x": 80, "y": 320},
                "floor_count": 2,
                "year_built": 1980,
                "departments": ["Кафедра физической культуры"],
                "amenities": ["Спортзалы", "Тренажеры", "Медкабинет"]
            },
            {
                "id": "D",
                "name": "Столовая",
                "type": "dining",
                "description": "Главная столовая университета",
                "coordinates": {"x": 120, "y": 80},
                "floor_count": 2,
                "year_built": 1960,
                "amenities": ["Горячее питание", "Буфет", "Кафе", "Летняя терраса"]
            }
        ]
        
        # Добавляем данные в базу
        with self.get_connection() as conn:
            for building_data in initial_buildings:
                conn.execute("""
                    INSERT INTO buildings 
                    (id, name, type, description, image_url, coordinates, floor_count, year_built, departments, amenities)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    building_data["id"],
                    building_data["name"],
                    building_data["type"],
                    building_data.get("description"),
                    building_data.get("image_url"),
                    json.dumps(building_data.get("coordinates")) if building_data.get("coordinates") else None,
                    building_data.get("floor_count"),
                    building_data.get("year_built"),
                    json.dumps(building_data.get("departments", [])),
                    json.dumps(building_data.get("amenities", []))
                ))
            conn.commit()
            logger.info(f"Добавлено {len(initial_buildings)} зданий в базу данных")
    
    def get_all_buildings(self, 
                         query: Optional[str] = None,
                         building_type: Optional[str] = None,
                         page: int = 1,
                         limit: int = 50) -> List[Building]:
        """Получение всех зданий с фильтрацией"""
        
        sql = "SELECT * FROM buildings WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            like_query = f"%{query}%"
            params.extend([like_query, like_query])
        
        if building_type:
            sql += " AND type = ?"
            params.append(building_type)
        
        # Пагинация
        offset = (page - 1) * limit
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            buildings = []
            for row in rows:
                building_data = dict(row)
                
                # Парсим JSON поля
                if building_data["coordinates"]:
                    building_data["coordinates"] = json.loads(building_data["coordinates"])
                if building_data["departments"]:
                    building_data["departments"] = json.loads(building_data["departments"])
                if building_data["amenities"]:
                    building_data["amenities"] = json.loads(building_data["amenities"])
                
                buildings.append(Building(**building_data))
            
            return buildings
    
    def get_building_by_id(self, building_id: str) -> Optional[Building]:
        """Получение здания по ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM buildings WHERE id = ?", (building_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            building_data = dict(row)
            
            # Парсим JSON поля
            if building_data["coordinates"]:
                building_data["coordinates"] = json.loads(building_data["coordinates"])
            if building_data["departments"]:
                building_data["departments"] = json.loads(building_data["departments"])
            if building_data["amenities"]:
                building_data["amenities"] = json.loads(building_data["amenities"])
            
            return Building(**building_data)
    
    def get_building_types(self) -> List[Dict[str, Any]]:
        """Получение типов зданий со статистикой"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT type, COUNT(*) as count 
                FROM buildings 
                GROUP BY type 
                ORDER BY count DESC
            """)
            
            type_labels = {
                "academic": "Учебные",
                "living": "Общежития", 
                "sports": "Спортивные",
                "dining": "Питание",
                "administrative": "Административные",
                "other": "Другое"
            }
            
            return [
                {
                    "type": row["type"],
                    "label": type_labels.get(row["type"], row["type"].title()),
                    "count": row["count"]
                }
                for row in cursor.fetchall()
            ]
    
    def get_total_count(self, 
                       query: Optional[str] = None,
                       building_type: Optional[str] = None) -> int:
        """Получение общего количества зданий с учетом фильтров"""
        sql = "SELECT COUNT(*) FROM buildings WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            like_query = f"%{query}%"
            params.extend([like_query, like_query])
        
        if building_type:
            sql += " AND type = ?"
            params.append(building_type)
        
        with self.get_connection() as conn:
            cursor = conn.execute(sql, params)
            return cursor.fetchone()[0]

# Глобальный экземпляр базы данных
db = Database() 