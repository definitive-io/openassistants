#!/bin/bash

trap "exit" INT TERM ERR
trap "kill 0" EXIT

(
  cd examples/fast-api-server
  poetry run ./run.sh
) &

(
  cd examples/next
  yarn dev
) &

wait

