#!/usr/bin/env bash

uvicorn fast_api_server.main:app --reload --reload-dir='../../packages/openassistants' --reload-dir="." --reload-include='*.yaml' --reload-include='*.py'