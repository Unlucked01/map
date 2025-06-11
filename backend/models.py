from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class RoomType(str, Enum):
    CLASSROOM = "classroom"
    LAB = "lab"
    OFFICE = "office"
    TOILET = "toilet"
    CAFE = "cafe"
    LIBRARY = "library"
    AUDITORIUM = "auditorium"
    OTHER = "other"

class Room(BaseModel):
    number: str = Field(..., description="Номер аудитории")
    floor: int = Field(..., description="Этаж")
    type: RoomType = Field(..., description="Тип аудитории")
    capacity: Optional[int] = Field(None, description="Вместимость")
    equipment: Optional[List[str]] = Field(default_factory=list, description="Оборудование")
    accessible: bool = Field(False, description="Доступность для маломобильных")

class Building(BaseModel):
    id: str = Field(..., description="Уникальный ID здания")
    name: str = Field(..., description="Название здания")
    type: str = Field(..., description="Тип здания")
    description: Optional[str] = Field(None, description="Описание здания")
    image_url: Optional[str] = Field(None, description="URL изображения")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Координаты на карте")
    floor_count: Optional[int] = Field(None, description="Количество этажей")
    year_built: Optional[int] = Field(None, description="Год постройки")
    departments: Optional[List[str]] = Field(default_factory=list, description="Кафедры и отделы")
    amenities: Optional[List[str]] = Field(default_factory=list, description="Удобства")
    rooms: Optional[List[Room]] = Field(default_factory=list, description="Аудитории")
    accessible: bool = Field(False, description="Доступность для маломобильных")
    has_elevator: bool = Field(False, description="Наличие лифта")
    has_parking: bool = Field(False, description="Наличие парковки")

class SearchResultType(str, Enum):
    BUILDING = "building"
    ROOM = "room"
    AMENITY = "amenity"

class SearchResult(BaseModel):
    type: SearchResultType = Field(..., description="Тип результата поиска")
    building: Building = Field(..., description="Здание")
    room: Optional[Room] = Field(None, description="Аудитория (если поиск по аудитории)")
    amenity: Optional[str] = Field(None, description="Услуга (если поиск по услуге)")
    match_text: str = Field(..., description="Текст совпадения")
    priority: int = Field(..., description="Приоритет для сортировки")

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str

class BuildingResponse(BaseModel):
    buildings: List[Building]
    total: int
    page: int
    limit: int 