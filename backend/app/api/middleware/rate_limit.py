from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from app.config import settings

# Ліміти за маршрутам
RATE_LIMITS = {
    "/api/v1/sessions": (60, 60),     # 60 зап/хв — збереження результатів
    "/api/v1/reports": (10, 60),      # 10 зап/хв — звіти
}
DEFAULT_LIMIT = (120, 60)            # 120 зап/хв — для решти маршрутів

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-базовий Rate Limiter.
    Ключ — telegram_id з JWT або IP-адреса (для неавторизованих запитів).
    Повертає HTTP 429 при перевищенні ліміту.
    """

    async def dispatch(self, request: Request, call_next):
        # Пропускаємо health-check без обмежень
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        # Визначаємо ідентифікатор користувача
        identifier = self._get_identifier(request)

        # Визначаємо ліміт для поточного маршруту
        max_requests, window = DEFAULT_LIMIT
        for path_prefix, limits in RATE_LIMITS.items():
            if request.url.path.startswith(path_prefix):
                max_requests, window = limits
                break

        key = f"rate:{identifier}:{request.url.path.split('/')[3]}" if len(request.url.path.split('/')) > 3 else f"rate:{identifier}:{request.url.path}"

        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, window)

        if count > max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Перевищено ліміт запитів. Спробуйте через {window} сек.",
            )

        return await call_next(request)

    @staticmethod
    def _get_identifier(request: Request) -> str:
        """JWT sub (основний) або IP (запасний)."""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            try:
                from app.services.auth_service import decode_token
                payload = decode_token(auth.split(" ")[1])
                if payload:
                    return f"user:{payload['sub']}"
            except Exception:
                pass
        return f"ip:{request.client.host}"
