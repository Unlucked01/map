# Реальные данные ПГУ (Пензенский государственный университет) 
# Основано на информации с официального сайта и структуре университета

def get_pgu_real_data():
    return [
        # ГЛАВНЫЙ КОРПУС - ул. Красная, 40
        {
            "id": "1",
            "name": "Главный корпус",
            "type": "academic",
            "description": "Главный корпус ПГУ на улице Красная с административными службами и институтами",
            "image_url": "/images/main-building.jpg",
            "coordinates": {"x": 100, "y": 150},
            "floor_count": 5,
            "year_built": 1943,
            "address": "ул. Красная, 40",
            "departments": ["Ректорат", "Административные службы", "Педагогический институт им. В.Г. Белинского", "Деканаты"],
            "amenities": ["Wi-Fi", "Библиотека", "Медпункт", "Буфет", "Актовый зал", "Конференц-залы"],
            "accessible": True,
            "has_elevator": True,
            "has_parking": True,
            "rooms": [
                # 1 этаж - административные службы
                {"number": "101", "floor": 1, "type": "office", "capacity": 15, "equipment": ["Приемная ректора", "Компьютеры"], "accessible": True},
                {"number": "102", "floor": 1, "type": "office", "capacity": 10, "equipment": ["Деканат", "Принтер"], "accessible": True},
                {"number": "103", "floor": 1, "type": "office", "capacity": 8, "equipment": ["Отдел кадров", "Сейф"], "accessible": True},
                {"number": "110", "floor": 1, "type": "toilet", "capacity": 0, "equipment": ["Раковины", "Зеркала"], "accessible": True},
                
                # 2 этаж - учебные аудитории
                {"number": "201", "floor": 2, "type": "auditorium", "capacity": 150, "equipment": ["Микрофоны", "Проектор", "Звуковая система"], "accessible": True},
                {"number": "202", "floor": 2, "type": "classroom", "capacity": 40, "equipment": ["Интерактивная доска", "Проектор"], "accessible": True},
                {"number": "203", "floor": 2, "type": "classroom", "capacity": 35, "equipment": ["Доска", "Компьютер"], "accessible": True},
                
                # 3 этаж - библиотека и учебные помещения
                {"number": "301", "floor": 3, "type": "library", "capacity": 100, "equipment": ["Каталоги", "Компьютеры", "Wi-Fi"], "accessible": True},
                {"number": "302", "floor": 3, "type": "classroom", "capacity": 30, "equipment": ["Проектор", "Доска"], "accessible": True},
                
                # 4-5 этажи - факультеты
                {"number": "401", "floor": 4, "type": "office", "capacity": 12, "equipment": ["Кафедра", "Компьютеры"], "accessible": False},
                {"number": "501", "floor": 5, "type": "classroom", "capacity": 25, "equipment": ["Семинарская", "Доска"], "accessible": False}
            ]
        },
        
        # ПОЛИТЕХНИЧЕСКИЙ ИНСТИТУТ
        {
            "id": "2",
            "name": "Политехнический институт",
            "type": "academic",
            "description": "Корпус Политехнического института с факультетами вычислительной техники, IT и электроники",
            "coordinates": {"x": 150, "y": 200},
            "floor_count": 4,
            "year_built": 1970,
            "departments": ["Факультет вычислительной техники", "Факультет информационных технологий и электроники", "Факультет промышленных технологий"],
            "amenities": ["Компьютерные классы", "Лаборатории", "IT-центр", "Wi-Fi", "Принтер"],
            "accessible": True,
            "has_elevator": True,
            "has_parking": True,
            "rooms": [
                {"number": "101", "floor": 1, "type": "lab", "capacity": 25, "equipment": ["Новые компьютеры", "Программирование"], "accessible": True},
                {"number": "102", "floor": 1, "type": "lab", "capacity": 20, "equipment": ["Электронные схемы", "Осциллографы"], "accessible": True},
                {"number": "201", "floor": 2, "type": "classroom", "capacity": 35, "equipment": ["Проектор", "Интерактивная доска"], "accessible": True},
                {"number": "202", "floor": 2, "type": "lab", "capacity": 30, "equipment": ["Компьютеры", "Сервер"], "accessible": True},
                {"number": "301", "floor": 3, "type": "auditorium", "capacity": 80, "equipment": ["Микрофоны", "Проектор"], "accessible": False},
                {"number": "401", "floor": 4, "type": "office", "capacity": 10, "equipment": ["Деканат", "Конференц-стол"], "accessible": False}
            ]
        },
        
        # МЕДИЦИНСКИЙ ИНСТИТУТ
        {
            "id": "3",
            "name": "Медицинский институт",
            "type": "academic",
            "description": "Медицинский институт ПГУ с лечебным факультетом и факультетом стоматологии",
            "coordinates": {"x": 180, "y": 120},
            "floor_count": 6,
            "year_built": 1995,
            "departments": ["Лечебный факультет", "Факультет стоматологии", "Клинические кафедры"],
            "amenities": ["Анатомический музей", "Симуляционный центр", "Медицинская библиотека", "Клиника"],
            "accessible": True,
            "has_elevator": True,
            "has_parking": False,
            "rooms": [
                {"number": "101", "floor": 1, "type": "lab", "capacity": 20, "equipment": ["Анатомические препараты", "Микроскопы"], "accessible": True},
                {"number": "102", "floor": 1, "type": "classroom", "capacity": 30, "equipment": ["Медицинские модели", "Проектор"], "accessible": True},
                {"number": "201", "floor": 2, "type": "lab", "capacity": 15, "equipment": ["Симуляторы", "Медицинское оборудование"], "accessible": True},
                {"number": "301", "floor": 3, "type": "auditorium", "capacity": 100, "equipment": ["Амфитеатр", "Микрофоны"], "accessible": True},
                {"number": "401", "floor": 4, "type": "office", "capacity": 8, "equipment": ["Кафедра терапии"], "accessible": False},
                {"number": "501", "floor": 5, "type": "lab", "capacity": 12, "equipment": ["Стоматологические установки"], "accessible": False}
            ]
        },
        
        # ПЕДАГОГИЧЕСКИЙ ИНСТИТУТ ИМ. В.Г. БЕЛИНСКОГО
        {
            "id": "4",
            "name": "Педагогический институт им. В.Г. Белинского",
            "type": "academic",
            "description": "Педагогический институт с историко-филологическим факультетом и факультетом педагогики",
            "coordinates": {"x": 220, "y": 180},
            "floor_count": 4,
            "year_built": 1965,
            "departments": ["Историко-филологический факультет", "Факультет педагогики и психологии", "Факультет физико-математических наук"],
            "amenities": ["Педагогическая библиотека", "Лингафонные кабинеты", "Музей истории", "Актовый зал"],
            "accessible": True,
            "has_elevator": False,
            "has_parking": True,
            "rooms": [
                {"number": "101", "floor": 1, "type": "classroom", "capacity": 30, "equipment": ["Лингафонное оборудование", "Наушники"], "accessible": True},
                {"number": "102", "floor": 1, "type": "classroom", "capacity": 25, "equipment": ["Карты", "Глобус", "Проектор"], "accessible": True},
                {"number": "201", "floor": 2, "type": "auditorium", "capacity": 120, "equipment": ["Сцена", "Микрофоны"], "accessible": True},
                {"number": "301", "floor": 3, "type": "classroom", "capacity": 35, "equipment": ["Интерактивная доска"], "accessible": False},
                {"number": "401", "floor": 4, "type": "office", "capacity": 12, "equipment": ["Деканат", "Архив"], "accessible": False}
            ]
        },
        
        # ЮРИДИЧЕСКИЙ ИНСТИТУТ
        {
            "id": "5",
            "name": "Юридический институт",
            "type": "academic",
            "description": "Юридический институт ПГУ с современными аудиториями и залом судебных заседаний",
            "coordinates": {"x": 250, "y": 140},
            "floor_count": 3,
            "year_built": 1998,
            "departments": ["Кафедра гражданского права", "Кафедра уголовного права", "Кафедра теории государства и права"],
            "amenities": ["Юридическая библиотека", "Зал судебных заседаний", "Правовой консультационный центр"],
            "accessible": True,
            "has_elevator": False,
            "has_parking": True,
            "rooms": [
                {"number": "101", "floor": 1, "type": "auditorium", "capacity": 60, "equipment": ["Зал судебных заседаний", "Судейское место"], "accessible": True},
                {"number": "102", "floor": 1, "type": "classroom", "capacity": 40, "equipment": ["Кодексы", "Проектор"], "accessible": True},
                {"number": "201", "floor": 2, "type": "classroom", "capacity": 35, "equipment": ["Юридическая литература"], "accessible": True},
                {"number": "301", "floor": 3, "type": "office", "capacity": 15, "equipment": ["Консультационный центр"], "accessible": False}
            ]
        },
        
        # ИНСТИТУТ ЭКОНОМИКИ И УПРАВЛЕНИЯ
        {
            "id": "6",
            "name": "Институт экономики и управления",
            "type": "academic",
            "description": "Институт экономики и управления с современными аудиториями и компьютерными классами",
            "coordinates": {"x": 280, "y": 200},
            "floor_count": 4,
            "year_built": 2000,
            "departments": ["Кафедра экономической теории", "Кафедра менеджмента", "Кафедра финансов и кредита"],
            "amenities": ["Бизнес-инкубатор", "Компьютерные классы", "Конференц-залы"],
            "accessible": True,
            "has_elevator": True,
            "has_parking": True,
            "rooms": [
                {"number": "101", "floor": 1, "type": "lab", "capacity": 30, "equipment": ["Экономическое ПО", "Компьютеры"], "accessible": True},
                {"number": "201", "floor": 2, "type": "auditorium", "capacity": 80, "equipment": ["Бизнес-презентации", "Проектор"], "accessible": True},
                {"number": "301", "floor": 3, "type": "classroom", "capacity": 25, "equipment": ["Флипчарт", "Маркеры"], "accessible": False},
                {"number": "401", "floor": 4, "type": "office", "capacity": 20, "equipment": ["Бизнес-инкубатор"], "accessible": False}
            ]
        },
        
        # ИНСТИТУТ ФИЗИЧЕСКОЙ КУЛЬТУРЫ И СПОРТА
        {
            "id": "7",
            "name": "Институт физической культуры и спорта",
            "type": "sports",
            "description": "Институт физической культуры и спорта с спортивными залами и тренажерными комплексами",
            "coordinates": {"x": 50, "y": 300},
            "floor_count": 3,
            "year_built": 1980,
            "departments": ["Кафедра физического воспитания", "Кафедра спортивных дисциплин"],
            "amenities": ["Спортивные залы", "Тренажерный зал", "Бассейн", "Стадион", "Раздевалки"],
            "accessible": True,
            "has_elevator": False,
            "has_parking": True,
            "rooms": [
                {"number": "Зал1", "floor": 1, "type": "other", "capacity": 100, "equipment": ["Спортивный инвентарь", "Баскетбольные кольца"], "accessible": True},
                {"number": "Зал2", "floor": 1, "type": "other", "capacity": 50, "equipment": ["Тренажеры", "Зеркала"], "accessible": True},
                {"number": "Р1", "floor": 1, "type": "other", "capacity": 30, "equipment": ["Раздевалки", "Душ"], "accessible": True},
                {"number": "201", "floor": 2, "type": "classroom", "capacity": 40, "equipment": ["Спортивная теория"], "accessible": True},
                {"number": "301", "floor": 3, "type": "office", "capacity": 15, "equipment": ["Деканат"], "accessible": False}
            ]
        },
        
        # ОБЩЕЖИТИЕ №1
        {
            "id": "О-1",
            "name": "Общежитие №1",
            "type": "living",
            "description": "Студенческое общежитие ПГУ для студентов различных институтов",
            "coordinates": {"x": 300, "y": 250},
            "floor_count": 9,
            "year_built": 1975,
            "amenities": ["Комнаты для проживания", "Кухни на этажах", "Прачечная", "Комната отдыха", "Интернет"],
            "accessible": False,
            "has_elevator": False,
            "has_parking": False,
            "rooms": [
                {"number": "101", "floor": 1, "type": "room", "capacity": 2, "equipment": ["Кровати", "Столы", "Шкафы"], "accessible": False},
                {"number": "102", "floor": 1, "type": "room", "capacity": 3, "equipment": ["Кровати", "Столы", "Шкафы"], "accessible": False},
                {"number": "К1", "floor": 1, "type": "other", "capacity": 10, "equipment": ["Плиты", "Холодильники"], "accessible": False},
                {"number": "201", "floor": 2, "type": "room", "capacity": 2, "equipment": ["Кровати", "Столы"], "accessible": False}
            ]
        },
        
        # ОБЩЕЖИТИЕ №2
        {
            "id": "О-2", 
            "name": "Общежитие №2",
            "type": "living",
            "description": "Современное общежитие ПГУ с улучшенными условиями проживания",
            "coordinates": {"x": 320, "y": 280},
            "floor_count": 10,
            "year_built": 2005,
            "amenities": ["Современные комнаты", "Кухни", "Прачечная", "Wi-Fi", "Спортзал", "Охрана"],
            "accessible": True,
            "has_elevator": True,
            "has_parking": True,
            "rooms": [
                {"number": "101", "floor": 1, "type": "room", "capacity": 2, "equipment": ["Мебель", "Wi-Fi"], "accessible": True},
                {"number": "С1", "floor": 1, "type": "other", "capacity": 20, "equipment": ["Спортзал", "Тренажеры"], "accessible": True},
                {"number": "201", "floor": 2, "type": "room", "capacity": 1, "equipment": ["Одноместная", "Холодильник"], "accessible": True}
            ]
        },
        
        # СТОЛОВАЯ
        {
            "id": "СТ",
            "name": "Столовая ПГУ",
            "type": "dining",
            "description": "Главная столовая университета с горячим питанием и кафе",
            "coordinates": {"x": 120, "y": 80},
            "floor_count": 2,
            "year_built": 1960,
            "amenities": ["Горячее питание", "Буфет", "Кафе", "Wi-Fi"],
            "accessible": True,
            "has_elevator": False,
            "has_parking": False,
            "rooms": [
                {"number": "Зал", "floor": 1, "type": "cafe", "capacity": 200, "equipment": ["Столы", "Касса"], "accessible": True},
                {"number": "Буфет", "floor": 1, "type": "cafe", "capacity": 30, "equipment": ["Витрина", "Касса"], "accessible": True},
                {"number": "Кухня", "floor": 1, "type": "other", "capacity": 15, "equipment": ["Промышленные плиты"], "accessible": False}
            ]
        },
        
        # БИБЛИОТЕКА
        {
            "id": "БИБ",
            "name": "Научно-техническая библиотека",
            "type": "academic",
            "description": "Центральная библиотека ПГУ с читальными залами и электронными ресурсами",
            "coordinates": {"x": 140, "y": 160},
            "floor_count": 3,
            "year_built": 1968,
            "departments": ["Отдел комплектования", "Читальные залы", "Электронная библиотека"],
            "amenities": ["Читальные залы", "Компьютеры", "Wi-Fi", "Ксерокс", "Сканер"],
            "accessible": True,
            "has_elevator": False,
            "has_parking": False,
            "rooms": [
                {"number": "Ч1", "floor": 1, "type": "library", "capacity": 100, "equipment": ["Столы", "Каталоги"], "accessible": True},
                {"number": "Ч2", "floor": 2, "type": "library", "capacity": 150, "equipment": ["Компьютеры", "Wi-Fi"], "accessible": True},
                {"number": "Э1", "floor": 3, "type": "library", "capacity": 50, "equipment": ["Электронные ресурсы"], "accessible": False}
            ]
        },
        
        # ВОЕННЫЙ УЧЕБНЫЙ ЦЕНТР
        {
            "id": "ВУЦ",
            "name": "Военный учебный центр им. В.Ф. Шишкова",
            "type": "academic",
            "description": "Военный учебный центр для подготовки офицеров запаса",
            "coordinates": {"x": 350, "y": 100},
            "floor_count": 2,
            "year_built": 1995,
            "departments": ["Военная кафедра", "Учебные подразделения"],
            "amenities": ["Тир", "Строевой плац", "Военная техника", "Склады"],
            "accessible": True,
            "has_elevator": False,
            "has_parking": True,
            "rooms": [
                {"number": "101", "floor": 1, "type": "classroom", "capacity": 30, "equipment": ["Военная подготовка"], "accessible": True},
                {"number": "Тир", "floor": 1, "type": "other", "capacity": 15, "equipment": ["Тренажеры стрельбы"], "accessible": True},
                {"number": "201", "floor": 2, "type": "office", "capacity": 10, "equipment": ["Штаб"], "accessible": False}
            ]
        }
    ] 