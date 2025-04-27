from fastapi.middleware.cors import CORSMiddleware
from dependencies.app import get_current_app
import os

origins = os.getenv('CORS_ORIGINS', 'http://localhost').split(',')

app = get_current_app()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
