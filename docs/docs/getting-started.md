---
sidebar_position: 1
---

# Getting started

Let's discover **OpenAssistants in less than 5 minutes**.

## Step 1: A simple FastAPI server based on OpenAssistants

See [code example](https://github.com/definitive-io/openassistants/blob/main/examples/fast-api-server/fast_api_server/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openassistants.core.assistant import Assistant
from openassistants_fastapi.routes import RouteAssistants, create_router

app = FastAPI()

route_assistants = RouteAssistants(
    assistants={"hooli": Assistant(libraries=["piedpiper"])}
)

# <Some CORS stuff left out for simplicity, see full code example on GitHub>

api_router = create_router(route_assistants)

app.include_router(api_router)
```

Note, by convention, libraries can be placed in the working directory of the Python app in `library/<name-of-library>`.

A FastAPI server can define multiple assistants, which one is used can be specified by the client by calling the right REST route.

## Step 2: Defining the library and Assistant

Functions are defined as YAML files in a folder (this is what we refer to as a "library" of functions). An assistant can consume multiple libraries to be able to use all functions defined across them.

A single function inside `library/piedpiper`:

```yaml
name: send_purchase_inquiry_email
display_name: Send purchase inquiry email
description: |
  send an inquiry email about a recent purchase to an employee
sample_questions:
  - send purchase inquiry email
parameters:
  json_schema:
    type: object
    properties:
      to:
        type: string
        format: email
        description: email address to send to
    required:
      - to
type: PythonEvalFunction
python_code: |
  async def main(args: dict):
    import asyncio
    yield [{"type": "text", "text": "Sending email..."}]
    await asyncio.sleep(2)
    yield [{"type": "text", "text": f"Inquiry email about recent purchase sent to: {args.get('to')}"}]
```

## Step 3: Using it through the UI

Once the functions have been defined we can connect to the REST API using the default UI client.

Simply start the Next.js app that points to the REST endpoint:

```bash
cd examples/next
yarn run dev
```

![UI](/img/openassistants.png)
