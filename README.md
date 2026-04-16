# Store Check — Система цінового моніторингу

Telegram Mini App для польових співробітників та аналітиків.
Дозволяє проводити моніторинг цін конкурентів без паперових носіїв та ручного перенесення даних.

## Технологічний стек

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2 (async), PostgreSQL
- **Cache / Queue:** Redis, Celery + Celery Beat
- **Bot:** aiogram 3.x
- **Frontend:** Vue 3 + Vite + Tailwind CSS
- **Reports:** pandas + openpyxl

---

## Швидкий старт (розробка)

### 1. Клонування та налаштування

```bash
git clone https://github.com/imeromua/monitoring.git
cd monitoring/backend
cp .env.example .env
# Відредагуй .env — вкажи DATABASE_URL, BOT_TOKEN, JWT_SECRET_KEY тощо
```

### 2. Встановлення залежностей

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Створення таблиць БД

```bash
python -m app.db.init_db
```

### 4. Запуск сервісів (окремі термінали)

```bash
# Термінал 1 — FastAPI
uvicorn app.main:app --reload --port 8000

# Термінал 2 — Telegram Bot
python -m bot.main

# Термінал 3 — Celery Worker
celery -A app.celery_app worker --loglevel=info

# Термінал 4 — Celery Beat (авто-очищення звітів)
celery -A app.celery_app beat --loglevel=info
```

### 5. Swagger UI

Після запуску FastAPI доступна документація API:
```
http://localhost:8000/docs
```

---

## Структура проєкту

```
monitoring/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI роутери
│   │   ├── models/          # SQLAlchemy моделі
│   │   ├── schemas/         # Pydantic схеми
│   │   ├── services/        # Бізнес-логіка
│   │   ├── tasks/           # Celery задачі
│   │   ├── db/              # Підключення до БД
│   │   ├── celery_app.py    # Celery + Beat
│   │   ├── config.py        # Налаштування (.env)
│   │   └── main.py          # FastAPI точка входу
│   ├── bot/                 # aiogram 3 бот
│   └── requirements.txt
├── frontend/                # Vue 3 + Vite + Tailwind
└── reports/                 # Локальні .xlsx звіти (git-ignored)
```

---

## Ключові ендпоінти API

| Метод | URL | Опис |
|-------|-----|------|
| POST | `/api/v1/auth/verify` | Авторизація через Telegram initData |
| GET | `/api/v1/catalog` | Каталог товарів (Redis-кеш) |
| GET | `/api/v1/stores` | Список магазинів |
| POST | `/api/v1/sessions` | Створити сесію обходу |
| POST | `/api/v1/sessions/{id}/results` | Зберегти результат |
| PATCH | `/api/v1/sessions/{id}/complete` | Завершити обхід |
| POST | `/api/v1/reports/export` | Завантажити звіт (admin) |
| POST | `/api/v1/admin/catalog/upload` | Завантажити каталог .xlsx |

---

## Примітки

- `SUPERADMIN_TELEGRAM_ID` зберігається виключно в `.env`
- Блокування користувача діє **миттєво** через Redis Blacklist
- Звіти генеруються у фоні (Celery), користувач не чекає
- Файли звітів автоматично видаляються через `REPORT_TTL_HOURS` (Celery Beat о 03:00)
- Новинки конкурентів підсвічуються **жовтим**, різновиди — *курсивом*
