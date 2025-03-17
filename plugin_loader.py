import os
import importlib.util
from fastapi import FastAPI
import logging
from utils.api import Router

logger = logging.getLogger("coffeebreak.core")


def plugin_loader(plugins_dir, app: FastAPI):
    for filename in os.listdir(plugins_dir):
        if os.path.isdir(os.path.join(plugins_dir, filename)) and filename != '__pycache__' and filename[-9:] != '.disabled':
            package_path = os.path.join(plugins_dir, filename)
            init_file = os.path.join(package_path, '__init__.py')
            if os.path.exists(init_file):
                spec = importlib.util.spec_from_file_location(
                    filename, init_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'router'):
                    router = module.router.get_router()
                    if router and isinstance(router, Router):
                        prefix = f"/{filename}"
                        tag = f"{filename}".capitalize()
                        logger.info(
                            f"Loading plugin {filename} with prefix {prefix} and tag {tag}")
                        app.include_router(router, prefix=prefix, tags=[tag])
