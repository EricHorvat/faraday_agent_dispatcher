import pytest
from click.testing import CliRunner
from typing import Dict, List
import os
from pathlib import Path

from faraday_agent_dispatcher.cli.main import config_wizard
from faraday_agent_dispatcher import config as config_mod
from tests.unittests.wizard_input import ExecutorInput, DispatcherInput, ParamInput, VarEnvInput, ADMType


def generate_inputs():
    return [
        # 0 All default
        {
            "dispatcher_input": DispatcherInput(),
            "exit_code": 0,
            "after_executors": set()
        },
        # 1 Dispatcher input
        {
            "dispatcher_input": DispatcherInput(host="127.0.0.1", api_port="13123", ws_port="1234", workspace="aworkspace",
                                      agent_name="agent", registration_token="1234567890123456789012345"),
            "exit_code": 0,
            "after_executors": set()
        },
        # 2 Bad token input
        {
            "dispatcher_input": DispatcherInput(host="127.0.0.1", api_port="13123", ws_port="1234", workspace="aworkspace",
                                      agent_name="agent", registration_token=["12345678901234567890", ""]),
            "exit_code": 0,
            "expected_output": ["registration must be 25 character length"],
            "after_executors": set()
        },
        # 3 Basic Executors input
        {
            "dispatcher_input": DispatcherInput(),
            "executors_input": [
                    ExecutorInput(name="ex1",
                                  cmd="cmd 1",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex2",
                                  cmd="cmd 2",
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex3",
                                  cmd="cmd 3",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex2", "ex3"}
        },
        # 4 Basic Bad Executors input
        {
            "dispatcher_input": DispatcherInput(),
            "executors_input": [
                    ExecutorInput(name="ex1",
                                  cmd="cmd 1",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex2",
                                  cmd="cmd 2",
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex3",
                                  cmd="cmd 3",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ]
                                  , adm_type=ADMType.ADD),
                    ExecutorInput(error_name="ex1",
                                  cmd="cmd 4",
                                  name="ex4",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex2", "ex3", "ex4"}
        },
        # 5 Basic Mod Executors input
        {
            "dispatcher_input": DispatcherInput(),
            "executors_input": [
                    ExecutorInput(name="ex1",
                                  cmd="cmd 1",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex2",
                                  cmd="cmd 2",
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex3", cmd="cmd 3",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex1",
                                  error_name="QWE",
                                  cmd="exit 1",
                                  params=[
                                       ParamInput(name="mod_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param1", value=False, adm_type=ADMType.MODIFY)
                                   ],
                                  adm_type=ADMType.MODIFY),
                    ExecutorInput(name="ex2",
                                  cmd="",
                                  varenvs=[
                                       VarEnvInput(name="mod_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.MODIFY),
                    ExecutorInput(name="ex3",
                                  new_name="eX3",
                                  cmd="",
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.MODIFY)
                                   ],
                                  adm_type=ADMType.MODIFY),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex2", "eX3"}
        },
        # 6 Basic Del Executors input
        {
            "dispatcher_input": DispatcherInput(),
            "executors_input": [
                    ExecutorInput(name="ex1",
                                  cmd="cmd 1",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex2",
                                  cmd="cmd 2",
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex3", cmd="cmd 3",
                                  params=[
                                       ParamInput(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamInput(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                  adm_type=ADMType.ADD),
                    ExecutorInput(name="ex1",
                                  error_name="QWE",
                                  cmd="exit 1",
                                  params=[
                                       ParamInput(name="add_param1", value=False, adm_type=ADMType.DELETE)
                                   ],
                                  adm_type=ADMType.MODIFY),
                    ExecutorInput(name="ex2",
                                  cmd="",
                                  adm_type=ADMType.DELETE),
                    ExecutorInput(name="ex3",
                                  cmd="",
                                  varenvs=[
                                       VarEnvInput(name="add_varenv1", value="", adm_type=ADMType.DELETE)
                                   ],
                                  adm_type=ADMType.MODIFY),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex3"}
        },
    ]


def old_version_path():
    return Path(__file__).parent.parent / 'data' / 'old_version_inis'


inputs = generate_inputs()
ini_configs = \
    [
        {
            "dir": "",
            "old_executors": set()
        },
        {
            "dir": old_version_path() / '0.1.ini',
            "old_executors": {config_mod.DEFAULT_EXECUTOR_VERIFY_NAME}
        },
        {
            "dir": old_version_path() / '1.0.ini',
            "old_executors": {"test", "test2"}
        }
    ]
error_ini_configs = \
    [
        {
            "dir": old_version_path() / '1.0_error0.ini',
            "exception_message": "notAConfiguredExecutor section does not exists"
        },
        {
            "dir": old_version_path() / '1.0_error1.ini',
            "exception_message": "executors option not in agent section"
        }
    ]


def parse_inputs(testing_inputs: Dict):
    result_input = ""
    if "dispatcher_input" in testing_inputs:
        dispatcher_input: DispatcherInput = testing_inputs['dispatcher_input']
        result_input = f"A\n{dispatcher_input.input_str()}"
    if "executors_input" in testing_inputs:
        executors_input: List[ExecutorInput] = testing_inputs["executors_input"]
        result_input = f"{result_input}E\n"
        for executor_input in executors_input:
            result_input = f"{result_input}{executor_input.input_str()}"
        result_input = f"{result_input}Q\n"
    result_input = f"{result_input}Q\n"
    return result_input


@pytest.mark.parametrize(
    "testing_inputs",
    inputs
)
@pytest.mark.parametrize(
    "ini_config",
    ini_configs
)
def test_new_config(testing_inputs: Dict[(str, object)], ini_config):
    runner = CliRunner()

    content = None
    content_path = ini_config["dir"]

    if content_path != "":
        with open(content_path, 'r') as content_file:
            content = content_file.read()

    with runner.isolated_filesystem() as file_system:

        if content:
            path = Path(file_system) / "dispatcher.ini"
            with path.open(mode="w") as content_file:
                content_file.write(content)
        else:
            path = Path(file_system)
        ''' 
        The in_data variable will be consumed for the cli command, but in order to avoid unexpected inputs with no
        data (and a infinite wait), a \0\n block of input is added at the end of the input. Furthermore the \0 is added
        as a possible choice of the ones and should exit with error.
        '''
        in_data = parse_inputs(testing_inputs) + "\0\n" * 1000
        env = os.environ
        env["DEBUG_INPUT_MODE"] = "True"
        result = runner.invoke(config_wizard, args=["-c", path], input=in_data, env=env)
        assert result.exit_code == testing_inputs["exit_code"], result.exception
        if "exception" in testing_inputs:
            assert str(result.exception) == str(testing_inputs["exception"])
            assert result.exception.__class__ == testing_inputs["exception"].__class__
        else:
            assert '\0\n' not in result.output  # Control '\0' is not passed in the output, as the input is echoed
        if "expected_outputs" in testing_inputs:
            for expected_output in testing_inputs["expected_outputs"]:
                assert expected_output in result.output

        expected_executors_set = set.union(ini_config["old_executors"], testing_inputs["after_executors"])

        config_mod.reset_config(path)
        executor_config_set = set(config_mod.instance.get(config_mod.Sections.AGENT, "executors").split(","))
        if '' in executor_config_set:
            executor_config_set.remove('')
        assert executor_config_set == expected_executors_set


@pytest.mark.parametrize(
    "ini_config",
    error_ini_configs
)
def test_verify(ini_config):
    runner = CliRunner()

    content_path = ini_config["dir"]

    with open(content_path, 'r') as content_file:
        content = content_file.read()

    with runner.isolated_filesystem() as file_system:

        path = Path(file_system) / "dispatcher.ini"
        with path.open(mode="w") as content_file:
            content_file.write(content)
        env = os.environ
        env["DEBUG_INPUT_MODE"] = "True"
        result = runner.invoke(config_wizard, args=["-c", path], input="\0\n"*1000, env=env)
        assert result.exit_code == 1, result.exception
        assert str(result.exception) == ini_config["exception_message"]
        assert result.exception.__class__ == ValueError
