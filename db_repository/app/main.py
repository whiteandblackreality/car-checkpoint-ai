from fastapi import FastAPI

from configs import get_environment_variables
from metadata.tags import Tags
from models import init
from routers.v1.cars_router import CarsRouter
from routers.v1.entries_router import EntriesRouter
from routers.v1.cameras_router import CamerasRouter

env = get_environment_variables()

app = FastAPI(
    title=env.APP_NAME,
    version=env.API_VERSION,
    openapi_tags=Tags,
)

app.include_router(CarsRouter)
app.include_router(EntriesRouter)
app.include_router(CamerasRouter)

init()
