from pydantic import BaseModel, Field
from typing import List, Optional, Dict

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

class BuildingResponse(BaseModel):
    buildings: List[Building]
    total: int
    page: int
    limit: int 