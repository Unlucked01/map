# 🚀 Продакшн развертывание PGU University Map

Полная инструкция по развертыванию интерактивной карты университета на сервере с доменом `unl-map.duckdns.org`.

## 📋 Предварительные требования

### На сервере должны быть установлены:
- Docker Engine (версия 20.10+)
- Docker Compose (версия 2.0+)
- Git
- Curl (для проверки доступности)

### Системные требования:
- **CPU**: минимум 2 ядра
- **RAM**: минимум 2GB
- **Дисковое пространство**: минимум 10GB
- **Операционная система**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

## 🔧 Настройка сервера

### 1. Установка Docker (Ubuntu/Debian)
```bash
# Обновляем пакеты
sudo apt update && sudo apt upgrade -y

# Устанавливаем зависимости
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавляем официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагружаемся или выходим/входим в систему
newgrp docker
```

### 2. Настройка фаервола
```bash
# Открываем необходимые порты
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 3. Настройка DNS
Убедитесь, что домен `unl-map.duckdns.org` указывает на IP-адрес вашего сервера.

## 🚀 Развертывание приложения

### 1. Клонирование репозитория
```bash
cd /opt
sudo git clone https://github.com/your-username/map_v2.git pgu-map
sudo chown -R $USER:$USER pgu-map
cd pgu-map
```

### 2. Автоматическое развертывание
```bash
# С вашим email (рекомендуется)
./deploy.sh your-email@example.com

# Или с помощью Makefile
make deploy
```

### 3. Ручное развертывание (если нужно больше контроля)

#### Шаг 1: Подготовка конфигурации
```bash
# Обновляем email в docker-compose.prod.yml
sed -i 's/your-email@example.com/your-actual-email@example.com/g' docker-compose.prod.yml
```

#### Шаг 2: Сборка образов
```bash
docker-compose -f docker-compose.prod.yml build --no-cache
```

#### Шаг 3: Первоначальный запуск (без SSL)
```bash
# Запускаем основные сервисы
docker-compose -f docker-compose.prod.yml up -d nginx frontend backend

# Проверяем, что сервисы запустились
docker-compose -f docker-compose.prod.yml ps
```

#### Шаг 4: Получение SSL сертификата
```bash
# Получаем сертификат от Let's Encrypt
docker-compose -f docker-compose.prod.yml run --rm certbot

# Перезапускаем nginx с SSL
docker-compose -f docker-compose.prod.yml restart nginx
```

## 📊 Проверка развертывания

### Проверка статуса сервисов
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Проверка логов
```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Проверка доступности
```bash
# HTTP (должен перенаправить на HTTPS)
curl -I http://unl-map.duckdns.org

# HTTPS
curl -I https://unl-map.duckdns.org

# Проверка API
curl https://unl-map.duckdns.org/api/health
```

## 🔄 Управление приложением

### Основные команды
```bash
# Запуск
make prod-up
# или
docker-compose -f docker-compose.prod.yml up -d

# Остановка
make prod-down
# или
docker-compose -f docker-compose.prod.yml down

# Перезапуск
docker-compose -f docker-compose.prod.yml restart

# Логи в реальном времени
make prod-logs
# или
docker-compose -f docker-compose.prod.yml logs -f
```

### Обновление приложения
```bash
# Получаем последние изменения
git pull origin main

# Пересобираем и перезапускаем
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Управление SSL сертификатами

### Ручное обновление сертификата
```bash
make renew-ssl
# или
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

### Автоматическое обновление (рекомендуется)
```bash
# Добавляем в crontab
crontab -e

# Добавляем строку (обновление каждое 1 число месяца в 00:00)
0 0 1 * * cd /opt/pgu-map && docker-compose -f docker-compose.prod.yml run --rm certbot renew && docker-compose -f docker-compose.prod.yml restart nginx
```

## 📈 Мониторинг и обслуживание

### Мониторинг ресурсов
```bash
# Использование ресурсов контейнерами
docker stats

# Использование дискового пространства
df -h
docker system df
```

### Очистка системы
```bash
# Очистка неиспользуемых образов и контейнеров
docker system prune -f

# Полная очистка (ОСТОРОЖНО!)
make clean
```

### Резервное копирование данных
```bash
# Создание резервной копии базы данных
docker run --rm \
  -v pgu-map_backend_prod_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/database-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# Восстановление из резервной копии
docker run --rm \
  -v pgu-map_backend_prod_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/database-YYYYMMDD-HHMMSS.tar.gz -C /data
```

## 🔍 Решение проблем

### Проблема: Nginx не запускается
```bash
# Проверяем логи nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Проверяем конфигурацию
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### Проблема: SSL сертификат не получается
```bash
# Проверяем, что домен указывает на сервер
nslookup unl-map.duckdns.org

# Проверяем доступность по HTTP
curl http://unl-map.duckdns.org/.well-known/acme-challenge/test

# Получаем сертификат в тестовом режиме
docker-compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot --webroot-path=/var/www/certbot \
  --email your-email@example.com --agree-tos --no-eff-email \
  --staging -d unl-map.duckdns.org
```

### Проблема: Приложение недоступно
```bash
# Проверяем статус всех сервисов
docker-compose -f docker-compose.prod.yml ps

# Проверяем логи backend
docker-compose -f docker-compose.prod.yml logs backend

# Проверяем внутреннюю связность
docker-compose -f docker-compose.prod.yml exec frontend curl http://backend:8000/health
```

## 🛡️ Безопасность

### Рекомендации по безопасности:
1. **Регулярно обновляйте сервер**: `sudo apt update && sudo apt upgrade`
2. **Настройте фаервол**: разрешите только необходимые порты
3. **Используйте strong пароли** и SSH ключи
4. **Мониторьте логи** на предмет подозрительной активности
5. **Регулярно создавайте резервные копии**

### Мониторинг безопасности:
```bash
# Проверка активных соединений
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Проверка процессов Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `make prod-logs`
2. Проверьте статус сервисов: `docker-compose -f docker-compose.prod.yml ps`
3. Перезапустите проблемный сервис: `docker-compose -f docker-compose.prod.yml restart [service_name]`

## 🔗 Полезные ссылки

- **Приложение**: https://unl-map.duckdns.org
- **Документация Docker**: https://docs.docker.com/
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx**: https://nginx.org/ru/docs/ 