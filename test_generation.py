import json
import datetime
import os

from agents import simple_tester_agent
from prompt_crafting import create_prompt_new, create_prompt_rewrite
from file_utilities import save_ai_response

def replace_target_file(response, filepath):
    
    # replacing tests in develpment folder
    test_file = filepath.replace('.ts', '.spec.ts')
    backup_file = test_file+".back"
    if(not os.path.exists(backup_file) and os.path.exists(test_file)):
        os.rename(test_file, backup_file)
    
    with open(test_file, 'w') as f:
        f.write(response)


def generate_test(filepath, custom_prompt):

    code = None
    with open(filepath, "r") as f:
        code = f.read()
    filename = os.path.basename(filepath)
    print('Generating test for {}'.format(filename))
    
    html_code = None
    htmlpath = filepath.replace('.ts', '.html')
    with open(htmlpath, "r") as f:
        html_code = f.read()

    user_prompt_str = create_prompt_new(filename, code, html_code, custom_prompt)

    # sending api request to GPT4mini
    simple_tester_agent.add_message(user_prompt_str)
    response = simple_tester_agent.run_agent()

    save_ai_response(response, filename, 'ai_test')
    
    replace_target_file(response, filepath)


def regenerate_test(filepath, testpath, error_obj, custom_prompt, test_i, err_i):
    code = None
    with open(filepath, "r") as f:
        code = f.read()
    
    test_code = None
    with open(testpath, "r") as f:
        test_code = f.read()

    html_code = None
    htmlpath = filepath.replace('.ts', '.html')
    with open(htmlpath, "r") as f:
        html_code = f.read()

    error_log = error_obj['text']

    filename = os.path.basename(filepath)
    print('Regenerating test for {}'.format(filename))

    user_prompt_str = create_prompt_rewrite(filepath, code, test_code, html_code, error_log, custom_prompt)

    # sending api request to GPT4mini
    simple_tester_agent.add_message(user_prompt_str)
    response = simple_tester_agent.run_agent()

    save_ai_response(response, filename, 'ai_retest_{}_{}'.format(test_i, err_i))
    
    replace_target_file(response, filepath)



