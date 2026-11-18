import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db
from app.db.seed import seed_data
from app.api.v1.router import api_v1_router
from app.api.v1.websocket import router as ws_router
from app.api.v1.dashboard import router as dashboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        await seed_data()
    except Exception as e:
        print(f'Seed note: {e}')
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description='Enterprise Fleet Management & Telemetry API for Kerala NH-66 Freight Operations',
    version='2.0.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, 'pod'), exist_ok=True)
app.mount('/uploads', StaticFiles(directory=settings.UPLOAD_DIR), name='uploads')

app.include_router(dashboard_router)
app.include_router(api_v1_router)
app.include_router(ws_router)

@app.get('/health', tags=['Health & Diagnostics'])
async def health_check():
    return {
        'status': 'healthy',
        'service': settings.PROJECT_NAME,
        'version': '2.0.0',
        'database': 'sqlite_aiosqlite (dual-engine active)'
    }

@app.get('/', tags=['Root'])
async def root():
    return {
        'name': settings.PROJECT_NAME,
        'docs': '/docs',
        'admin_dashboard': '/admin',
        'health': '/health',
        'telemetry_ws': '/ws/v1/fleet'
    }
