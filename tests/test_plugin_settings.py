import asyncio
import sys
from pathlib import Path

# Add the project directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.ui.plugin_settings import (
    create_plugin_setting,
    get_plugin_setting_by_title,
    delete_plugin_setting_by_title
)
from schemas.plugin_setting import PluginSetting, SelectorInput, TextInput, ShortTextInput, CheckboxInput, ComposedTextInput
from dependencies.mongodb import db

async def setup():
    # Setup: Clear the plugin_settings collection before each test
    await db['plugin_settings'].delete_many({})
    print("Setup: Cleared the plugin_settings collection")

async def teardown():
    # Teardown: Clear the plugin_settings collection after each test
    await db['plugin_settings'].delete_many({})
    print("Teardown: Cleared the plugin_settings collection")

async def test_create_plugin_setting():
    plugin_setting = PluginSetting(
        title="Plugin Name",
        description="Plugin Description",
        inputs=[
            SelectorInput(type="selector", title="title", description="description", options=["op1", "op2", "op3"]),
            TextInput(type="text", title="title"),
            ShortTextInput(type="shortText", title="title"),
            CheckboxInput(type="checkbox", kind=["multiple", "single", "toggle"], title="title", options=["op1", "op2", "op3"]),
            ComposedTextInput(type="composedText", title="title", name="name", description="description")
        ]
    )
    created_plugin_setting = await create_plugin_setting(plugin_setting)
    assert created_plugin_setting.title == "Plugin Name", f"Expected title 'Plugin Name', got {created_plugin_setting.title}"
    print("test_create_plugin_setting: Passed")

async def test_get_plugin_setting_by_title():
    # First, create a plugin setting
    plugin_setting = PluginSetting(
        title="Plugin Name",
        description="Plugin Description",
        inputs=[
            SelectorInput(type="selector", title="title", description="description", options=["op1", "op2", "op3"]),
            TextInput(type="text", title="title"),
            ShortTextInput(type="shortText", title="title"),
            CheckboxInput(type="checkbox", kind=["multiple", "single", "toggle"], title="title", options=["op1", "op2", "op3"]),
            ComposedTextInput(type="composedText", title="title", name="name", description="description")
        ]
    )
    await create_plugin_setting(plugin_setting)
    # Then, get the plugin setting by title
    retrieved_plugin_setting = await get_plugin_setting_by_title("Plugin Name")
    assert retrieved_plugin_setting.title == "Plugin Name", f"Expected title 'Plugin Name', got {retrieved_plugin_setting.title}"
    print("test_get_plugin_setting_by_title: Passed")

async def test_delete_plugin_setting():
    # First, create a plugin setting
    plugin_setting = PluginSetting(
        title="Plugin Name",
        description="Plugin Description",
        inputs=[
            SelectorInput(type="selector", title="title", description="description", options=["op1", "op2", "op3"]),
            TextInput(type="text", title="title"),
            ShortTextInput(type="shortText", title="title"),
            CheckboxInput(type="checkbox", kind=["multiple", "single", "toggle"], title="title", options=["op1", "op2", "op3"]),
            ComposedTextInput(type="composedText", title="title", name="name", description="description")
        ]
    )
    await create_plugin_setting(plugin_setting)
    # Then, delete the plugin setting by title
    deleted_plugin_setting = await delete_plugin_setting_by_title("Plugin Name")
    assert deleted_plugin_setting.title == "Plugin Name", f"Expected title 'Plugin Name', got {deleted_plugin_setting.title}"
    print("test_delete_plugin_setting: Passed")

async def main():
    await setup()
    try:
        await test_create_plugin_setting()
        await test_get_plugin_setting_by_title()
        await test_delete_plugin_setting()
    finally:
        await teardown()

if __name__ == "__main__":
    asyncio.run(main())