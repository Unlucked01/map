from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import asyncio
from contextlib import asynccontextmanager
import logging

# Импорты новых модулей
from models import Building, BuildingResponse
from controllers import BuildingController
from database import db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Запуск приложения...")
    logger.info(f"База данных инициализирована с {db.get_total_count()} зданиями")
    yield
    # Shutdown
    logger.info("Завершение приложения...")

# Инициализация FastAPI
app = FastAPI(
    title="University Map API",
    description="API для интерактивной карты Пермского государственного университета",
    version="2.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Ответ: {response.status_code}")
    return response

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Главная страница API"""
    return {
        "message": "University Map API v2.0", 
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Проверка здоровья API"""
    buildings_count = db.get_total_count()
    return {"status": "healthy", "buildings_count": str(buildings_count)}

@app.get("/api/buildings", response_model=List[Building])
async def get_buildings(
    query: Optional[str] = Query(None, description="Поисковый запрос по названию"),
    type: Optional[str] = Query(None, description="Фильтр по типу здания"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(50, ge=1, le=100, description="Количество результатов на странице")
):
    """
    Получение списка зданий университета
    
    - **query**: Поиск по названию или описанию здания
    - **type**: Фильтр по типу здания (academic, living, sports, dining, administrative)
    - **page**: Номер страницы для пагинации
    - **limit**: Количество результатов на странице (максимум 100)
    """
    return await BuildingController.get_buildings(query, type, page, limit)

@app.get("/api/buildings/paginated", response_model=BuildingResponse)
async def get_buildings_paginated(
    query: Optional[str] = Query(None, description="Поисковый запрос по названию"),
    type: Optional[str] = Query(None, description="Фильтр по типу здания"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(50, ge=1, le=100, description="Количество результатов на странице")
):
    """
    Получение списка зданий с метаинформацией о пагинации
    """
    return await BuildingController.get_buildings_with_pagination(query, type, page, limit)

@app.get("/api/buildings/{building_id}", response_model=Building)
async def get_building(building_id: str):
    """
    Получение детальной информации о здании по ID
    
    - **building_id**: Уникальный идентификатор здания
    """
    return await BuildingController.get_building_by_id(building_id)

@app.get("/api/buildings/types", response_model=List[Dict[str, Any]])
async def get_building_types():
    """
    Получение списка типов зданий со статистикой
    
    Возвращает список всех типов зданий с количеством зданий каждого типа
    """
    return await BuildingController.get_building_types()

# Обработчики ошибок
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ресурс не найден"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Внутренняя ошибка сервера: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 