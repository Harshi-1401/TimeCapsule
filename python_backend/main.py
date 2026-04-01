from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from database.db import engine, Base
import models
from models import capsule
from routes import auth, rooms, tasks, admin, capsules, profile
from utils.scheduler import start_scheduler, stop_scheduler

# Create all tables on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="Time Capsule API",
    description="Time Capsule — Digital Memory Locker",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded media files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(capsules.router)
app.include_router(rooms.router)
app.include_router(tasks.router)
app.include_router(admin.router)
app.include_router(profile.router)


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "message": "Time Capsule API is running"}
