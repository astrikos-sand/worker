import os
from contextlib import contextmanager

@contextmanager
def change_directory(target_directory):
    original_directory = os.getcwd()
    os.chdir(target_directory)
    try:
        yield
    finally:
        os.chdir(original_directory)

def run_task():
    with change_directory('/app'):
        from dotenv import load_dotenv

        from v2_task import task_handler

        load_dotenv()
        import json

        with open("data.json") as f:
            data = json.load(f)

        flow_manager = task_handler(data)
        _flow_item = flow_manager.global_dict["globals"]
        _flow_logs = flow_manager.logs

    return _flow_item, _flow_logs
