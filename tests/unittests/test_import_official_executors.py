import importlib
import os
import re
from pathlib import Path

from faraday_agent_dispatcher.cli.utils.model_load import executor_folder, executor_metadata, full_check_metadata


def test_imports():
    folder = executor_folder()
    modules = [
        f"{Path(module).stem}"
        for module in os.listdir(folder)
        if re.match(r".*\.py", module) is not None]
    error_message = ""
    for module in modules:
        try:
            importlib.import_module(f"faraday_agent_dispatcher.static.executors.official.{module}")
        except ImportError as e:
            error_message = f"{error_message}Can't import {module}\n"

    assert len(error_message) == 0, error_message


def test_no_path_varenv_in_manifests():
    folder = executor_folder()
    modules = [
        f"{Path(module).stem}"
        for module in os.listdir(folder)
        if re.match(r".*\.py", module) is not None]

    error_message = ""
    for module in modules:
        try:
            metadata = executor_metadata(module)
            if not full_check_metadata(metadata):
                error_message = f"{error_message}Not all manifest keys in manifest for {module}\n"
            if "environment_variables" in metadata:
                if "PATH" in metadata["environment_variables"]:
                    error_message = f"{error_message}Overriding PATH environment variable in {module}\n"

        except FileNotFoundError as e:
            error_message = f"{error_message}Can't found manifest file for {module}\n"

    assert len(error_message) == 0, error_message
