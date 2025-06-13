# Используем официальный Python образ
FROM --platform=linux/amd64 python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файла зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Создание директории для базы данных
RUN mkdir -p /app/data

# Перемещение базы данных в постоянную директорию
RUN if [ -f university_map.db ]; then mv university_map.db /app/data/; fi

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Открытие порта
EXPOSE 8000

# Команда запуска (убираем --reload для продакшена)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 