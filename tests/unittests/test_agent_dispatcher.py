#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  Infobyte LLC (http://www.infobytesec.com/)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Tests for `faraday_agent_dispatcher` package."""

import json
import os
from pathlib import Path

import pytest
import sys

from itsdangerous import TimestampSigner

from faraday_agent_dispatcher.dispatcher import Dispatcher
from faraday_agent_dispatcher.config import (
    instance as configuration,
    Sections,
)
from tests.unittests.config.agent_dispatcher import (
    generate_basic_built_config,
    generate_executor_options,
    generate_register_options,
    connect_ws_responses,
)
from tests.utils.testing_faraday_server import (  # noqa: F401
    FaradayTestConfig,
    test_config,
    tmp_custom_config,
    tmp_default_config,
    test_logger_handler,
    test_logger_folder,
)


@pytest.mark.parametrize('config_changes_dict',
                         generate_basic_built_config())
def test_basic_built(tmp_custom_config, config_changes_dict):  # noqa F811
    for section in config_changes_dict["replace"]:
        for option in config_changes_dict["replace"][section]:
            if section not in configuration:
                configuration.add_section(section)
            configuration.set(
                section,
                option,
                config_changes_dict["replace"][section][option]
            )
    for section in config_changes_dict["remove"]:
        if "section" in config_changes_dict["remove"][section]:
            configuration.remove_section(section)
        else:
            for option in config_changes_dict["remove"][section]:
                configuration.remove_option(section, option)
    tmp_custom_config.save()
    if "expected_exception" in config_changes_dict:
        if "duplicate_exception" in config_changes_dict \
                and config_changes_dict["duplicate_exception"]:
            with open(tmp_custom_config.config_file_path, "r") as file:
                content = file.read()
            with open(tmp_custom_config.config_file_path, "w") as file:
                file.write(content)
                file.write(content)
        with pytest.raises(config_changes_dict["expected_exception"]):
            Dispatcher(None, tmp_custom_config.config_file_path)
    else:
        Dispatcher(None, tmp_custom_config.config_file_path)


@pytest.mark.parametrize('register_options',
                         generate_register_options())
@pytest.mark.asyncio
async def test_start_and_register(register_options,
                                  test_config: FaradayTestConfig,  # noqa F811
                                  tmp_default_config,  # noqa F811
                                  test_logger_handler):  # noqa F811
    os.environ['DISPATCHER_TEST'] = "True"

    client = test_config.ssl_client \
        if register_options["use_ssl_server"] \
        else test_config.client

    # Config
    configuration.set(Sections.SERVER, "api_port", str(client.port))
    configuration.set(Sections.SERVER, "host", client.host)
    configuration.set(Sections.SERVER, "workspace", test_config.workspace)
    configuration.set(
        Sections.TOKENS,
        "registration",
        test_config.registration_token
    )
    configuration.set(Sections.EXECUTOR_DATA.format("ex1"), "cmd", 'exit 1')

    for section in register_options["replace_data"]:
        for option in register_options["replace_data"][section]:
            if section not in configuration:
                configuration.add_section(section)
            configuration.set(
                section,
                option,
                register_options["replace_data"][section][option]
            )

    tmp_default_config.save()

    # Init and register it
    dispatcher = Dispatcher(
        client.session,
        tmp_default_config.config_file_path
    )

    if "expected_exception" not in register_options:
        await dispatcher.register()
        # Control tokens
        assert dispatcher.agent_token == test_config.agent_token

        signer = TimestampSigner(
            test_config.app_config['SECRET_KEY'],
            salt="websocket_agent"
        )
        agent_id = int(
            signer.unsign(dispatcher.websocket_token).decode('utf-8')
        )
        assert test_config.agent_id == agent_id
    else:
        with pytest.raises(register_options["expected_exception"]):
            await dispatcher.register()

    history = test_logger_handler.history

    logs_ok, failed_logs = await check_logs(history, register_options["logs"])

    if "optional_logs" in register_options and not logs_ok:
        logs_ok, new_failed_logs = await check_logs(
            history,
            register_options["optional_logs"]
        )
        failed_logs = {"logs": failed_logs, "optional_logs": new_failed_logs}

    assert logs_ok, failed_logs


async def check_logs(history, logs):
    logs_ok = True
    failed_logs = []
    for log in logs:
        min_count = 1 if "min_count" not in log else log["min_count"]
        max_count = sys.maxsize if "max_count" not in log else log["max_count"]
        log_ok = \
            max_count >= \
            len(
                list(
                    filter(
                        lambda x: (log["msg"] in x.message) and
                                  (x.levelname == log["levelname"]),
                        history
                    )
                )
            ) >= min_count

        if not log_ok:
            failed_logs.append(log)

        logs_ok &= log_ok
    return logs_ok, failed_logs


@pytest.mark.parametrize('executor_options',
                         generate_executor_options())
