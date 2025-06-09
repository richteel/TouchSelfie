#!/bin/bash

VENV_DIR="/home/pi/photobooth"  # Change this to your virtual environment directory

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment exists."
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
echo "Virtual environment activated!"


cd scripts/
python setup.py

deactivate
