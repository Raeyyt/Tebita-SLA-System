from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import auth, divisions, departments, requests, sla, me, kpis, dashboard, pdf, uploads, resources, analytics, ws, role_dashboard, notifications, users, satisfaction, settings as settings_router_module, visual_analytics

from .websocket.redis_pubsub import init_redis, start_listener, stop_listener
from .services.scheduler import start_scheduler, stop_scheduler

# Create all database tables
Base.metadata.create_all(bind=engine)

from fastapi.middleware.trustedhost import TrustedHostMiddleware

# ... imports ...

app = FastAPI(title=settings.app_name)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*"] # Update with actual domain in production
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(role_dashboard.router)
app.include_router(notifications.router)
app.include_router(divisions.router)
app.include_router(departments.router)
app.include_router(requests.router)
app.include_router(pdf.router)
app.include_router(uploads.router)
app.include_router(sla.router)
app.include_router(me.router)
app.include_router(kpis.router)
app.include_router(resources.router)
app.include_router(analytics.router)
app.include_router(satisfaction.router)
app.include_router(visual_analytics.router)
app.include_router(settings_router_module.router)
app.include_router(ws.router)



@app.on_event("startup")
async def _startup_redis_listener():
    try:
        if settings.redis_url:
            await init_redis(settings.redis_url)
            start_listener()
    except Exception:
        pass
    
    try:
        start_scheduler()
    except Exception as e:
        print(f"Failed to start scheduler: {e}")


@app.on_event("shutdown")
async def _shutdown_redis_listener():
    try:
        await stop_listener()
    except Exception:
        pass
        
    try:
        stop_scheduler()
    except Exception:
        pass


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.get("/healthz")
def healthz():
    """Health check for container orchestration"""
    return {"status": "ok"}