@pytest.mark.asyncio
async def test_run_once(test_config: FaradayTestConfig, # noqa F811
                        tmp_default_config, # noqa F811
                        test_logger_handler, # noqa F811
                        test_logger_folder, # noqa F811
                        executor_options):
    # Config
    workspace = test_config.workspace \
        if "workspace" not in executor_options \
        else executor_options["workspace"]
    configuration.set(Sections.SERVER, "api_port",
                      str(test_config.client.port))
    configuration.set(Sections.SERVER, "host", test_config.client.host)
    configuration.set(Sections.SERVER, "workspace", workspace)
    configuration.set(Sections.TOKENS, "registration",
                      test_config.registration_token)
    configuration.set(Sections.TOKENS, "agent", test_config.agent_token)
    path_to_basic_executor = (
            Path(__file__).parent.parent /
            'data' / 'basic_executor.py'
    )
    executor_names = ["ex1"] + (
        [] if "extra" not in executor_options else executor_options["extra"])
    configuration.set(Sections.AGENT, "executors", ",".join(executor_names))
    for executor_name in executor_names:
        executor_section = Sections.EXECUTOR_DATA.format(executor_name)
        params_section = Sections.EXECUTOR_PARAMS.format(executor_name)
        varenvs_section = Sections.EXECUTOR_VARENVS.format(executor_name)
        for section in [executor_section, params_section, varenvs_section]:
            if section not in configuration:
                configuration.add_section(section)

        configuration.set(executor_section, "cmd",
                          "python {}".format(path_to_basic_executor))
        configuration.set(params_section, "out", "True")
        [configuration.set(params_section, param, "False") for param in [
            "count", "spare", "spaced_before", "spaced_middle", "err",
            "fails"]]
        if "varenvs" in executor_options:
            for varenv in executor_options["varenvs"]:
                configuration.set(varenvs_section, varenv,
                                  executor_options["varenvs"][varenv])

        max_size = str(64 * 1024) if "max_size" not in executor_options else \
            executor_options["max_size"]
        configuration.set(executor_section, "max_size", max_size)

    tmp_default_config.save()

    async def ws_messages_checker(msg):
        msg_ = json.loads(msg)
        assert msg_ in executor_options["ws_responses"]
        executor_options["ws_responses"].remove(msg_)

    # Init and register it
    dispatcher = Dispatcher(test_config.client.session,
                            tmp_default_config.config_file_path)
    await dispatcher.run_once(json.dumps(executor_options["data"]),
                              ws_messages_checker)
    history = test_logger_handler.history
    assert len(executor_options["ws_responses"]) == 0
    for log in executor_options["logs"]:
        min_count = 1 if "min_count" not in log else log["min_count"]
        max_count = sys.maxsize if "max_count" not in log else log["max_count"]
        assert max_count >= \
               len(
                   list(
                       filter(
                           lambda x: x.levelname == log["levelname"] and log[
                               "msg"] in x.message, history))) >= \
               min_count, log["msg"]


@pytest.mark.asyncio
async def test_connect(test_config: FaradayTestConfig, # noqa F811
                       tmp_default_config, # noqa F811
                       test_logger_handler, # noqa F811
                       test_logger_folder): # noqa F811
    configuration.set(Sections.SERVER, "api_port",
                      str(test_config.client.port))
    configuration.set(Sections.SERVER, "host", test_config.client.host)
    configuration.set(Sections.SERVER, "workspace", test_config.workspace)
    configuration.set(Sections.TOKENS, "registration",
                      test_config.registration_token)
    configuration.set(Sections.TOKENS, "agent", test_config.agent_token)
    path_to_basic_executor = (
            Path(__file__).parent.parent /
            'data' / 'basic_executor.py'
    )
    configuration.set(Sections.AGENT, "executors", "ex1,ex2,ex3,ex4")

    for executor_name in ["ex1", "ex3", "ex4"]:
        executor_section = Sections.EXECUTOR_DATA.format(executor_name)
        params_section = Sections.EXECUTOR_PARAMS.format(executor_name)
        for section in [executor_section, params_section]:
            if section not in configuration:
                configuration.add_section(section)
        configuration.set(executor_section, "cmd",
                          "python {}".format(path_to_basic_executor))

    configuration.set(Sections.EXECUTOR_PARAMS.format("ex1"), "param1", "True")
    configuration.set(Sections.EXECUTOR_PARAMS.format("ex1"), "param2",
                      "False")
    configuration.set(Sections.EXECUTOR_PARAMS.format("ex3"), "param3",
                      "False")
    configuration.set(Sections.EXECUTOR_PARAMS.format("ex3"), "param4",
                      "False")
    tmp_default_config.save()
    dispatcher = Dispatcher(test_config.client.session,
                            tmp_default_config.config_file_path)

    ws_responses = connect_ws_responses(test_config.workspace)

    async def ws_messages_checker(msg):
        msg_ = json.loads(msg)
        assert msg_ in ws_responses
        ws_responses.remove(msg_)

    await dispatcher.connect(ws_messages_checker)

    assert len(ws_responses) == 0
