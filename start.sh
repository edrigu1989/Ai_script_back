#!/bin/bash
echo "Starting AI Script Strategist Backend..."
echo "Python version check:"
python3 --version
echo "Starting FastAPI with uvicorn..."
python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT

