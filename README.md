# 🏪 Store Check — Система цінового моніторингу

> Telegram Mini App для автоматизації польового моніторингу цін конкурентів.  
> Без паперових носіїв. Без ручного переносу даних. Звіти — автоматично на email.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen)](https://vuejs.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)](https://aiogram.dev)

---

## 📋 Зміст

- [Як це працює](#як-це-працює)
- [Технологічний стек](#технологічний-стек)
- [Структура проєкту](#структура-проєкту)
- [Швидкий старт](#швидкий-старт)
- [Змінні середовища](#змінні-середовища)
- [API Reference](#api-reference)
- [Архітектура](#архітектура)
- [Деплой](#деплой)

---

## Як це працює

1. **Співробітник** відкриває Telegram-бот → натискає кнопку Mini App
2. Обирає магазин → система створює сесію обходу
3. По кожному товару вводить ціну на великому numpad (або позначає "відсутнє")
4. Товари, відсутні **3 обходи поспіль**, автоматично приховуються (Smart Hide)
5. Після завершення — Celery у фоні генерує `.xlsx` звіт і надсилає аналітикам на email
6. **Адміністратор** через ту ж Mini App управляє персоналом, магазинами, каталогом та вручну вивантажує звіти

---

## Технологічний стек

| Шар | Технологія |
|-----|-----------|
| Backend API | Python 3.11+, FastAPI, SQLAlchemy 2 (async) |
| База даних | PostgreSQL 15+ |
| Кеш / Черга | Redis 7+, Celery 5 + Celery Beat |
| Telegram Bot | aiogram 3.x |
| Frontend | Vue 3, Vite 5, Tailwind CSS 3, Pinia |
| Звіти | pandas, openpyxl |
| Офлайн | IndexedDB (каталог) + localStorage (черга результатів) |

---

## Структура проєкту

```
monitoring/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── middleware/
│   │   │   │   └── rate_limit.py       # Rate Limiting (Redis)
│   │   │   └── v1/
│   │   │       ├── auth.py             # POST /auth/verify
│   │   │       ├── catalog.py          # GET /catalog (Redis-кеш)
│   │   │       ├── stores.py           # GET /stores
│   │   │       ├── sessions.py         # POST + PATCH /sessions
│   │   │       ├── results.py          # POST /results + Smart Hide
│   │   │       ├── reports.py          # POST /reports/export
│   │   │       ├── deps.py             # JWT, RBAC, Redis deps
│   │   │       └── admin/
│   │   │           ├── users.py        # CRUD + блокування
│   │   │           ├── stores.py       # Створення + архів
│   │   │           └── catalog.py      # UPSERT .xlsx + інвалідація кешу
│   │   ├── models/
│   │   │   ├── user.py                 # users (telegram_id, role, is_active)
│   │   │   ├── store.py                # stores (is_active)
│   │   │   ├── category.py             # categories (parent_id, level, sort_order)
│   │   │   ├── product.py              # products (article_id UNIQUE, is_archived)
│   │   │   ├── session.py              # monitoring_sessions (status enum)
│   │   │   ├── result.py               # monitoring_results (result_type, індекси)
│   │   │   └── stats.py                # store_product_stats (UNIQUE store+product)
│   │   ├── schemas/                    # Pydantic v2 схеми
│   │   ├── services/
│   │   │   ├── auth_service.py         # HMAC-SHA256, JWT
│   │   │   └── report_service.py       # .xlsx генерація, SMTP email
│   │   ├── tasks/
│   │   │   ├── report_tasks.py         # Celery: генерація + email (retry ×3)
│   │   │   └── maintenance.py          # Celery Beat: cleanup о 03:00
│   │   ├── db/
│   │   │   ├── base.py                 # AsyncEngine, AsyncSessionLocal
│   │   │   └── init_db.py              # create_all()
│   │   ├── celery_app.py               # Celery + Beat (timezone Kyiv)
│   │   ├── config.py                   # Pydantic Settings (.env)
│   │   └── main.py                     # FastAPI app + middleware
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── start.py                # /start → WebApp кнопка
│   │   │   └── menu.py                 # /help
│   │   ├── middlewares/
│   │   │   └── auth.py                 # Перевірка доступу (БД + superadmin)
│   │   └── main.py                     # Dispatcher, polling
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                        # Axios-клієнти (auth, catalog, sessions, reports)
│   │   ├── components/
│   │   │   ├── Numpad.vue              # Цифрова клавіатура (2 знаки після коми)
│   │   │   ├── ProductCard.vue         # Картка товару
│   │   │   ├── ProgressBar.vue         # Прогрес категорії
│   │   │   ├── TabBar.vue              # Нижня навігація
│   │   │   └── ConnectionStatus.vue    # Онлайн/офлайн індикатор
│   │   ├── stores/
│   │   │   ├── auth.js                 # Pinia: JWT, роль
│   │   │   ├── catalog.js              # Pinia: каталог + IndexedDB
│   │   │   └── session.js              # Pinia: сесія + офлайн-черга
│   │   ├── views/
│   │   │   ├── SelectStore.vue         # Вибір магазину
│   │   │   ├── Home.vue                # Плитки категорій
│   │   │   ├── Catalog.vue             # Деревоподібний каталог
│   │   │   ├── Carousel.vue            # Обхід товарів (Numpad + Smart Hide)
│   │   │   ├── Unauthorized.vue        # Заглушка без доступу
│   │   │   └── admin/
│   │   │       ├── Users.vue           # Управління персоналом
│   │   │       ├── Stores.vue          # Управління магазинами
│   │   │       └── Reports.vue         # Ручне вивантаження звітів
│   │   ├── router/index.js             # Vue Router (guards: auth + admin)
│   │   ├── App.vue                     # Telegram theme + ConnectionStatus
│   │   └── main.js
│   ├── index.html                      # telegram-web-app.js підключення
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
└── README.md
```

---

## Швидкий старт

### Вимоги

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### 1. Клонування

```bash
git clone https://github.com/imeromua/monitoring.git
cd monitoring
```

### 2. Бекенд

```bash
cd backend
cp .env.example .env
# Відредагуй .env (див. розділ "Змінні середовища")

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Створення таблиць БД
python -m app.db.init_db
```

### 3. Фронтенд

```bash
cd ../frontend
npm install
```

### 4. Запуск (окремі термінали)

```bash
# Термінал 1 — FastAPI
cd backend
uvicorn app.main:app --reload --port 8000

# Термінал 2 — Telegram Bot
python -m bot.main

# Термінал 3 — Celery Worker
celery -A app.celery_app worker --loglevel=info -c 2

# Термінал 4 — Celery Beat
celery -A app.celery_app beat --loglevel=info

# Термінал 5 — Vue Dev Server
cd frontend
npm run dev
```

### 5. Swagger UI

```
http://localhost:8000/docs
```

---

## Змінні середовища

Файл: `backend/.env`

```env
# ── База даних ─────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/monitoring

# ── Redis ──────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ── Telegram ───────────────────────────────────────────────────
BOT_TOKEN=your_bot_token_here
SUPERADMIN_TELEGRAM_ID=123456789        # Твій Telegram ID

# ── JWT ────────────────────────────────────────────────────────
JWT_SECRET_KEY=your_super_secret_key_here   # мін. 32 символи
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8

# ── SMTP Email ─────────────────────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password         # App Password, не звичайний пароль
REPORT_RECIPIENTS=analyst1@company.com,analyst2@company.com

# ── Звіти ──────────────────────────────────────────────────────
REPORTS_DIR=/tmp/reports                # Директорія для .xlsx файлів
REPORT_TTL_HOURS=2                      # Через скільки годин видаляти файли
```

> **Gmail:** увімкни двофакторну автентифікацію → створи App Password на [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## API Reference

### Аутентифікація

| Метод | URL | Опис | Auth |
|-------|-----|------|------|
| `POST` | `/api/v1/auth/verify` | Авторизація через Telegram `initData` (HMAC-SHA256) | — |

### Worker API

| Метод | URL | Опис | Auth |
|-------|-----|------|------|
| `GET` | `/api/v1/catalog` | Каталог товарів і категорій (Redis TTL 1 год) | JWT |
| `GET` | `/api/v1/stores` | Список активних магазинів | JWT |
| `POST` | `/api/v1/sessions` | Створити сесію обходу | JWT |
| `POST` | `/api/v1/sessions/{id}/results` | Зберегти результат по товару | JWT |
| `PATCH` | `/api/v1/sessions/{id}/complete` | Завершити обхід → запустити Celery | JWT |

### Admin API

| Метод | URL | Опис | Auth |
|-------|-----|------|------|
| `POST` | `/api/v1/reports/export` | Завантажити `.xlsx` звіт (фільтр дат/магазин) | JWT Admin |
| `GET` | `/api/v1/admin/users` | Список персоналу | JWT Admin |
| `POST` | `/api/v1/admin/users` | Додати співробітника | JWT Admin |
| `PATCH` | `/api/v1/admin/users/{id}` | Оновити / заблокувати (Redis Blacklist) | JWT Admin |
| `GET` | `/api/v1/admin/stores` | Список магазинів (всі) | JWT Admin |
| `POST` | `/api/v1/admin/stores` | Створити магазин | JWT Admin |
| `PATCH` | `/api/v1/admin/stores/{id}/archive` | Архівувати магазин | JWT Admin |
| `POST` | `/api/v1/admin/catalog/upload` | UPSERT каталогу з `.xlsx` | JWT Admin |

### Rate Limits

| Маршрут | Ліміт |
|---------|-------|
| `/api/v1/sessions/*` | 60 запитів / хв |
| `/api/v1/reports/*` | 10 запитів / хв |
| Решта | 120 запитів / хв |

---

## Архітектура

```
Telegram User
     │
     ▼
┌─────────────┐    initData    ┌──────────────────┐
│ Telegram Bot│ ─────────────▶ │  FastAPI Backend  │
│  (aiogram3) │                │                  │
└─────────────┘                │  • JWT Auth       │
                               │  • Rate Limiting  │
┌─────────────┐   API calls    │  • Redis Cache    │
│  Vue 3 Mini │ ◀────────────▶ │  • RBAC (3 ролі) │
│     App     │                │                  │
└─────────────┘                └────────┬─────────┘
  IndexedDB                             │
  (офлайн)                    ┌─────────▼─────────┐
                               │    PostgreSQL      │
                               │  7 таблиць + idx   │
                               └─────────┬─────────┘
                                         │
                               ┌─────────▼─────────┐
                               │  Celery + Redis    │
                               │  • Звіт → Email   │
                               │  • Cleanup 03:00  │
                               └───────────────────┘
```

### Ключові патерни

- **Smart Hide** — товар приховується після 3 підряд відсутностей (`consecutive_missing_count` в `store_product_stats`), відновлюється вручну
- **Redis Blacklist** — блокування набирає чинності **миттєво**, без очікування закінчення JWT
- **Offline-first** — каталог у IndexedDB, результати в `localStorage`-черзі; при відновленні з'єднання авто-синхронізація
- **Celery async** — генерація звіту не блокує відповідь API, auto-retry ×3 при збої

---

## Деплой

### Продакшн (базовий сценарій)

```bash
# 1. Збірка фронтенду
cd frontend
npm run build
# dist/ → скопіювати на nginx або CDN

# 2. Запуск бекенду через gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 3. Celery через supervisord або systemd
celery -A app.celery_app worker -c 2 -l info
celery -A app.celery_app beat -l info

# 4. Telegram Webhook (замість polling)
# Після деплою: POST https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://your-domain.com/webhook
```

### Nginx (приклад)

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location / {
        root /var/www/store-check/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

> ⚠️ Telegram Mini App вимагає **HTTPS**. Використовуй [Let's Encrypt](https://letsencrypt.org/) / Certbot.

---

## Безпека

- `SUPERADMIN_TELEGRAM_ID` — лише в `.env`, ніколи не в БД
- Усі паролі та токени — лише через змінні середовища
- `.env` та `reports/` додані до `.gitignore`
- JWT підписується `HS256` + секрет ≥ 32 символи
- CORS в продакшні — замінити `allow_origins=["*"]` на реальний домен

---

## Ліцензія

MIT © 2026 imeromua
