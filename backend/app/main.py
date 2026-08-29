from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import load_settings
from app.services.dashboard import DashboardService


app = FastAPI(
    title="Kalshi Weather Dashboard API",
    version="1.0.0",
    description="Read-only NYC weather and prediction-market analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

service = DashboardService(load_settings())


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard")
def dashboard() -> dict:
    try:
        return asdict(service.build())
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="The live data providers could not be reached. Try again later.",
        ) from error
