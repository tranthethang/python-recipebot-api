from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.recipe_routes import router as recipe_router
from app.utils.logger_config import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("RecipeBot API starting up")
    yield
    logger.info("RecipeBot API shutting down")


app = FastAPI(
    title="RecipeBot API",
    description="AI-powered recipe recommendations from ingredients",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(recipe_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RecipeBot API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)