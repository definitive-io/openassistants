from fastapi import FastAPI
from openassistants.core.assistant import Assistant
from openassistants_fastapi.routes import RouteAssistants, create_router

app = FastAPI()

route_assistants = RouteAssistants(
    assistants={"test": Assistant(libraries=["piedpiper"])}
)

api_router = create_router(route_assistants)

app.include_router(api_router)
