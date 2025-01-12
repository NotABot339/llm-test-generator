from datetime import datetime
import os
from config import localConfig 
from test_generation import generate_test, regenerate_test
from file_utilities import prepare_file, prepare_files_from_folder
from test_validation import validate_test, run_test
from config import get_testable_path
from agents import simple_tester_agent
import globals


def test_files_in_folder():
    """
    Call this tool when user wants to test multiple files in folder. Dont ask for test parameters and just run a function ASAP.

    Args:

    Returns:

    """
    process_test(True)
    return "Test generation finished"


def test_single_file():

    """
    Call this tool when user wants to test single file. Dont ask for test parameters and just run a function ASAP.

    Args:

    Returns:

    """
    process_test(False)
    return "Test generation finished"


def process_test(is_folder):
    
    globals.current_timestamp = str(datetime.now().strftime('%Y%m%d-%H%M%S'))

    print("Creating/Updating config values.")
    global localConfig

    localConfig.specify_project_path()
    localConfig.read_config_file()
    localConfig.specify_config_values()
    localConfig.update_config_file()
    
    path = get_testable_path(is_folder)

    print("Preparing filelist")
    if(not is_folder):
        filelist = prepare_file(path)
    else:
        filelist = prepare_files_from_folder(path)

    print("Generating and running tests.")
    for file in filelist:
        simple_tester_agent.create_thread()

        print("Specify starting prompt or accept default. Default: 'Test if components are launched properly.'")
        custom_prompt = input('User: ')
        if(len(custom_prompt)==0):
            custom_prompt = 'Test if components are launched properly.'
        generate_test(file, custom_prompt)
        test_loop(file, custom_prompt)


def test_loop(filepath, custom_prompt):
    
    filename = os.path.basename(filepath)
    cur_iter = localConfig.get_key('max_retry')
    testpath = filepath.replace('.ts', '.spec.ts')
    test_success = False
    for test_i in range(1, cur_iter+1):
        if not test_success:
            stdout, stderr = run_test(filepath, test_i, 0)
            errors = validate_test(filepath, stdout, stderr, test_i, 0)
            if(len(errors)) == 0:
                test_success = True
                break
            else:
                print('Test {} completed with errors'.format(filename))
                for err_i in range(1, len(errors)+1):
                    error = errors[err_i-1]
                    regenerate_test(filepath, testpath, error, custom_prompt, test_i, err_i)
                    stdout, stderr = run_test(filepath, test_i, err_i)
                    new_errors = validate_test(filepath, stdout, stderr, test_i, err_i)
                    if(len(new_errors)) == 0:
                        test_success = True
                        break
        else: 
            break
    
    if (not test_success):
        print('Test failed after {} attempts. Try checking for project file compile errors or specify different prompt'.format(localConfig.get_key('max_retry')))






