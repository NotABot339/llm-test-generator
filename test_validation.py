import os
import subprocess
import json

from file_utilities import save_ai_response
from agents import simple_tester_agent
from prompt_crafting import create_prompt_error

from config import localConfig


def run_test(filepath, test_i, err_i):

    filename = os.path.basename(filepath)
    root_filepath = filepath[len(localConfig.project_path)+1:]
    print('Running test {}. Iter:{}. Err:{}'.format(filename, test_i, err_i))
    result = subprocess.run(
        localConfig.get_key('single_test').format(filename = root_filepath), 
        shell=True, 
        capture_output=True, 
        text=True,
        cwd=localConfig.project_path)
    stdout = result.stdout
    stderr = result.stderr

    save_ai_response(stdout, filename, 'stdout_{}_{}'.format(test_i, err_i))
    save_ai_response(stderr, filename, 'stderr_{}_{}'.format(test_i, err_i))

    return [stdout, stderr]


def validate_test(filepath, stdout, stderr, test_i, err_i):
    filename = os.path.basename(filepath)

    errors = []

    if (len(stdout) > 0):

        check_error_prompt_str = create_prompt_error(filename, stdout)

        simple_tester_agent.add_message(check_error_prompt_str)
        answer = simple_tester_agent.run_agent()

        save_ai_response(answer, filename, 'ai_error_{}_{}'.format(test_i*2-1, err_i))

        answer_str = json.loads(answer)
        if(len(answer_str) > 0):
            errors = errors + answer_str

    if (len(stderr) > 0):

        check_error_prompt_str = create_prompt_error(filename, stderr)

        simple_tester_agent.add_message(check_error_prompt_str)
        answer = simple_tester_agent.run_agent()

        save_ai_response(answer, filename, 'ai_error_{}_{}'.format(test_i*2, err_i))

        answer_str = json.loads(answer)
        if(len(answer_str) > 0):
            errors = errors + answer_str

    return errors
