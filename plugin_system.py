# plugin_system.py
import importlib
import os
from logger import logger

class PluginSystem:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        plugin_dir = "plugins"
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"plugins.{module_name}")
                    if hasattr(module, "register_plugin"):
                        plugin_info = module.register_plugin()
                        self.plugins[module_name] = plugin_info
                        logger.logger.info(f"Loaded plugin: {module_name}")
                except Exception as e:
                    logger.error(f"Error loading plugin {module_name}: {str(e)}")

    def get_plugin(self, name):
        return self.plugins.get(name)

    def execute_plugin(self, name, *args, **kwargs):
        plugin = self.get_plugin(name)
        if plugin and "execute" in plugin:
            return plugin["execute"](*args, **kwargs)
        else:
            logger.error(f"Plugin {name} not found or does not have an execute function")
            return None

plugin_system = PluginSystem()