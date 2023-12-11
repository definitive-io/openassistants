#!/usr/bin/env bash

uvicorn fast_api_server.main:app --reload --reload-include='*.yaml' --reload-include='*.py'
