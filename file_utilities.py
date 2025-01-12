import os
import fnmatch
import globals
from config import localConfig

def prepare_file(path):
    proj_filelist_name = "project_paths.txt"
    
    test_filelist = [os.path.join(localConfig.project_path, path)]

    test_folder_path = os.path.join(localConfig.project_path, path)

    # vector_store_tester_agent.clean_store_files()

    context_filelist = get_context_filelist(test_folder_path)

    filelist = list(set(test_filelist).union(set(context_filelist))) #remove dublicates

    filelist.append(os.path.join(localConfig.project_path, 'package.json'))
    filelist.append(os.path.join(localConfig.project_path, 'angular.json'))
    filelist.append(os.path.join(localConfig.project_path, 'package-lock.json'))

    filelist.append(proj_filelist_name)

    # vector_store_tester_agent.send_store_files(filelist)

    return test_filelist


def prepare_files_from_folder(path):
    proj_filelist_name = "project_paths.txt"
    
    test_folder_path = os.path.join(localConfig.project_path, path)

    # vector_store_tester_agent.clean_store_files()

    test_filelist = get_test_filelist(test_folder_path)

    context_filelist = get_context_filelist(test_folder_path)

    filelist = list(set(test_filelist).union(set(context_filelist))) #remove dublicates

    filelist.append(os.path.join(localConfig.project_path, 'package.json'))
    filelist.append(os.path.join(localConfig.project_path, 'angular.json'))
    filelist.append(os.path.join(localConfig.project_path, 'package-lock.json'))


    filelist.append(proj_filelist_name)

    # vector_store_tester_agent.send_store_files(filelist)

    return test_filelist


def get_test_filelist(path):
    files = []

    for file in list_files_by_wildcard(path, '*.component.ts'):
        files.append(file)

    for file in list_files_by_wildcard(path, '*.service.ts'):
        files.append(file)
    
    return files

def get_context_filelist(path):
    files = []

    for file in list_files_by_wildcard(path, '*[!spec].ts'):
        files.append(file)

    for file in list_files_by_wildcard(path, '*.js'):
        files.append(file)

    for file in list_files_by_wildcard(path, '*.html'):
        files.append(file)

    return files

def list_files_by_wildcard(directory, pattern):
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, pattern):
                matching_files.append(os.path.join(root, file))
    return matching_files

def save_ai_response(response, filename, prefix):

    # saving ai response
    filename_template = './api_answers/{str_time}_{filename}_{prefix}'
    
    save_filename = filename_template.format(prefix=prefix, str_time=globals.current_timestamp, filename=filename)

    with open(save_filename, 'w') as outFile:
        outFile.write(response)