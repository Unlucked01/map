from fastapi import HTTPException, Query
from typing import List, Optional, Dict, Any
from models import Building, BuildingResponse
from database import db
import logging

logger = logging.getLogger(__name__)

class BuildingController:
    @staticmethod
    async def get_buildings(
        query: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> List[Building]:
        """Получение списка зданий с фильтрацией и поиском"""
        try:
            logger.info(f"Запрос зданий: query={query}, type={type}, page={page}, limit={limit}")
            
            buildings = db.get_all_buildings(
                query=query,
                building_type=type,
                page=page,
                limit=limit
            )
            
            logger.info(f"Найдено {len(buildings)} зданий")
            return buildings
            
        except Exception as e:
            logger.error(f"Ошибка при получении зданий: {e}")
            raise HTTPException(status_code=500, detail="Ошибка сервера при получении зданий")
    
    @staticmethod
    async def get_building_by_id(building_id: str) -> Building:
        """Получение здания по ID"""
        try:
            logger.info(f"Запрос здания по ID: {building_id}")
            
            building = db.get_building_by_id(building_id)
            
            if not building:
                logger.warning(f"Здание с ID {building_id} не найдено")
                raise HTTPException(status_code=404, detail=f"Здание с ID {building_id} не найдено")
            
            logger.info(f"Найдено здание: {building.name}")
            return building
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при получении здания {building_id}: {e}")
            raise HTTPException(status_code=500, detail="Ошибка сервера при получении здания")
    
    @staticmethod
    async def get_building_types() -> List[Dict[str, Any]]:
        """Получение типов зданий со статистикой"""
        try:
            logger.info("Запрос типов зданий")
            
            types = db.get_building_types()
            
            logger.info(f"Найдено {len(types)} типов зданий")
            return types
            
        except Exception as e:
            logger.error(f"Ошибка при получении типов зданий: {e}")
            raise HTTPException(status_code=500, detail="Ошибка сервера при получении типов зданий")
    
    @staticmethod
    async def get_buildings_with_pagination(
        query: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> BuildingResponse:
        """Получение зданий с пагинацией и метаинформацией"""
        try:
            buildings = await BuildingController.get_buildings(query, type, page, limit)
            total = db.get_total_count(query, type)
            
            return BuildingResponse(
                buildings=buildings,
                total=total,
                page=page,
                limit=limit
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка при получении зданий с пагинацией: {e}")
            raise HTTPException(status_code=500, detail="Ошибка сервера") 