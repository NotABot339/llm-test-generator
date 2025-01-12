import json

def create_prompt_error(filename, log):

    prompt = {
        "mode": "error",
        "filename": filename,
        "log": log
    }

    prompt_str = json.dumps(prompt)
    return prompt_str

def create_prompt_rewrite(filepath, code, test_code, html_code, error_log, custom_prompt):
    prompt = {
        "mode": "rewrite",
        "filename": filepath,
        "code": code,
        "html": html_code,
        "test": test_code,
        "error": error_log,
        "prompt": custom_prompt
    }

    prompt_str = json.dumps(prompt)
    return prompt_str


def create_prompt_new(filename, code, html_code, custom_prompt):
    
    prompt = {
        "mode": "new",
        "filename": filename,
        "code": code,
        "html": html_code,
        "prompt": custom_prompt
    }

    prompt_str = json.dumps(prompt)
    return prompt_str