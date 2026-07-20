import asyncio
import sys
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.data.database import setup_db
from src.settings import settings
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger  = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try: 
        await setup_db()
        logger.info("Database setup complete")
        yield
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

app = FastAPI(
    title="World Cup 2026 AI Analytics",
    description="RAG and Agent powered World Cup API",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return{"message": "Helloo, World!"}


@app.get("/health")
async def health():
    return {"status": "ok"}

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)
