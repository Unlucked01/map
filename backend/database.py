import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from models import Building, Room, RoomType
from pgu_real_data import get_pgu_real_data

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
                    amenities TEXT,    -- JSON строка
                    rooms TEXT,        -- JSON строка для аудиторий
                    accessible BOOLEAN DEFAULT 0,
                    has_elevator BOOLEAN DEFAULT 0,
                    has_parking BOOLEAN DEFAULT 0
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
        
        # Реальные данные ПГУ (Пензенский государственный университет)
        initial_buildings = get_pgu_real_data()
        
        # Добавляем данные в базу
        with self.get_connection() as conn:
            for building_data in initial_buildings:
                conn.execute("""
                    INSERT INTO buildings 
                    (id, name, type, description, image_url, coordinates, floor_count, year_built, departments, amenities, rooms, accessible, has_elevator, has_parking)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(building_data.get("amenities", [])),
                    json.dumps(building_data.get("rooms", [])),
                    building_data.get("accessible", False),
                    building_data.get("has_elevator", False),
                    building_data.get("has_parking", False)
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
                if building_data["rooms"]:
                    rooms_data = json.loads(building_data["rooms"])
                    building_data["rooms"] = [Room(**room) for room in rooms_data]
                else:
                    building_data["rooms"] = []
                
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
            if building_data["rooms"]:
                rooms_data = json.loads(building_data["rooms"])
                building_data["rooms"] = [Room(**room) for room in rooms_data]
            else:
                building_data["rooms"] = []
            
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