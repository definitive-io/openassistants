from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openassistants.core.assistant import Assistant
from openassistants_fastapi.routes import RouteAssistants, create_router

app = FastAPI()

route_assistants = RouteAssistants(
    assistants={"hooli": Assistant(libraries=["piedpiper"])}
)

api_router = create_router(route_assistants)

# IMPORTANT! Do not ship this to production! You should be more restrictive
# https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router)
