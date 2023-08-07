"""Core functions to interact with settings yaml file.

These are necessary for persisting settings in a yaml file (reading/updating)
"""
import logging
import yaml
from typing import Any


def read_settings_from_yaml() -> dict[str, Any]:
    """Reads the settings the yaml config at app.yaml.
    """
    # Read YAML to initialize settings
    with open("app.yaml", "r", encoding="utf-8") as stream:
        try:
            settings = yaml.safe_load(stream)
            logging.info("loaded settings: %s", settings)
            return settings
        except yaml.YAMLError as exc:
            logging.error(exc)
            return {}


def write_settings_to_yaml(key: str, value: Any):
    """Write the settings to the yaml config at app.yaml
    """
    # Doing this through a single pass with "r+" permission does not work...
    # It'll end up appending the updated contents to the yaml instead of
    # overwriting.
    settings = read_settings_from_yaml()
    settings[key] = value
    with open("app.yaml", "w", encoding="utf-8") as stream:
        try:
            logging.info("wrote settings: %s", settings)
            yaml.safe_dump(settings, stream, sort_keys=False)
        except yaml.YAMLError as exc:
            logging.error(exc)


def label_to_yaml_property(name: str) -> str:
    return "_".join(name.lower().split(" "))

