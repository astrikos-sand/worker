import tarfile
from flask import Flask, request
from dotenv import load_dotenv
from config.const import DOCKER_SOCKET_PATH

load_dotenv()

import config.const as const
import logging
from datetime import datetime
import docker
import json
import requests
import os

app = Flask(__name__)

def setup_logging():
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"execution_{current_time}.log"
    
    logger = logging.getLogger(f"execution_{current_time}")
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return log_file, logger

def send_logs_to_django(log_file):
    try:
        with open(log_file, 'rb') as f:
            files = {'file': f}
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            data = {'filename': f'Execution_Logs_{current_time}'}
            response = requests.post(f"{const.BACKEND_URL}/archives/", files=files, data=data)
            response.raise_for_status()
        logging.info(f"Logs sent to Django backend successfully.")
        
        os.remove(log_file)
        logging.info(f"Log file {log_file} deleted successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send logs to Django backend: {str(e)}")
    except OSError as e:
        logging.error(f"Failed to delete log file {log_file}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in send_logs_to_django: {str(e)}")

@app.route("/", methods=["POST"])
def handle_task():
    log_file, logger = setup_logging()
    try:
        data = request.json
        logger.info(f"Received task data: {data}")

        env_id = data.get("data", {}).get("env_id")

        if env_id is not None:
            try:
                client = docker.from_env()
                logger.info(f"Docker client initialized successfully")
            except Exception as docker_error:
                logger.error(f"Failed to initialize Docker client: {str(docker_error)}")
                raise
            serialized_data = json.dumps(data)
            command = ["python", "task_handler.py", serialized_data]

            logger.info(f"Running container for environment {env_id}")
            container = client.containers.run(
                image=f"astrikos-environment-{env_id}",
                command=command,
                detach=True,
            )

            container.wait()
            logs = container.logs().decode("utf-8")
            logger.info(f"Container logs: {logs}")
            container.remove()
        else:
            from task_handler import task_handler
            logger.info("Running task_handler directly")
            task_handler(data)

        logger.info("Task completed successfully")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error in handle_task: {str(e)}")
        return {"error": str(e), "success": False}, 500
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        send_logs_to_django(log_file)

@app.route("/env/", methods=["POST"])
def create_environment():
    data = request.json
    requirements = data.get("requirements")
    id = data.get("id")

    import docker
    from string import Template
    from io import BytesIO
    import json
    import os

    if const.DEBUG:
        media_part = requirements.split("/media/")[1]
        download_url = f"{const.BACKEND_URL}/media/{media_part}"

    template_file_path = f"{const.BASE_DIR}/environment/Dockerfile"
    script_path = f"{const.BASE_DIR}/environment/download_script.py"

    with open(script_path, "r") as file:
        script_content = file.read()

    with open(template_file_path, "r") as file:
        template = Template(file.read())
        dockerfile_content = template.substitute(
            download_url=download_url, download_script=json.dumps(script_content)
        )

    client = docker.DockerClient(base_url=DOCKER_SOCKET_PATH)
    image_tag = f"astrikos-environment-{id}"

    dockerfile_bytes = dockerfile_content.encode("utf-8")
    dockerfile_obj = BytesIO(dockerfile_bytes)

    # TODO: add tar in volume for enhancement

    project_dir = const.BASE_DIR
    tar_stream = BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        tarinfo = tarfile.TarInfo("Dockerfile")
        tarinfo.size = len(dockerfile_bytes)
        tar.addfile(tarinfo, dockerfile_obj)

        file_paths = ["requirements.txt", "tasks.py", ".env", "task_handler.py"]

        for _file_path in file_paths:
            file_path = os.path.join(project_dir, _file_path)
            tar.add(file_path, arcname=_file_path)

        directories = ["executors", "utils", "config"]
        for directory in directories:
            app_dir = os.path.join(project_dir, directory)
            for root, dirs, files in os.walk(app_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    tar.add(
                        file_path, arcname=f"{os.path.relpath(file_path, project_dir)}"
                    )

    tar_stream.seek(0)

    client.images.build(
        fileobj=tar_stream,
        tag=image_tag,
        rm=True,
        pull=True,
        custom_context=True,
    )

    return {"success": True, "image_tag": image_tag}


if __name__ == "__main__":
    app.config["DEBUG"] = 1
    app.run(debug=1, host=const.HOST, port=const.PORT)
