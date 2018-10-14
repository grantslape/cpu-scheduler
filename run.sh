#!/bin/bash

VIRTUAL_ENV="env"

echo "Checking for existing virtual environment"
if [ ! -d "$VIRTUAL_ENV" ]; then
    echo 'No virtualenv found!'
    echo "creating virtualenv 'env' "
    python3 -m venv env
else
    echo "Virtual Environment found!"
fi

echo "activating virtual environment"
source env/bin/activate
