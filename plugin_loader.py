import os
import importlib.util
from fastapi import APIRouter
import logging
import asyncio
from utils.api import Router

logger = logging.getLogger("coffeebreak.core")

plugins_modules = {}
registered_plugins = {}

required_attributes = ['REGISTER']

def plugin_loader(plugins_dir, app: APIRouter):
    """
    Load all plugins from the plugins directory.
    This is now an async function that properly awaits the tasks.
    """
    # Create a list to hold the load plugin tasks
    load_tasks = []
    
    for filename in os.listdir(plugins_dir):
        if os.path.isdir(os.path.join(plugins_dir, filename)) and filename != '__pycache__' and filename[-9:] != '.disabled':
            package_path = os.path.join(plugins_dir, filename)
            init_file = os.path.join(package_path, '__init__.py')
            if os.path.exists(init_file):
                spec = importlib.util.spec_from_file_location(
                    package_path.replace("/", "."), init_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                missing_attrs = [attr for attr in required_attributes if not hasattr(module, attr)]
                if missing_attrs:
                    logger.warning(
                        f"Plugin {filename} is missing required attributes: {', '.join(missing_attrs)} and will not be loaded")
                    continue
                if not hasattr(module, 'UNREGISTER'):
                    logger.warning(
                        f"Plugin {filename} does not have a UNREGISTER method")
                plugins_modules[filename] = module
                
                logging.debug(f"Loading plugin {filename} from {package_path}")
                loop = asyncio.get_event_loop()
                task = loop.create_task(load_plugin(app, filename))
                load_tasks.append(task)


async def plugin_unloader(app: APIRouter):
    """
    Unload all loaded plugins.
    This is now an async function that properly awaits the tasks.
    """
    logger.debug("Unloading plugins...")
    # Create a list to hold the unload plugin tasks
    unload_tasks = []
    
    for plugin_name in list(registered_plugins.keys()):
        task = unload_plugin(app, plugin_name)
        unload_tasks.append(task)

    # Wait for all plugins to finish unloading
    if unload_tasks:
        await asyncio.gather(*unload_tasks)


async def load_plugin(app: APIRouter, plugin_name) -> bool:
    if plugin_name not in plugins_modules or plugin_name in registered_plugins:
        return False
    module = plugins_modules[plugin_name]
    
    # Handle both async and sync REGISTER functions
    if asyncio.iscoroutinefunction(module.REGISTER):
        await module.REGISTER()
    else:
        module.REGISTER()
        
    if hasattr(module, 'router'):
        if module.router and isinstance(module.router, Router):
            logger.debug(f"Router: {module.router}")
            router = module.router.get_router()
            prefix = f"/{plugin_name}"
            tag = f"{plugin_name}".replace("_", " ").replace("-", " ").title()
            logger.debug(f"Loading plugin router {plugin_name} with prefix {prefix} and tag {tag}: {router}")
            app.include_router(router, prefix=prefix, tags=[tag])
            registered_plugins[plugin_name] = module
    else:
        registered_plugins[plugin_name] = module
    return True


async def unload_plugin(app: APIRouter, plugin_name: str) -> bool:
    if plugin_name in registered_plugins:
        module = registered_plugins.pop(plugin_name)
        if hasattr(module, 'UNREGISTER'):
            if asyncio.iscoroutinefunction(module.UNREGISTER):
                await module.UNREGISTER()
            else:
                module.UNREGISTER()
        if hasattr(module, 'router'):
            router = module.router.get_router()
            app.router.routes = [route for route in app.router.routes if route not in router.routes]
        logger.info(f"Unloaded plugin {plugin_name}")
        return True
    logger.warning(f"Plugin {plugin_name} not found")
    return False