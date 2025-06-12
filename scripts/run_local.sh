#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")/.."

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r app/requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Run the application using streamlit directly
echo "Starting Menu Maestro..."
cd app
streamlit run app.py