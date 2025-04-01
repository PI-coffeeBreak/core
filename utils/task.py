from fastapi import BackgroundTasks

class TaskService:
    def __init__(self):
        self.background_tasks = BackgroundTasks()

    def add_task(self, func, *args, **kwargs):
        self.background_tasks.add_task(func, *args, **kwargs)

    def get_tasks(self):
        return self.background_tasks

