from dotenv import load_dotenv
import os
import fcntl
import tempfile
import time

# Load environment variables from .env file
load_dotenv()

import asyncio
from fastapi import FastAPI, Request, Response
import logging
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader
from dependencies.app import set_current_app
from dependencies.database import engine, Base
from swagger import configure_swagger_ui
from plugin_loader import plugin_unloader
from defaults import initialize_defaults
from sqlalchemy.exc import OperationalError

logger = logging.getLogger("coffeebreak")

app = FastAPI(root_path="/api/v1", openapi_prefix="/api/v1")
set_current_app(app)

import middlewares # setup middlewares here

from routes import routes_app

def acquire_lock(lock_name: str) -> tuple[bool, int | None]:
    """
    Acquire a file lock to ensure only one worker executes a specific operation
    
    Args:
        lock_name: Name of the lock (will be used to create the lock file)
    
    Returns:
        tuple[bool, int | None]: (success, file_descriptor)
            - success: True if lock was acquired, False otherwise
            - file_descriptor: The file descriptor if lock was acquired, None otherwise
    """
    lock_file = os.path.join(tempfile.gettempdir(), f'coffeebreak_{lock_name}.lock')
    lock_fd = open(lock_file, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True, lock_fd
    except IOError:
        # Another worker has the lock
        lock_fd.close()
        return False, None

def acquire_db_lock():
    """Acquire a file lock to ensure only one worker initializes the database"""
    success, lock_fd = acquire_lock('db')
    return lock_fd

def acquire_defaults_lock():
    """Acquire a file lock to ensure only one worker initializes the defaults"""
    success, lock_fd = acquire_lock('defaults')
    return lock_fd

def wait_for_defaults_initialization():
    """Wait for defaults initialization to complete by checking a flag file"""
    flag_file = os.path.join(tempfile.gettempdir(), 'coffeebreak_defaults.initialized')
    while not os.path.exists(flag_file):
        time.sleep(0.1)  # Small delay to avoid busy waiting

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all plugins first
    await plugin_loader('plugins', routes_app)

    # Try to acquire the database lock
    lock_fd = acquire_db_lock()
    
    if lock_fd is not None:
        try:
            # Create tables with checkfirst=True to avoid errors with existing objects
            Base.metadata.create_all(bind=engine, checkfirst=True)
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            raise RuntimeError("Could not connect to the database")
        except Exception as e:
            logger.error(f"Error managing database tables: {e}")
            raise RuntimeError(f"Error managing database tables: {str(e)}")
        finally:
            # Release the lock
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
    else:
        logger.info("Another worker is initializing the database, skipping...")

    # Include all routers from routes/__init__.py after plugins
    app.include_router(routes_app)

    # Configure Swagger UI after all routes are registered
    configure_swagger_ui(app)

    # Initialize default configurations with lock
    defaults_lock_fd = acquire_defaults_lock()
    flag_file = os.path.join(tempfile.gettempdir(), 'coffeebreak_defaults.initialized')
    
    if defaults_lock_fd is not None:
        try:
            logger.info("Starting defaults initialization...")
            await initialize_defaults()
            # Create flag file to indicate initialization is complete
            with open(flag_file, 'w') as f:
                f.write(str(time.time()))
            logger.info("Defaults initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing defaults: {e}")
            raise RuntimeError(f"Error initializing defaults: {str(e)}")
        finally:
            # Release the lock
            fcntl.flock(defaults_lock_fd, fcntl.LOCK_UN)
            defaults_lock_fd.close()
    else:
        logger.info("Waiting for defaults initialization to complete...")
        wait_for_defaults_initialization()
        logger.info("Defaults initialization completed by another worker")

    # Log all available routes
    for route in routes_app.routes:
        logger.debug(
            f"Route: {route.path} [{route.methods if hasattr(route, 'methods') else 'WebSocket'}]")

    try:
        yield
    finally:
        await plugin_unloader(routes_app)


app.router.lifespan_context = lifespan

# Start the application with:
# uvicorn main:app --reload --log-config logging_config.json
# Additional configuration:
# --env-file <env_file>

# For production, use:
# gunicorn main:app -k uvicorn.workers.UvicornWorker -w <N_WORKERS> -b <HOST>:<PORT> --log-config-json logging_config.json
