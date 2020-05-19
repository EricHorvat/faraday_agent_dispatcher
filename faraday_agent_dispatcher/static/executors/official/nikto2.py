#!/usr/bin/env python
import os
import sys
import subprocess
import tempfile
from faraday_plugins.plugins.repo.nikto.plugin import NiktoPlugin


def main():
    # If the script is run outside the dispatcher the environment variables are checked.
    # ['EXECUTOR_CONFIG_TARGET_URL', 'EXECUTOR_CONFIG_TARGET_PORT']
    url_target = os.environ.get('EXECUTOR_CONFIG_TARGET_URL')
    url_port = os.environ.get('EXECUTOR_CONFIG_TARGET_PORT')
    url_target = 'localhost'
    url_port = 8080
    if not url_target:
        print("URL not provided", file=sys.stderr)
        sys.exit()

    with tempfile.TemporaryDirectory() as tempdirname:
        name_result = f'{tempdirname}/output.xml'
        if not url_port:
            command = f'nikto -h {url_target} -o {name_result}'
        else:
            command = f'nikto -h {url_target} -p {url_port} -o {name_result}'

        nikto_process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if len(nikto_process.stdout) > 0:
            print(f"Nikto stdout: {nikto_process.stdout.decode('utf-8')}", file=sys.stderr)
        if len(nikto_process.stderr) > 0:
            print(f"Nikto stderr: {nikto_process.stderr.decode('utf-8')}", file=sys.stderr)
        plugin = NiktoPlugin()
        with open(name_result, 'r') as f:
            plugin.parseOutputString(f.read())
            print(plugin.get_json())


if __name__ == '__main__':
    main()
