from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from openassistants.core.assistant import Assistant
from openassistants.functions.crud import PythonCRUD
from openassistants_fastapi.routes import RouteAssistants, create_router

from fast_api_server.find_email_by_name_function import find_email_by_name_function

app = FastAPI()

# create a library with the custom function
custom_python_lib = PythonCRUD(functions=[find_email_by_name_function])

hooli_assistant = Assistant(
    libraries=["chevy_watsonville", custom_python_lib],
    scope_description="""Only answer questions about Hooli company related matters.
You're also allowed to answer questions that refer to anything in the current chat history.""",
)

route_assistants = RouteAssistants(assistants={"hooli": hooli_assistant})

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


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}
