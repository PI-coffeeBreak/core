from fastapi.middleware.gzip import GZipMiddleware
from dependencies.app import get_current_app
from constants.gzip import GZIP_MINIMUM_SIZE

app = get_current_app()

app.add_middleware(GZipMiddleware, minimum_size=GZIP_MINIMUM_SIZE)