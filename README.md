# OpenAssistants

[![Documentation](https://img.shields.io/badge/docs-openassistants-blue.svg)](https://definitive-io.github.io/openassistants/)
[![OpenAssistants PyPI](https://img.shields.io/pypi/v/openassistants.svg)](https://pypi.org/project/openassistants/)
[![OpenAssistants-FastAPI PyPI](https://img.shields.io/pypi/v/openassistants-fastapi.svg)](https://pypi.org/project/openassistants-fastapi/)
[![npm version](https://img.shields.io/npm/v/@definitive-io/openassistants-ui)](https://www.npmjs.com/package/@definitive-io/openassistants-ui)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/discord/1182644873992613989.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/Snd4Cry7wD)


OpenAssistants is a collection of open source libraries aimed at developing robust AI assistants rather than autonomous agents. By focusing on specific tasks and incorporating human oversight, OpenAssistants strives to minimize error rates typically found in agentic systems.

- `openassistants` the core library responsible for the main function calling / message generating runtime
- `openassistants-fastapi` a set of FastAPI routes used for interacting with the core runtime loop through a REST API
- `openassistants-ui` an example chat client that supports rich streaming outputs like tables, plots, form inputs and text.

OpenAssistants is built on [LangChain](https://github.com/langchain-ai/langchain) and designed to be an open alternative to OpenAI's [Assistants API](https://platform.openai.com/docs/assistants/overview). We also think it's easier to use!

Join us in creating AI assistants that are not only useful but dependable for production use today.

## Features
- Included Chat UI
- Support function calling with any LLM (open source & proprietary)
- Declarative library of functions
- Built-in SQL functions (DuckDB support)
- Extend with any custom Python function
- Support for 50+ functions in a single chat Assistant
- Native OpenAI Functions integration

<br>
<p align="center">
<br>
 <img src="https://github.com/definitive-io/openassistants/assets/1309307/3e7821f4-62d8-42c0-80c7-94be8b3f2e2c" />
 <br><i>OpenAssistants UI</i>
</p>

## Quick Start

To run the project locally:

- Navigate to `examples/fast-api-server` to start the **backend** example:
  - Run `poetry install`
  - Activate the virtual environment with `poetry shell`
  - Start the server with `./run.sh`

- Then, go to `examples/next` to start the **frontend** example:
  - Install dependencies with `yarn install`
  - Launch the development server with `yarn run dev`
  - Access the application at `localhost:3000`

Join our community and start contributing today!
