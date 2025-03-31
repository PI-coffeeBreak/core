# CoffeeBreak Core

The CoffeeBreak Core is the backend service for the CoffeeBreak application. It provides APIs, middleware, and database integration to support the application's functionality.
It includes a dynamic plugin system for adding new features or integrating external systems.
## Features

- **FastAPI Framework**: Built with FastAPI for high performance and easy-to-use APIs.
- **Database Integration**: Supports both SQL (via SQLAlchemy) and MongoDB for data storage.
- **Custom Middleware**: Includes logging and CORS middleware for enhanced functionality.
- **Dynamic Plugin System**: Allows loading and managing plugins dynamically.
- **Default UI Configurations**: Automatically creates default main menu and color themes if not present.
- **Swagger UI**: Provides interactive API documentation.

## Project Structure

- **`dependencies/`**: Contains modules for database and application dependencies.
- **`models/`**: Defines data models for the application.
- **`schemas/`**: Defines pydantic schemas.
- **`routes/`**: Includes API route definitions.
- **`plugins/`**: Directory for dynamically loaded plugins.

## Setup Instructions

### Prerequisites

- Python 3.12
- MongoDB and SQL database
- Keycloak server

_**Note**: See the orchestrator repository to know more_

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd core
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Create a `.env` file with necessary configurations (e.g., database URLs, Keycloak credentials).

4. Initialize the database:
   ```bash
   python -m dependencies.database
   ```

### Running the Application

Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload --log-config logging_config.json --env-file .env
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Adding Plugins

1. Place your plugin in the `plugins/` directory.
2. Ensure the plugin follows the expected structure and is loaded dynamically.

See [Docs](docs/) for more information.

### Modifying Default Configurations

- Update the `create_default_main_menu` and `create_default_color_theme` functions in `main.py` to modify default UI configurations.

## Logging

You can configure logging by modifying the `logging_config.json` file.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request.

