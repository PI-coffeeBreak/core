from fastapi import BackgroundTasks
import logging
import asyncio

logger = logging.getLogger("coffeebreak.core")

class TaskService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.background_tasks = BackgroundTasks()
        self._initialized = True

    def add_task(self, func, *args, **kwargs):
        logger.info(f"Adding task: {func.__name__}")
        return asyncio.create_task(func(*args, **kwargs))

    def get_tasks(self):
        return self.background_tasks

