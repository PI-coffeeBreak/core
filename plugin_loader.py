import os
import importlib.util
from fastapi import APIRouter
import logging
import asyncio
from utils.api import Router
from typing import List, Tuple, Optional

logger = logging.getLogger("coffeebreak.core")

plugins_modules = {}
registered_plugins = {}

required_attributes = ['REGISTER']


def _is_valid_plugin_directory(dirname: str) -> bool:
    """Check if a directory is a valid plugin directory"""
    return (
        dirname != '__pycache__' and
        not dirname.endswith('.disabled')
    )


def _load_plugin_module(plugins_dir: str, plugin_name: str) -> Optional[Tuple[str, object]]:
    """Load a plugin module from file"""
    package_path = os.path.join(plugins_dir, plugin_name)
    init_file = os.path.join(package_path, '__init__.py')

    if not os.path.exists(init_file):
        return None

    spec = importlib.util.spec_from_file_location(
        package_path.replace("/", "."), init_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    missing_attrs = [
        attr for attr in required_attributes if not hasattr(module, attr)]
    if missing_attrs:
        logger.warning(
            f"Plugin {plugin_name} is missing required attributes: {', '.join(missing_attrs)} and will not be loaded")
        return None

    if not hasattr(module, 'UNREGISTER'):
        logger.warning(
            f"Plugin {plugin_name} does not have a UNREGISTER method")

    return plugin_name, module


def _get_plugin_directories(plugins_dir: str) -> List[str]:
    """Get list of valid plugin directories"""
    return [
        filename for filename in os.listdir(plugins_dir)
        if os.path.isdir(os.path.join(plugins_dir, filename)) and
        _is_valid_plugin_directory(filename)
    ]


async def plugin_loader(plugins_dir: str, app: APIRouter) -> None:
    """Load all plugins from the plugins directory"""
    plugin_dirs = _get_plugin_directories(plugins_dir)
    load_tasks = []

    for plugin_dir in plugin_dirs:
        result = _load_plugin_module(plugins_dir, plugin_dir)
        if result:
            plugin_name, module = result
            plugins_modules[plugin_name] = module
            logger.debug(f"Loading plugin {plugin_name}")
            load_tasks.append(load_plugin(app, plugin_name))

    if load_tasks:
        results = await asyncio.gather(*load_tasks)
        logger.info(
            f"Loaded {sum(1 for r in results if r)} plugins successfully")


async def plugin_unloader(app: APIRouter) -> None:
    """Unload all loaded plugins"""
    logger.debug("Unloading plugins...")
    unload_tasks = [
        unload_plugin(app, plugin_name)
        for plugin_name in list(registered_plugins.keys())
    ]

    if unload_tasks:
        await asyncio.gather(*unload_tasks)

    _log_remaining_routes(app)


def _log_remaining_routes(app: APIRouter) -> None:
    """Log routes that remain after unloading plugins"""
    logger.info("Remaining routes after unloading plugins:")
    for route in app.routes:
        logger.info(
            f"  - {route.path} [{route.methods if hasattr(route, 'methods') else 'WebSocket'}]")


async def _register_plugin(module) -> None:
    """Register a plugin using its REGISTER function"""
    if asyncio.iscoroutinefunction(module.REGISTER):
        await module.REGISTER()
    else:
        module.REGISTER()


def _setup_plugin_router(app: APIRouter, plugin_name: str, module) -> None:
    """Setup router for a plugin if it has one"""
    if not hasattr(module, 'router') or not module.router:
        return

    if not isinstance(module.router, Router):
        return

    router = module.router.get_router()
    prefix = f"/{plugin_name}"
    tag = plugin_name.replace("_", " ").replace("-", " ").title()

    logger.debug(
        f"Loading plugin router {plugin_name} with prefix {prefix} and tag {tag}")
    app.include_router(router, prefix=prefix, tags=[tag])


async def load_plugin(app: APIRouter, plugin_name: str) -> bool:
    """Load a single plugin"""
    if plugin_name not in plugins_modules or plugin_name in registered_plugins:
        return False

    module = plugins_modules[plugin_name]
    await _register_plugin(module)
    _setup_plugin_router(app, plugin_name, module)
    registered_plugins[plugin_name] = module

    return True


async def _unregister_plugin(module) -> None:
    """Unregister a plugin using its UNREGISTER function"""
    if not hasattr(module, 'UNREGISTER'):
        return

    if asyncio.iscoroutinefunction(module.UNREGISTER):
        await module.UNREGISTER()
    else:
        module.UNREGISTER()


def _remove_plugin_routes(app: APIRouter, module) -> None:
    """Remove routes associated with a plugin"""
    if not hasattr(module, 'router'):
        return

    router = module.router.get_router()
    app.routes = [route for route in app.routes if route not in router.routes]


async def unload_plugin(app: APIRouter, plugin_name: str) -> bool:
    """Unload a single plugin"""
    if plugin_name not in registered_plugins:
        logger.warning(f"Plugin {plugin_name} not found")
        return False

    module = registered_plugins.pop(plugin_name)
    await _unregister_plugin(module)
    _remove_plugin_routes(app, module)

    logger.info(f"Unloaded plugin {plugin_name}")
    return True
