from fastapi import FastAPI

from app.configs import get_environment_variables
from app.metadata.tags import Tags
from app.routers.v1.videos_router import VideosRouter


env = get_environment_variables()

app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION,
    openapi_tags=Tags,
)

app.include_router(VideosRouter)
