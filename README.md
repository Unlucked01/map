# Интерактивная карта ПГУ

## 📋 Описание проекта

Интерактивная карта **Пензенского государственного университета (ПГУ)** - это современное веб-приложение, которое предоставляет студентам, преподавателям и посетителям удобный способ навигации по территории университета. Проект включает в себя детальную информацию о корпусах, институтах, аудиториях и других объектах инфраструктуры ПГУ.

## 🎯 Основные возможности

- **Интерактивная карта** с масштабированием и панорамированием
- **Поиск зданий** по названию и типу
- **Детальная информация** о каждом корпусе (аудитории, этажи, оборудование)
- **Фильтрация** по типу зданий (учебные, жилые, спортивные, административные)
- **Адаптивный дизайн** для мобильных устройств
- **Быстрый поиск** аудиторий и помещений
- **Информация о доступности** для людей с ограниченными возможностями

## 🏛️ Структура ПГУ в системе

Система содержит информацию о реальных корпусах ПГУ:

### Институты и факультеты:
- **Главный корпус** (ул. Красная, 40) - административные службы
- **Политехнический институт** - IT, вычислительная техника, электроника
- **Медицинский институт** - лечебный факультет, стоматология
- **Педагогический институт им. В.Г. Белинского** - история, филология, педагогика
- **Юридический институт** - правовые дисциплины
- **Институт экономики и управления** - экономика, менеджмент
- **Институт физической культуры и спорта** - спортивные дисциплины

### Инфраструктура:
- **Научно-техническая библиотека** - читальные залы и электронные ресурсы
- **Столовая** - питание для студентов и сотрудников
- **Общежития** - проживание для иногородних студентов
- **Военный учебный центр им. В.Ф. Шишкова** - военная подготовка

## 🛠️ Технологический стек

### Frontend
- **Vue.js 3** - прогрессивный JavaScript-фреймворк
- **Vue Router** - маршрутизация в SPA
- **Pinia** - управление состоянием приложения
- **Vite** - быстрый сборщик для разработки
- **Tailwind CSS** - utility-first CSS фреймворк
- **Vite PWA** - поддержка Progressive Web App

### Backend
- **FastAPI** - современный Python веб-фреймворк
- **SQLite** - легковесная реляционная база данных
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - валидация данных и сериализация
- **Uvicorn** - ASGI сервер для продакшена

### DevOps и деплой
- **Docker** - контейнеризация приложения
- **Docker Compose** - оркестрация многоконтейнерного приложения
- **Nginx** - веб-сервер и reverse proxy
- **Let's Encrypt** - SSL сертификаты
- **DuckDNS** - динамический DNS

## 📁 Структура проекта

```
map_v2/
├── front/                      # Frontend приложение (Vue.js)
│   ├── public/                 # Статические файлы
│   │   ├── components/         # Vue компоненты
│   │   │   ├── MapViewer.vue   # Основной компонент карты
│   │   │   ├── BuildingCard.vue # Карточка здания
│   │   │   ├── SearchBar.vue   # Поиск
│   │   │   └── FilterPanel.vue # Фильтры
│   │   ├── stores/             # Pinia stores
│   │   │   └── buildings.ts    # Состояние зданий
│   │   ├── router/             # Vue Router
│   │   └── main.js             # Точка входа
│   ├── package.json            # Зависимости frontend
│   └── vite.config.ts          # Конфигурация Vite
│
├── backend/                    # Backend приложение (FastAPI)
│   ├── main.py                 # Точка входа FastAPI
│   ├── models.py               # SQLAlchemy модели
│   ├── database.py             # Подключение к БД
│   ├── pgu_real_data.py        # Данные ПГУ
│   └── requirements.txt        # Python зависимости
│
├── nginx/                      # Конфигурация Nginx
│   └── conf.d/
│       └── unl-map.conf        # Конфигурация домена
│
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile.backend          # Dockerfile для backend
├── Dockerfile.frontend         # Dockerfile для frontend
└── README.md                   # Документация проекта
```

## 🏗️ Архитектура системы

### Архитектурный паттерн: Трехуровневая архитектура

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Presentation  │────▶│    Business     │────▶│   Data Access   │
│     Layer       │     │     Layer       │     │     Layer       │
│   (Vue.js)      │     │   (FastAPI)     │     │   (SQLite)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Диаграмма компонентов:

```mermaid
graph TD
    A[Frontend Vue.js SPA] --> B[Nginx Reverse Proxy]
    B --> C[FastAPI Backend]
    C --> D[SQLite Database]
    
    E[MapViewer Component] --> F[BuildingCard Component]
    E --> G[SearchBar Component]
    E --> H[FilterPanel Component]
    
    I[Pinia Store] --> J[Buildings State]
    I --> K[Search State]
    
    L[API Routes] --> M[Buildings Controller]
    L --> N[Search Controller]
    
    O[Database Layer] --> P[Models SQLAlchemy]
    O --> Q[Data Access Layer]
    
    A --> E
    A --> I
    C --> L
    C --> O
    
    style A fill:#42b883
    style C fill:#ff6b6b
    style D fill:#4ecdc4
```

