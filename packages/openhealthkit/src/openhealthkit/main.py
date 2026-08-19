from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from openhealthkit import __version__
from openhealthkit.api import v1_router
from openhealthkit.config import settings
from openhealthkit.database import init_db
from openhealthkit.plugins import ConsoleNotificationPlugin, plugin_manager
from openhealthkit.utils.logger import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


import time
from collections import defaultdict

from fastapi.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        # Clean up old timestamps outside window
        window_start = now - self.window_seconds
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > window_start
        ]

        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please wait before retrying."},
            )

        self.requests[client_ip].append(now)
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing OpenHealthKit database & plugins...")
    await init_db()

    # Register default console notification plugin
    plugin_manager.register_plugin(ConsoleNotificationPlugin())

    # Seed initial roles and admin user if needed
    from sqlalchemy.future import select

    from openhealthkit.database import AsyncSessionLocal
    from openhealthkit.models import Role, User
    from openhealthkit.utils.security import hash_password

    async with AsyncSessionLocal() as session:
        # Check permissions & roles
        res = await session.execute(select(Role).where(Role.name == "ADMIN"))
        admin_role = res.scalars().first()
        if not admin_role:
            admin_role = Role(name="ADMIN", description="System Administrator")
            worker_role = Role(name="HEALTH_WORKER", description="Community Health Worker")
            analyst_role = Role(name="ANALYST", description="Public Health Analyst")
            viewer_role = Role(name="VIEWER", description="Read-only Viewer")
            session.add_all([admin_role, worker_role, analyst_role, viewer_role])
            await session.commit()
            await session.refresh(admin_role)

        # Check default admin user
        user_res = await session.execute(select(User).where(User.username == "admin"))
        if not user_res.scalars().first():
            admin_user = User(
                username="admin",
                email=settings.INITIAL_ADMIN_EMAIL,
                hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                full_name="OpenHealthKit Admin",
            )
            admin_user.roles.append(admin_role)
            session.add(admin_user)
            await session.commit()
            logger.info(
                f"Created default admin user: username='admin' email='{settings.INITIAL_ADMIN_EMAIL}'"
            )

    logger.info("OpenHealthKit API Ready.")
    yield
    logger.info("Shutting down OpenHealthKit API...")


app = FastAPI(
    title="OpenHealthKit API",
    description=(
        "An offline-first open-source developer toolkit for building resilient "
        "community and public-health applications."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

class I18nMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        accept_lang = request.headers.get("Accept-Language", "en")
        primary_lang = accept_lang.split(",")[0].split("-")[0].strip()
        request.state.locale = primary_lang
        response = await call_next(request)
        response.headers["Content-Language"] = primary_lang
        return response


# Add Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(I18nMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router under /api
app.include_router(v1_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "title": "OpenHealthKit API",
        "tagline": "An offline-first open-source toolkit for building resilient community and public-health applications.",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
