import os
import json


class LocalConfig:
    def __init__(self):
        self.project_path = None
        self.package_json_path = None
        self.config_path = None
        self.config_descriptions = {
            "max_retry": "Maximum number of retries",
            "single_test": "Command to run single file test"
        }
        self.config = {
            "max_retry": 3,
            "single_test": "ng test --watch=false --browsers ChromeHeadless --include={filename}"
        }
    

    def specify_project_path(self):
        print('Please, provide path to project folder(package.json inside): ')
        project_path = input('User: ')
        package_json_path = os.path.join(project_path, 'package.json')
        while(not os.path.exists(package_json_path)):
            print('Selected project is not Node.js project. Try again.')
            project_path = input('User: ')
            package_json_path = os.path.join(project_path, 'package.json')
        
        self.project_path =  project_path
        self.package_json_path = os.path.join(project_path, 'package.json')
        self.config_path = os.path.join(project_path, 'ai_config.json')


    def specify_config_values(self):
        for field, param in self.config.items():

            print('Select new value for parameter "{}" or leave empty to use current: '.format(self.config_descriptions[field]))
            print('Current value is: {}'.format(self.config[field]))
            answer = input('User: ')
            if(len(answer) > 0):
                print('Saving new value')
                self.config[field] = answer
            else:
                print('Using previous value')

    def read_config_file(self):
        if(os.path.exists(self.config_path)):
            with open(self.config_path, 'r') as f:
                content = f.read()
                print(self.config_path)
                print(content)
                self.config = json.loads(content)            
        else:
            with open(self.config_path, 'w') as f:
                f.write(json.dumps(self.config))

    def update_config_file(self):
        if(os.path.exists(self.config_path)):
            with open(self.config_path, 'w') as f:
                f.write(json.dumps(self.config))

    def set_key(self, key, value):
        self.config[key] = value

    def get_key(self, key):
        return self.config[key]

def get_testable_path(is_folder):
    ftype = 'File'
    path = None
    if is_folder:
        ftype = 'Directory'
    print('Path to testing {}: '.format(ftype.lower()))
    path = input('User: ').strip()
    full_path = os.path.join(localConfig.project_path, path)
    while(
        not os.path.exists(full_path) 
        or (is_folder and not os.path.isdir(full_path)) 
        or (not is_folder and not os.path.isfile(full_path))):
        print('{} with name {} doesnt exist. Try again'.format(ftype, full_path))
        path = input('User: ')
        full_path = os.path.join(localConfig.project_path, path)

    return path

localConfig = LocalConfig()

