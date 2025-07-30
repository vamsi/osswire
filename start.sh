#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Run the seed script if database doesn't exist
if [ ! -f "osswire.db" ]; then
    echo "Seeding database..."
    python seed.py
fi

# Start the application
echo "Starting OSSWire..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 