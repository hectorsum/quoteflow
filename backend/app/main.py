from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.core.config import settings
from app.core.database import init_db
from app.graph.builder import build_graph
from app.api.routes.quotes import router as quotes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # AsyncSqliteSaver debe abrirse como context manager y mantenerse vivo
    # durante toda la vida de la app para que el checkpointer funcione.
    async with AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path) as checkpointer:
        app.state.graph = build_graph(checkpointer)
        yield


app = FastAPI(
    title="QuoteFlow API",
    description="Sistema agéntico de cotizaciones B2B — AndesPro Industrial",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "quoteflow-api"}
