#!/bin/bash

# Navigate to the backend directory
cd backend

# Check if the virtual environment already exists
if [ ! -d ".venv" ]; then
  # Create a virtual environment if it doesn't exist
  python -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

# Navigate back to the project root directory
cd ..

# Navigate to the frontend directory
cd frontend/briefbox-front

# Install the frontend dependencies
npm install

# Navigate back to the project root directory
cd ../..

# Run the start_app.sh script
./start.sh