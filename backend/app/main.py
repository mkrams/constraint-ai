"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import items, parameters, traces, constraints, engine, tracespace


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle."""
    init_db()
    print("Database initialized")

    # Auto-seed: run if empty OR if FORCE_RESEED is set
    auto_seed = os.getenv("AUTO_SEED", "false").lower() == "true"
    force_reseed = os.getenv("FORCE_RESEED", "false").lower() == "true"

    if auto_seed or force_reseed:
        from app.database import SessionLocal
        from app.models.models import Item
        db = SessionLocal()
        try:
            item_count = db.query(Item).count()
            if item_count == 0 or force_reseed:
                reason = "FORCE_RESEED enabled" if force_reseed else "Empty database detected"
                print(f"{reason}, running seed...")
                db.close()
                import subprocess
                subprocess.run(["python", "seed.py"], check=True)
                print("Seed complete")
            else:
                db.close()
        except Exception as e:
            print(f"Seed check failed (non-fatal): {e}")
            db.close()

    yield


app = FastAPI(
    title="Constraint AI Backend",
    description="Engineering Constraint Graph Application API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Vercel frontend
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # all Vercel preview deploys
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router)
app.include_router(parameters.router)
app.include_router(traces.router)
app.include_router(constraints.router)
app.include_router(engine.router)
app.include_router(tracespace.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Constraint AI Backend", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"message": "Constraint AI Backend", "docs": "/docs", "openapi_schema": "/openapi.json"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
