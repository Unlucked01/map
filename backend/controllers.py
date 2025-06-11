from fastapi import HTTPException, Query
from typing import List, Optional, Dict, Any
from models import Building, BuildingResponse, SearchResult, SearchResponse, SearchResultType, Room
from database import db
import logging
import re

logger = logging.getLogger(__name__)

class SearchController:
    @staticmethod
    async def advanced_search(query: str, limit: int = 10) -> SearchResponse:
        """Расширенный поиск по зданиям, аудиториям и услугам"""
        try:
            logger.info(f"Расширенный поиск: query='{query}', limit={limit}")
            
            if not query or len(query.strip()) < 2:
                return SearchResponse(results=[], total=0, query=query)
            
            search_term = query.lower().strip()
            results = []
            
            # Получаем все здания для поиска
            all_buildings = db.get_all_buildings()
            
            for building in all_buildings:
                # Поиск по названию здания
                if search_term in building.name.lower():
                    results.append(SearchResult(
                        type=SearchResultType.BUILDING,
                        building=building,
                        match_text=building.name,
                        priority=1
                    ))
                
                # Поиск по описанию здания
                if building.description and search_term in building.description.lower():
                    results.append(SearchResult(
                        type=SearchResultType.BUILDING,
                        building=building,
                        match_text=building.description,
                        priority=2
                    ))
                
                # Поиск по аудиториям
                if building.rooms:
                    for room in building.rooms:
                        if search_term in room.number.lower():
                            results.append(SearchResult(
                                type=SearchResultType.ROOM,
                                building=building,
                                room=room,
                                match_text=f"Аудитория {room.number}",
                                priority=1
                            ))
                
                # Поиск по услугам/удобствам
                if building.amenities:
                    for amenity in building.amenities:
                        if search_term in amenity.lower():
                            results.append(SearchResult(
                                type=SearchResultType.AMENITY,
                                building=building,
                                amenity=amenity,
                                match_text=amenity,
                                priority=3
                            ))
            
            # Сортировка по приоритету и релевантности
            results.sort(key=lambda x: (x.priority, x.match_text))
            
            # Ограничиваем количество результатов
            results = results[:limit]
            
            logger.info(f"Найдено {len(results)} результатов для запроса '{query}'")
            
            return SearchResponse(
                results=results,
                total=len(results),
                query=query
            )
            
        except Exception as e:
            logger.error(f"Ошибка при расширенном поиске: {e}")
            raise HTTPException(status_code=500, detail="Ошибка сервера при поиске")

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