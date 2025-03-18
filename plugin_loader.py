import os
import importlib.util
from fastapi import FastAPI
import logging
from utils.api import Router

logger = logging.getLogger("coffeebreak.core")

loaded_plugins = {}

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
                if hasattr(module, 'REGISTER'):
                    module.REGISTER()
                    if hasattr(module, 'router'):
                        router = module.router.get_router()
                        if router and isinstance(router, Router):
                            prefix = f"/{filename}"
                            tag = f"{filename}".capitalize()
                            logger.info(
                                f"Loading plugin {filename} with prefix {prefix} and tag {tag}")
                            app.include_router(router, prefix=prefix, tags=[tag])
                            loaded_plugins[filename] = module
                else:
                    logger.warning(f"Plugin {filename} does not have a REGISTER method and will not be loaded")

def unload_plugin(app: FastAPI, plugin_name: str):
    if plugin_name in loaded_plugins:
        module = loaded_plugins.pop(plugin_name)
        if hasattr(module, 'UNREGISTER'):
            module.UNREGISTER()
        if hasattr(module, 'router'):
            router = module.router.get_router()
            app.router.routes = [route for route in app.router.routes if route not in router.routes]
        logger.info(f"Unloaded plugin {plugin_name}")
    else:
        logger.warning(f"Plugin {plugin_name} not found")