### Диаграмма развертывания:

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Frontend Container"
            A[Vue.js App<br/>Port 3000]
            B[Vite Build]
        end
        
        subgraph "Backend Container"
            C[FastAPI App<br/>Port 8000]
            D[Python Runtime]
            E[SQLite Database]
        end
        
        subgraph "Nginx Container"
            F[Nginx Proxy<br/>Port 80/443]
            G[SSL Certificates]
            H[Static Files]
        end
    end
    
    I[Internet] --> F
    F --> A
    F --> C
    C --> E
    
    J[Let's Encrypt] --> G
    K[DuckDNS] --> I
    
    style A fill:#42b883
    style C fill:#ff6b6b
    style E fill:#4ecdc4
    style F fill:#90EE90
```

### Уровни архитектуры:

1. **Presentation Layer (Уровень представления)**
   - Vue.js SPA приложение
   - Интерактивная карта SVG
   - Компоненты пользовательского интерфейса
   - Маршрутизация и навигация

2. **Business Layer (Бизнес-логика)**
   - FastAPI REST API
   - Валидация данных через Pydantic
   - Бизнес-правила и обработка запросов
   - Сериализация/десериализация данных

3. **Data Access Layer (Уровень доступа к данным)**
   - SQLite база данных
   - SQLAlchemy ORM
   - Модели данных зданий и аудиторий

## 🗃️ Модель данных

### Диаграмма классов:

```mermaid
classDiagram
    class Building {
        +String id
        +String name
        +String type
        +String description
        +String image_url
        +Dict coordinates
        +int floor_count
        +int year_built
        +List departments
        +List amenities
        +List rooms
        +boolean accessible
        +boolean has_elevator
        +boolean has_parking
    }
    
    class Room {
        +String number
        +int floor
        +RoomType type
        +int capacity
        +List equipment
        +boolean accessible
    }
    
    class RoomType {
        <<enumeration>>
        CLASSROOM
        LAB
        OFFICE
        TOILET
        CAFE
        LIBRARY
        AUDITORIUM
        ROOM
        OTHER
    }
    
    class DatabaseManager {
        +init_database() void
        +get_all_buildings() List
        +get_building_by_id(id) Building
        +search_buildings(query) List
        +get_suggestions(query) List
    }
    
    class APIController {
        +get_buildings() BuildingResponse
        +get_building_detail(id) Building
        +search_buildings(query) SearchResponse
        +get_suggestions(query) List
    }
    
    Building --> Room
    Room --> RoomType
    APIController --> DatabaseManager
    DatabaseManager --> Building
```

### Диаграмма последовательности (поиск зданий):

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant UI as Vue.js Frontend
    participant Store as Pinia Store
    participant API as FastAPI Backend
    participant DB as SQLite Database
    
    User->>UI: Вводит поисковый запрос
    UI->>Store: updateSearchQuery(query)
    Store->>API: GET /api/search?q=query
    API->>DB: search_buildings(query)
    DB-->>API: List[Building]
    API-->>Store: SearchResponse
    Store-->>UI: Обновляет состояние
    UI-->>User: Отображает результаты поиска
    
    User->>UI: Кликает на здание
    UI->>Store: selectBuilding(buildingId)
    Store->>API: GET /api/buildings/{id}
    API->>DB: get_building_by_id(id)
    DB-->>API: Building with rooms
    API-->>Store: Building details
    Store-->>UI: Обновляет selectedBuilding
    UI-->>User: Показывает детали здания
```

### Основные сущности:

- **Building** - Здание/корпус университета
- **Room** - Аудитория/помещение
- **RoomType** - Тип помещения (enum)

### Атрибуты зданий:
- Базовая информация (название, описание, тип)
- Координаты на карте
- Физические характеристики (этажи, год постройки)
- Департаменты и удобства
- Доступность для людей с ограниченными возможностями

### Атрибуты аудиторий:
- Номер и этаж
- Тип помещения
- Вместимость
- Оборудование
- Доступность

## 🚀 Развертывание

### Разработка (локально)

1. **Клонирование репозитория:**
```bash
git clone https://github.com/your-repo/map_v2.git
cd map_v2
```

2. **Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Frontend:**
```bash
cd front
npm install
npm run dev
```

### Продакшен (Docker)

1. **Сборка и запуск:**
```bash
docker-compose up -d
```

2. **SSL сертификаты:**
```bash
./deploy-ssl-fix.sh
```

## 🔧 API Endpoints

### Buildings
- `GET /api/buildings` - Получить все здания
- `GET /api/buildings/{id}` - Получить здание по ID
- `GET /api/search?q={query}` - Поиск зданий
- `GET /api/suggestions?q={query}` - Автодополнение поиска

### Примеры запросов:

```bash
# Получить все здания
curl http://localhost:8000/api/buildings

# Поиск зданий
curl http://localhost:8000/api/search?q=Политехнический

# Получить конкретное здание
curl http://localhost:8000/api/buildings/1
```

## 📊 Производительность

### Оптимизации:
- **Кэширование** SVG карт в памяти
- **Lazy loading** компонентов Vue
- **Компрессия** статических файлов через Nginx
- **Bundle splitting** для оптимизации загрузки
- **PWA** поддержка для оффлайн использования

### Масштабируемость:
- Контейнеризация через Docker
- Горизонтальное масштабирование через Docker Compose
- Reverse proxy через Nginx
- Кэширование на уровне HTTP

## 🔒 Безопасность

- **HTTPS** через Let's Encrypt
- **CORS** настройки для API
- **Rate limiting** для защиты от DDoS
- **Валидация** входных данных через Pydantic
- **Изоляция** через Docker containers

## 📱 Мобильная адаптация

- **Responsive design** через Tailwind CSS
- **Touch events** для мобильной навигации
- **PWA** для установки на мобильные устройства
- **Оптимизированные** изображения и ресурсы

## 🧪 Тестирование

### Фронтенд:
- **Unit tests** для Vue компонентов
- **Integration tests** для API взаимодействия
- **E2E tests** для пользовательских сценариев

### Бэкенд:
- **Unit tests** для бизнес-логики
- **API tests** для endpoints
- **Database tests** для ORM операций


## 👥 Команда разработки

- **Frontend Developer** - Vue.js, JavaScript, CSS
- **Backend Developer** - Python, FastAPI, SQLite
- **DevOps Engineer** - Docker, Nginx, SSL


##### ER диаграмма базы данных:
```mermaid
erDiagram
    BUILDING {
        string id PK "Уникальный идентификатор здания"
        string name "Название здания"
        string type "Тип здания (academic, living, sports, dining)"
        string description "Описание здания"
        string image_url "URL изображения"
        int x_coordinate "X координата на карте"
        int y_coordinate "Y координата на карте" 
        int floor_count "Количество этажей"
        int year_built "Год постройки"
        string address "Адрес здания"
        json departments "JSON массив департаментов"
        json amenities "JSON массив удобств"
        boolean accessible "Доступность для людей с ограниченными возможностями"
        boolean has_elevator "Наличие лифта"
        boolean has_parking "Наличие парковки"
        datetime created_at "Дата создания записи"
        datetime updated_at "Дата обновления записи"
    }
    
    ROOM {
        int id PK "Уникальный идентификатор аудитории"
        string building_id FK "ID здания"
        string number "Номер аудитории"
        int floor "Этаж"
        string type "Тип помещения (classroom, lab, office, auditorium, etc.)"
        int capacity "Вместимость"
        json equipment "JSON массив оборудования"
        boolean accessible "Доступность для людей с ограниченными возможностями"
        datetime created_at "Дата создания записи"
        datetime updated_at "Дата обновления записи"
    }
    
    ROOM_TYPE {
        string value PK "Значение типа"
        string label "Отображаемое название"
        string description "Описание типа"
    }
    
    DEPARTMENT {
        int id PK "Уникальный идентификатор департамента"
        string name "Название департамента"
        string description "Описание департамента"
        string building_id FK "ID здания"
        string contact_info "Контактная информация"
        datetime created_at "Дата создания записи"
    }
    
    AMENITY {
        int id PK "Уникальный идентификатор удобства"
        string name "Название удобства"
        string description "Описание удобства"
        string icon "Иконка удобства"
        datetime created_at "Дата создания записи"
    }
    
    BUILDING_AMENITY {
        int building_id FK "ID здания"
        int amenity_id FK "ID удобства"
        boolean available "Доступность"
        string notes "Дополнительные заметки"
    }
    
    EQUIPMENT {
        int id PK "Уникальный идентификатор оборудования"
        string name "Название оборудования"
        string category "Категория оборудования"
        string description "Описание оборудования"
        datetime created_at "Дата создания записи"
    }
    
    ROOM_EQUIPMENT {
        int room_id FK "ID аудитории"
        int equipment_id FK "ID оборудования"
        int quantity "Количество"
        string condition "Состояние"
        string notes "Дополнительные заметки"
    }
    
    BUILDING ||--o{ ROOM : "содержит"
    BUILDING ||--o{ DEPARTMENT : "включает"
    BUILDING ||--o{ BUILDING_AMENITY : "имеет"
    ROOM ||--o{ ROOM_EQUIPMENT : "оснащена"
    ROOM_TYPE ||--o{ ROOM : "определяет_тип"
    AMENITY ||--o{ BUILDING_AMENITY : "связано_с"
    EQUIPMENT ||--o{ ROOM_EQUIPMENT : "используется_в"
```

## 📞 Контакты

- **Сайт:** [unl-map.duckdns.org](https://unl-map.duckdns.org)

