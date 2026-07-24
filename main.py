from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.health import router as health_router
from src.api.routers.prediction import router as prediction_router

from src.config.settings import get_settings
from src.config.container import Container

container = Container()

from utils.logger import get_logger
from uuid import UUID

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):

    container.init_resources()

    logger.info(container)

    model_loader = container.model_loader()
    await model_loader.load()
    
    # logger.info(f"Models loaded: {model_loader.model}, schema: {model_loader.schema}, metadata: {model_loader.metadata}")

    # await database.create_tables()

    # inference = container.inference()

    # data = {
    #      "credit_score": 700,
    #     "geography": "Germany",
    #     "gender": "male",
    #     "age": 41,
    #     "balance": 12000,
    #     "is_active_member": True
    # }

    # await inference.predict(data)

    app.state.container = container

    try:
        yield

    finally:
        container.shutdown_resources


import src
container = Container()

container.wire(
    modules=[
        src.api.routers.prediction

    ]
)


settings = get_settings()



app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug="info",
    lifespan=lifespan
)



app.include_router(health_router)
app.include_router(prediction_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        port=8000,
        host="0.0.0.0",
        log_level="debug"
    )