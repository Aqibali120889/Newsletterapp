#!/bin/sh
# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Run the FastAPI app using the command in main.py
python main.py