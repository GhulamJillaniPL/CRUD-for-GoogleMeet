# Google Meet Management API

A FastAPI application for managing Google Meet meetings through the Google Calendar API. This service allows you to create, read, update, and delete Google Meet meetings programmatically.

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package manager)
3. Google Cloud Platform account
4. Google Calendar API enabled
5. OAuth 2.0 credentials configured

## Google Cloud Platform Setup

1. Go to the Google Cloud Console (https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   ```bash
   # Navigate to APIs & Services > Library
   # Search for "Google Calendar API"
   # Click Enable
   ```
4. Create OAuth 2.0 credentials:
   ```bash
   # Go to APIs & Services > Credentials
   # Click Create Credentials > OAuth client ID
   # Select Desktop Application
   # Download the JSON file and rename it to credentials.json
   ```

## Installation on Linux

1. Update system packages:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. Create and navigate to project directory:
   ```bash
   mkdir google-meet-api
   cd google-meet-api
   ```

3. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Create project structure:
   ```bash
   mkdir -p app/api app/services
   touch app/api/__init__.py app/api/endpoints.py
   touch app/services/__init__.py app/services/google_meet_service.py
   touch app/__init__.py app/config.py app/main.py app/models.py
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Configure environment:
   ```bash
   # Create .env file
   echo "google_credentials_file=credentials.json" > .env
   
   # Move your downloaded credentials.