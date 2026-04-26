# AGENT.md — Контекст проєкту для AI-агентів

> Цей файл описує архітектуру, домовленості та правила проєкту.
> Читай його **перед** будь-якими змінами в коді.

---

## Що це за проєкт

**Store Check** — Telegram Mini App для автоматизації польового цінового моніторингу.
Польовий співробітник (worker) відкриває бота, обирає магазин і по черзі вводить ціни
конкурентів з великого numpad. Після завершення Celery у фоні генерує `.xlsx`-звіт
і надсилає аналітикам на email.

---

## Технологічний стек

| Шар | Технологія | Версія |
|-----|-----------|--------|
| Backend API | FastAPI + SQLAlchemy 2 async | Python 3.11+ |
| База даних | PostgreSQL | 15+ |
| Кеш / черга | Redis + Celery + Celery Beat | Redis 7+ |
| Telegram Bot | aiogram | 3.x |
| Frontend | Vue 3 + Vite + Tailwind CSS + Pinia | Node 20+ |
| Звіти | pandas + openpyxl | — |

---

## Структура репозиторію

```
monitoring/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── middleware/rate_limit.py   # Redis Rate Limiting
│   │   │   └── v1/
│   │   │       ├── auth.py               # POST /auth/verify (HMAC-SHA256)
│   │   │       ├── catalog.py            # GET /catalog (Redis TTL 1h)
│   │   │       ├── stores.py             # GET /stores
│   │   │       ├── sessions.py           # POST + PATCH /sessions
│   │   │       ├── results.py            # POST /results + Smart Hide
│   │   │       ├── reports.py            # POST /reports/export
│   │   │       ├── deps.py               # JWT deps, RBAC, Redis
│   │   │       └── admin/                # users, stores, catalog
│   │   ├── models/                       # SQLAlchemy ORM (7 таблиць)
│   │   ├── schemas/                      # Pydantic v2
│   │   ├── services/
│   │   │   ├── auth_service.py           # HMAC, JWT create/decode
│   │   │   └── report_service.py         # .xlsx генерація + SMTP
│   │   ├── tasks/
│   │   │   ├── report_tasks.py           # Celery: звіт + email
│   │   │   └── maintenance.py            # Celery Beat: cleanup 03:00
│   │   ├── db/
│   │   │   ├── base.py                   # AsyncEngine, AsyncSessionLocal
│   │   │   └── init_db.py                # create_all()
│   │   ├── celery_app.py                 # Celery + Beat (timezone Kyiv)
│   │   ├── config.py                     # Pydantic Settings з .env
│   │   └── main.py                       # FastAPI app entry point
│   ├── bot/
│   │   ├── handlers/start.py             # /start → WebApp кнопка
│   │   ├── handlers/menu.py              # /help
│   │   ├── middlewares/auth.py           # перевірка доступу (БД + superadmin)
│   │   └── main.py                       # Dispatcher, polling
│   ├── .env.example                      # шаблон змінних середовища
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                          # Axios клієнти
│   │   ├── components/
│   │   │   ├── Numpad.vue                # цифрова клавіатура
│   │   │   ├── ProductCard.vue           # картка товару
│   │   │   ├── ProgressBar.vue           # прогрес категорії
│   │   │   ├── TabBar.vue                # нижня навігація
│   │   │   └── ConnectionStatus.vue      # онлайн/офлайн індикатор
│   │   ├── stores/
│   │   │   ├── auth.js                   # Pinia: JWT, роль
│   │   │   ├── catalog.js                # Pinia: каталог + IndexedDB
│   │   │   └── session.js                # Pinia: сесія + офлайн-черга
│   │   ├── views/
│   │   │   ├── SelectStore.vue
│   │   │   ├── Home.vue
│   │   │   ├── Catalog.vue
│   │   │   ├── Carousel.vue              # основний робочий екран
│   │   │   ├── Unauthorized.vue
│   │   │   └── admin/                    # Users, Stores, Reports
│   │   ├── router/index.js               # guards: requiresAuth, requiresAdmin
│   │   └── App.vue                       # Telegram theme init
│   ├── index.html                        # telegram-web-app.js підключення
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── .gitignore
├── README.md
└── AGENT.md                              # ← цей файл
```

---

## Бізнес-логіка (критично знати)

### Smart Hide
Якщо товар позначений "відсутнє" **3 рази підряд** в одному магазині —
він автоматично ховається з карусельного обходу.
- Лічильник: `store_product_stats.consecutive_missing_count`
- При наявності ціни — лічильник скидається в 0
- Товар можна "воскресити" вручну через "Цвинтар" наприкінці категорії

### result_type enum
```
standard        — звичайна ціна конкурента
variant         — різновид товару (відображається курсивом у звіті)
competitor_new  — новинка конкурента (підсвічується жовтим у звіті)
```

### Redis Blacklist
- Блокування набирає чинності **миттєво**, не чекаючи закінчення JWT
- Ключ: `blocked:{telegram_id}`
- Перевірка в `deps.py` перед декодуванням токена

