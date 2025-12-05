# REST-сервис для управления заявками на выплату средств

REST-сервис на Django REST Framework для управления заявками на выплату с асинхронной обработкой через Celery.

## Технологический стек

- Python 3.10+
- Django 4.2+
- Django REST Framework
- Celery + Redis
- PostgreSQL
- Docker Compose

## Структура проекта

```
.
├── docker-compose.yml      # Конфигурация Docker Compose
├── Dockerfile              # Образ для приложения
├── requirements.txt        # Зависимости Python
├── manage.py              # Django management script
├── payout_service/        # Основной проект Django
│   ├── __init__.py
│   ├── settings.py        # Настройки Django
│   ├── urls.py           # Главный URL router
│   ├── wsgi.py           # WSGI конфигурация
│   └── celery.py         # Конфигурация Celery
└── payouts/              # Приложение для заявок на выплату
    ├── models.py         # Модель PayoutRequest
    ├── serializers.py    # DRF сериализаторы
    ├── views.py          # ViewSet для API
    ├── urls.py           # URL маршруты API
    ├── tasks.py          # Celery задачи
    └── admin.py          # Админ-панель
```

## Быстрый старт

### 1. Клонирование и настройка

```bash
# Создайте файл .env на основе .env.example
cp .env.example .env

# Отредактируйте .env при необходимости
```

### 2. Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 3. Применение миграций

```bash
# В отдельном терминале или после запуска контейнеров
docker-compose exec web python manage.py migrate

# Создание суперпользователя (опционально)
docker-compose exec web python manage.py createsuperuser
```

### 4. Доступ к сервису

- API: http://localhost:8000/api/
- Админ-панель: http://localhost:8000/admin/

## API Эндпоинты

### Список заявок
```
GET /api/payouts/
```

### Получение заявки по ID
```
GET /api/payouts/{id}/
```

### Создание новой заявки
```
POST /api/payouts/
Content-Type: application/json

{
    "amount": "1000.00",
    "currency": "RUB",
    "recipient_details": "Банковские реквизиты получателя",
    "comment": "Комментарий к заявке (опционально)"
}
```

При создании заявки автоматически запускается Celery-задача для асинхронной обработки.

### Частичное обновление заявки
```
PATCH /api/payouts/{id}/
Content-Type: application/json

{
    "status": "completed",
    "comment": "Обновленный комментарий"
}
```

### Удаление заявки
```
DELETE /api/payouts/{id}/
```

## Модель данных

### PayoutRequest (Заявка на выплату)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Идентификатор (автоматически) |
| amount | Decimal | Сумма выплаты (положительное число) |
| currency | String | Валюта (USD, EUR, RUB) |
| recipient_details | Text | Реквизиты получателя (до 1000 символов) |
| status | String | Статус заявки (pending, processing, completed, failed, cancelled) |
| comment | Text | Комментарий (до 500 символов, опционально) |
| created_at | DateTime | Дата создания (автоматически) |
| updated_at | DateTime | Дата обновления (автоматически) |

## Статусы заявки

- `pending` - Ожидает обработки (начальный статус)
- `processing` - В обработке (устанавливается Celery задачей)
- `completed` - Завершена (успешная обработка)
- `failed` - Ошибка (при ошибке обработки)
- `cancelled` - Отменена

## Асинхронная обработка

При создании заявки через API автоматически запускается Celery-задача `process_payout_request`, которая:

1. Изменяет статус заявки на `processing`
2. Выполняет имитацию обработки (проверки, задержка)
3. Изменяет статус на `completed` или `failed` в зависимости от результата

Логи обработки можно просмотреть в логах Celery worker:
```bash
docker-compose logs celery
```

## Валидация

При создании заявки проверяются:

- **amount**: должно быть положительным числом (> 0)
- **currency**: должна быть одной из допустимых валют (USD, EUR, RUB)
- **recipient_details**: обязательное поле, не пустое, до 1000 символов
- **comment**: опциональное поле, до 500 символов

## Примеры использования API

### Создание заявки

```bash
curl -X POST http://localhost:8000/api/payouts/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "5000.00",
    "currency": "RUB",
    "recipient_details": "Счет: 40817810099910004312, БИК: 044525225, Банк: ПАО Сбербанк",
    "comment": "Выплата за март 2024"
  }'
```

### Получение списка заявок

```bash
curl http://localhost:8000/api/payouts/
```

### Обновление статуса заявки

```bash
curl -X PATCH http://localhost:8000/api/payouts/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelled"
  }'
```

## Разработка без Docker

Если вы хотите запустить проект локально без Docker:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
export SECRET_KEY=your-secret-key
export DEBUG=True
export POSTGRES_DB=payout_db
export POSTGRES_USER=payout_user
export POSTGRES_PASSWORD=payout_password
export POSTGRES_HOST=localhost
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Применение миграций
python manage.py migrate

# Запуск сервера разработки
python manage.py runserver

# В отдельном терминале - запуск Celery worker
celery -A payout_service worker --loglevel=info
```

## Тестирование

Для тестирования API можно использовать:

- curl (примеры выше)
- Postman
- httpie: `http POST localhost:8000/api/payouts/ amount=1000 currency=RUB recipient_details="Реквизиты"`
- Django REST Framework Browsable API: http://localhost:8000/api/payouts/

## Логирование

Логи Celery задач можно просмотреть:
```bash
docker-compose logs -f celery
```

Логи веб-сервера:
```bash
docker-compose logs -f web
```

## Остановка сервисов

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (удалит данные БД)
docker-compose down -v
```

## Примечания

- По умолчанию используется база данных PostgreSQL в Docker
- Redis используется как брокер сообщений для Celery
- Все сервисы настроены для работы в Docker Compose
- Для production необходимо изменить SECRET_KEY и настройки безопасности

