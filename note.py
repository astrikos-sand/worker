import time
import os
from threading import Thread

from jupyter_server.serverapp import ServerApp
from jupyter_server._tz import utcnow

import config.const as const


def insert_code_cell(notebook_path, new_code: str):
    import json

    with open(notebook_path, 'r', encoding='utf-8') as file:
        notebook: dict = json.load(file)

    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": new_code.splitlines(True)
    }

    notebook['cells'].append(new_cell)

    with open(notebook_path, 'w', encoding='utf-8') as file:
        json.dump(notebook, file, indent=1)


def copy_startup_file(flow_dir: str):
    import shutil

    ipython_startup_dir = "/root/.ipython/profile_default/startup"
    os.makedirs(ipython_startup_dir, exist_ok=True)
    destination_path = os.path.join(ipython_startup_dir, "task.py")

    custom_startup_script = (const.BASE_DIR / "v2/notebook/startup.py").as_posix()

    shutil.copyfile(custom_startup_script, destination_path)

    template_notebook = (const.BASE_DIR / "v2/notebook/template.ipynb").as_posix()
    notebook_path = os.path.join(const.BASE_DIR, f"media/notebooks/{flow_dir.split('-')[0]}/template.ipynb")

    default_code = f"# Flow: {flow_dir}\n"
    default_code += f"_flow_item, _flow_logs = run_task()"
    insert_code_cell(template_notebook, default_code)

    if not os.path.exists(notebook_path):
        shutil.copyfile(template_notebook, notebook_path)


class CustomServerApp(ServerApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inactivity_limit = 600
        self.inactivity_check_interval = 60

    def start_inactivity_timer(self):
        while True:
            time.sleep(self.inactivity_check_interval)
            seconds_since_active = (
                utcnow() - self.web_app.last_activity()
            ).total_seconds()
            print(f"Seconds since last activity: {seconds_since_active}")

            if seconds_since_active >= self.inactivity_limit:
                print(
                    f"No requests received for {seconds_since_active} seconds. Stopping the server."
                )
                self.stop()
                break


if __name__ == "__main__":
    import sys
    flow_dir = sys.argv[1]

    server = CustomServerApp()
    server.config_file = (const.BASE_DIR / "v2/notebook/config.py").as_posix()

    root_notebook_dir = (const.BASE_DIR / f"media/notebooks/{flow_dir.split('-')[0]}").as_posix()
    os.makedirs(root_notebook_dir, exist_ok=True)
    server.root_dir = root_notebook_dir

    server.initialize([])

    inactivity_thread = Thread(target=server.start_inactivity_timer)
    inactivity_thread.daemon = True
    inactivity_thread.start()

    copy_startup_file(flow_dir)

    server.start()