### Офлайн-режим
- Каталог кешується в **IndexedDB** браузера
- Незбережені результати йдуть у `localStorage`-чергу
- При відновленні з'єднання `ConnectionStatus.vue` автоматично викликає `session.syncOfflineQueue()`

---

## Змінні середовища (`backend/.env`)

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/monitoring
REDIS_URL=redis://localhost:6379/0

BOT_TOKEN=                        # @BotFather
SUPERADMIN_TELEGRAM_ID=           # числовий Telegram ID суперадміна

JWT_SECRET_KEY=                   # мін. 32 символи (python -c "import secrets; print(secrets.token_hex(32))")
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=                    # Gmail App Password (без пробілів)
REPORT_RECIPIENTS=                # через кому: a@b.com,c@d.com

REPORTS_DIR=/tmp/reports          # директорія для .xlsx файлів
REPORT_TTL_HOURS=2                # через скільки годин видаляти
```

---

## API ендпоінти

### Публічні
| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/auth/verify` | Авторизація через Telegram initData |

### Worker (JWT)
| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/api/v1/catalog` | Каталог (Redis TTL 1h) |
| `GET` | `/api/v1/stores` | Активні магазини |
| `POST` | `/api/v1/sessions` | Створити сесію |
| `POST` | `/api/v1/sessions/{id}/results` | Зберегти результат |
| `PATCH` | `/api/v1/sessions/{id}/complete` | Завершити → запустити Celery |

### Admin (JWT + role=admin)
| Метод | URL | Опис |
|-------|-----|------|
| `POST` | `/api/v1/reports/export` | Завантажити .xlsx |
| `GET/POST/PATCH` | `/api/v1/admin/users` | Управління персоналом |
| `GET/POST/PATCH` | `/api/v1/admin/stores` | Управління магазинами |
| `POST` | `/api/v1/admin/catalog/upload` | UPSERT каталогу з .xlsx |

### Rate Limits
| Маршрут | Ліміт |
|---------|-------|
| `/api/v1/sessions/*` | 60 req / хв |
| `/api/v1/reports/*` | 10 req / хв |
| решта | 120 req / хв |

---

## Домовленості по коду

### Backend
- **Async скрізь** — всі DB-операції через `async with AsyncSessionLocal() as db`
- **Транзакції** — `async with db.begin()` для операцій запис+оновлення
- **Схеми** — вхідні дані валідуються Pydantic v2; від'ємна ціна та > 100 000 — помилка
- **Celery tasks** — лише синхронний код; для DB використовувати `psycopg2` (не asyncpg)
- **Timezone** — завжди `Europe/Kyiv`; в БД зберігати UTC, виводити через `AT TIME ZONE`
- **Soft delete** — використовувати `is_active=False` / `is_archived=True`, не `DELETE`
- **Config** — всі налаштування через `settings` з `app/config.py`, не хардкодити

### Frontend
- **Composition API** — тільки `<script setup>`, не Options API
- **Стилі** — тільки Tailwind утиліти + CSS-змінні `var(--tg-theme-*)`, без кастомного CSS
- **API-виклики** — тільки через функції з `src/api/`, не axios напряму у компонентах
- **Стан** — тільки через Pinia stores, не `ref()` у батьківських компонентах для глобального стану
- **Офлайн** — будь-який запис результату має проходити через `session.saveResult()` (є fallback)

### Git
- Коміти: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`
- Гілки для нових фіч: `feature/назва`
- Ніколи не комітити: `.env`, `node_modules/`, `dist/`, `reports/`, `*.xlsx`

---

## Що НЕ робити

- ❌ Не змінювати `result_type` enum без міграції БД
- ❌ Не видаляти записи з БД — тільки soft delete
- ❌ Не додавати синхронні DB-виклики в async FastAPI handlers
- ❌ Не зберігати секрети у коді — тільки через `settings`
- ❌ Не змінювати `SUPERADMIN_TELEGRAM_ID` логіку — він завжди з `.env`, ніколи з БД
- ❌ Не використовувати `allow_origins=["*"]` у продакшн CORS
- ❌ Не запускати `init_db.py` повторно на існуючій БД без перевірки — перезапише дані

---

## Типові задачі

### Додати новий API ендпоінт
1. Схема в `app/schemas/`
2. Логіка в `app/api/v1/`
3. Зареєструвати роутер в `app/main.py`

### Додати новий Vue-екран
1. Компонент в `src/views/`
2. Маршрут в `src/router/index.js`
3. Посилання в `TabBar.vue` (якщо потрібна навігація)

### Змінити структуру БД
1. Змінити модель в `app/models/`
2. Оновити `init_db.py` або написати Alembic-міграцію
3. Оновити відповідні Pydantic-схеми

### Додати Celery-задачу
1. Функція в `app/tasks/`
2. Якщо за розкладом — додати до `beat_schedule` в `celery_app.py`
3. Використовувати тільки синхронний `psycopg2` для DB всередині задачі
