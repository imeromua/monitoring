from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, catalog, stores, sessions, results, reports
from app.api.v1.admin import users as admin_users
from app.api.v1.admin import stores as admin_stores
from app.api.v1.admin import catalog as admin_catalog
from app.api.v1.admin import reports_archive as admin_reports_archive
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.config import settings

app = FastAPI(
    title="Store Check API",
    description="Система автоматизації конкурентного цінового моніторингу",
    version="1.0.0",
)

# Middleware (порядок важливий: Rate Limit → CORS)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(catalog.router, prefix=API_PREFIX)
app.include_router(stores.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)
app.include_router(results.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(admin_users.router, prefix=API_PREFIX)
app.include_router(admin_stores.router, prefix=API_PREFIX)
app.include_router(admin_catalog.router, prefix=API_PREFIX)
app.include_router(admin_reports_archive.router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
