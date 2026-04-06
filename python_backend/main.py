from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy import text
import os

from database.db import engine, Base
import models
from models import capsule
from routes import auth, rooms, tasks, admin, capsules, profile
from utils.scheduler import start_scheduler, stop_scheduler

# Create all tables on startup
Base.metadata.create_all(bind=engine)


def run_migrations():
    """Add any missing columns that were added after initial deployment."""
    with engine.connect() as conn:
        # Add media_filename column if missing
        try:
            conn.execute(text("ALTER TABLE capsules ADD COLUMN media_filename VARCHAR(255)"))
            conn.commit()
            print("✅ Migration: added media_filename column")
        except Exception:
            pass  # Column already exists

        # Add profile_image column to users if missing
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN profile_image VARCHAR(500)"))
            conn.commit()
            print("✅ Migration: added profile_image column")
        except Exception:
            pass  # Column already exists


# Run migrations immediately at startup (not just in lifespan)
run_migrations()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Time Capsule API",
    description="Time Capsule — Digital Memory Locker",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://time-capsule-six-coral.vercel.app",
    ],
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
