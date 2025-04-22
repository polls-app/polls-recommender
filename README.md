# PollsApp Recommendation Service

This repository contains the code for a personalized recommendation service used in the PollsApp web application.

## Requirements

- Python 3.10.7 or higher

## Setup

1. Create a virtual environment:
   ```
   py -m venv venv
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following structure:
   ```
   DB_DIALECT="postgresql"
   DB_DRIVER="asyncpg"
   DB_HOST="your-host"
   DB_PORT="your-port"
   DB_NAME="your-db-name"
   DB_USER="your-username"
   DB_PASSWORD="your-password"
   ```

## Running the Project

1. Navigate to the `src` directory:
   ```
   cd src
   ```

2. Start the server:
   ```
   fastapi dev main.py
   ```

## Testing

Once the server is running, you can test the endpoints using the Swagger documentation available at the URL displayed in the terminal after startup.