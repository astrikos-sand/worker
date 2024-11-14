import tarfile
from flask import Flask, request
from dotenv import load_dotenv
from config.const import DOCKER_SOCKET_PATH
from datetime import datetime
from utils.logger import logger
import threading

import docker
import json
from io import BytesIO
import os
import requests

load_dotenv()

import config.const as const

app = Flask(__name__)


@app.route("/notebook/start/", methods=["POST"])
def start_notebook():
    data = request.json
    lib = data.get("lib")

    if os.path.exists("/tmp/astrikos.txt"):
        with open("/tmp/astrikos.txt", "r") as file:
            container_id = file.read()

        print(f"Stopping container {container_id}", flush=True)

        client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCKET_PATH}")
        try:
            container = client.containers.get(container_id)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass

    if lib is not None:
        id = lib.get("id")[:8]
        name = lib.get("name")

        client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCKET_PATH}")
        serialized_data = json.dumps(data)
        command = [
            "sh",
            "-c",
            f"pip install jupyter-server && python v2_task.py && python note.py {data.get('flow').get('id')[:8]}-{data.get('flow').get('name')}",
        ]
        image = f"{name}-{id}"

        project_dir = const.BASE_DIR
        tarstream = BytesIO()

        with tarfile.open(fileobj=tarstream, mode="w") as tar:
            json_bytes = serialized_data.encode("utf-8")
            json_file = BytesIO(json_bytes)
            tarinfo = tarfile.TarInfo(name="data.json")
            tarinfo.size = len(json_bytes)
            tar.addfile(tarinfo, json_file)

            file_paths = [
                "tasks.py",
                ".env",
                "task_handler.py",
                "v2_task.py",
                "note.py",
            ]

            for _file_path in file_paths:
                file_path = os.path.join(project_dir, _file_path)
                tar.add(file_path, arcname=_file_path)

            directories = ["executors", "utils", "config", "wrappers", "v2"]
            for directory in directories:
                app_dir = os.path.join(project_dir, directory)
                for root, dirs, files in os.walk(app_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        tar.add(
                            file_path,
                            arcname=f"{os.path.relpath(file_path, project_dir)}",
                        )

        tarstream.seek(0)

        def run_container():
            container = client.containers.create(
                image=image,
                command=command,
                detach=True,
                extra_hosts={
                    "host.docker.internal": "host-gateway",
                },
                ports={
                    "8888/tcp": 9510,
                },
                mounts=[
                    {
                        "source": "astrikos_worker_executors",
                        "target": "/app/media",
                        "type": "volume",
                    }
                ],
            )

            client.api.put_archive(container.id, "/app/", tarstream)

            with open("/tmp/astrikos.txt", "w") as file:
                file.write(f"{container.id}")

            container.start()
            container.wait()

            logs = container.logs()
            logger.info(
                f"\n*****Container Logs*****\n{logs.decode('utf-8')}\n************************"
            )

            container.remove()

        thread = threading.Thread(target=run_container)
        thread.start()

    return {"success": True}


@app.route("/health/", methods=["GET"])
def health():
    return {"success": True}


@app.route("/v2/", methods=["POST"])
def handle_v2_task():
    data = request.json
    lib = data.get("lib")

    if lib is not None:
        id = lib.get("id")[:8]
        name = lib.get("name")

        res = requests.post(
            f"{const.BACKEND_URL}/v2/flows/{data.get('flow').get('id')}/executions/",
        )
        data["execution_id"] = res.json().get("id")

        crr_time = datetime.now()

        year = crr_time.year
        month = crr_time.month
        day = crr_time.day
        hour = crr_time.hour
        minute = crr_time.minute
        second = crr_time.second
        log_filename = f"{day}_{hour:02}:{minute:02}:{second:02}.txt"

        def handle_error(e):
            logger.error(f"{e}")

            logs = f"Error: {e}".encode("utf-8")
            res = requests.post(
                f"{const.BACKEND_URL}/v2/archives/logs/",
                data={
                    "flow": data.get("flow").get("id"),
                    "timestamp_prefix": f"txt/{year}/{month:02}",
                    "name": log_filename,
                },
                files={"file": (log_filename, BytesIO(logs))},
            )

            archive_id = res.json().get("id")

            requests.patch(
                f"{const.BACKEND_URL}/v2/flows/{data.get('flow').get('id')}/executions/",
                json={
                    "id": data.get("execution_id"),
                    "container_logs": archive_id,
                    "status": "ERROR",
                },
            )

        client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCKET_PATH}")
        serialized_data = json.dumps(data)
        command = ["python", "v2_task.py"]
        image = f"{name}-{id}"

        project_dir = const.BASE_DIR
        tarstream = BytesIO()

        with tarfile.open(fileobj=tarstream, mode="w") as tar:
            json_bytes = serialized_data.encode("utf-8")
            json_file = BytesIO(json_bytes)
            tarinfo = tarfile.TarInfo(name="data.json")
            tarinfo.size = len(json_bytes)
            tar.addfile(tarinfo, json_file)

            file_paths = ["tasks.py", ".env", "task_handler.py", "v2_task.py"]

            for _file_path in file_paths:
                file_path = os.path.join(project_dir, _file_path)
                tar.add(file_path, arcname=_file_path)

            directories = ["executors", "utils", "config", "wrappers", "v2"]
            for directory in directories:
                app_dir = os.path.join(project_dir, directory)
                for root, dirs, files in os.walk(app_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        tar.add(
                            file_path,
                            arcname=f"{os.path.relpath(file_path, project_dir)}",
                        )

        tarstream.seek(0)

        def run_container():
            try:
                container = client.containers.create(
                    image=image,
                    command=command,
                    detach=True,
                    extra_hosts={
                        "host.docker.internal": "host-gateway",
                    },
                )

                client.api.put_archive(container.id, "/app/", tarstream)

                container.start()
                container.wait()

                logs = container.logs()
                logger.info(
                    f"\n*****Container Logs*****\n{logs.decode('utf-8')}\n************************"
                )
                container.remove()

                archive_id = None

                if len(logs) > 0:
                    res = requests.post(
                        f"{const.BACKEND_URL}/v2/archives/logs/",
                        data={
                            "flow": data.get("flow").get("id"),
                            "timestamp_prefix": f"txt/{year}/{month:02}",
                            "name": log_filename,
                        },
                        files={"file": (log_filename, BytesIO(logs))},
                    )

                    archive_id = res.json().get("id")

                requests.patch(
                    f"{const.BACKEND_URL}/v2/flows/{data.get('flow').get('id')}/executions/",
                    json={
                        "id": data.get("execution_id"),
                        "container_logs": archive_id,
                        "status": "SUCCESS",
                    },
                )

                print(
                    f"Task for {data.get('flow', {}).get('name')} completed successfully",
                    flush=True,
                )

            except Exception as e:
                handle_error(e)

        thread = threading.Thread(target=run_container)
        thread.start()

    return {"success": True}


@app.route("/", methods=["POST"])
def handle_task():
    data = request.json

    meta_data = data.get("data", {})
    env_id = meta_data.get("env_id", None)
    flow_id = meta_data.get("flow_id", None)

    if env_id is not None:
        client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCKET_PATH}")
        serialized_data = json.dumps(data)
        command = ["python", "task_handler.py"]
        image = f"astrikos-environment-{env_id}"

        project_dir = const.BASE_DIR
        tarstream = BytesIO()

        with tarfile.open(fileobj=tarstream, mode="w") as tar:
            json_bytes = serialized_data.encode("utf-8")
            json_file = BytesIO(json_bytes)
            tarinfo = tarfile.TarInfo(name="data.json")
            tarinfo.size = len(json_bytes)
            tar.addfile(tarinfo, json_file)

            file_paths = ["tasks.py", ".env", "task_handler.py"]

            for _file_path in file_paths:
                file_path = os.path.join(project_dir, _file_path)
                tar.add(file_path, arcname=_file_path)

            directories = ["executors", "utils", "config", "wrappers"]
            for directory in directories:
                app_dir = os.path.join(project_dir, directory)
                for root, dirs, files in os.walk(app_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        tar.add(
                            file_path,
                            arcname=f"{os.path.relpath(file_path, project_dir)}",
                        )

        tarstream.seek(0)

        container = client.containers.create(
            image=image,
            command=command,
            detach=True,
            extra_hosts={
                "host.docker.internal": "host-gateway",
            },
        )

        client.api.put_archive(container.id, "/app/", tarstream)

        container.start()
        container.wait()

        logs = container.logs()
        logger.info(
            f"\n*****Container Logs*****\n{logs.decode('utf-8')}\n************************"
        )
        container.remove()

        crr_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{flow_id}_{crr_time}.log"

        requests.post(
            f"{const.BACKEND_URL}/archives/",
            data={"filename": log_filename},
            files={"file": (log_filename, BytesIO(logs))},
        )

    else:
        from task_handler import task_handler

        task_handler(data)

    return {"success": True}


@app.route("/env/", methods=["POST"])
def create_environment():
    data = request.json
    requirements = data.get("requirements")
    id = data.get("id")[:8]
    name = data.get("name")

    from string import Template

    if const.DEBUG:
        media_part = requirements.split("/media/")[1]
        download_url = f"{const.BACKEND_URL}/media/{media_part}"

    template_file_path = f"{const.BASE_DIR}/environment/template.txt"
    script_path = f"{const.BASE_DIR}/environment/download_script.py"

    with open(script_path, "r") as file:
        script_content = file.read()

    with open(template_file_path, "r") as file:
        template = Template(file.read())
        dockerfile_content = template.substitute(
            download_url=download_url,
            download_script=json.dumps(script_content),
            python_image="default-astrikos-env",
        )

    image_tag = f"{name}-{id}"

    dockerfile_bytes = dockerfile_content.encode("utf-8")
    dockerfile_obj = BytesIO(dockerfile_bytes)

    project_dir = const.BASE_DIR
    tar_stream = BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        tarinfo = tarfile.TarInfo("Dockerfile")
        tarinfo.size = len(dockerfile_bytes)
        tar.addfile(tarinfo, dockerfile_obj)

        file_paths = ["requirements.txt"]

        for _file_path in file_paths:
            file_path = os.path.join(project_dir, _file_path)
            tar.add(file_path, arcname=_file_path)

    tar_stream.seek(0)

    def build_image():
        logs = ""

        crr_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{id}_{crr_time}.txt"

        try:
            client = docker.DockerClient(base_url=f"unix://{DOCKER_SOCKET_PATH}")
            _, response = client.images.build(
                fileobj=tar_stream,
                tag=image_tag,
                rm=True,
                custom_context=True,
                extra_hosts={
                    "host.docker.internal": "host-gateway",
                },
            )

            for line in response:
                if "stream" in line:
                    logs += line["stream"]

            logs += f"Image {image_tag} built successfully"
        except Exception as e:
            logs += f"Error building image: {e}"

        logs = logs.encode("utf-8")
        requests.post(
            f"{const.BACKEND_URL}/v2/archives/env/",
            data={
                "env": data.get("id"),
                "name": log_filename,
            },
            files={"file": (log_filename, BytesIO(logs))},
        )

    thread = threading.Thread(target=build_image)
    thread.start()

    return {"success": True, "image_tag": image_tag}


if __name__ == "__main__":
    app.config["DEBUG"] = 1

    from v2.subscribe import register_executors

    register_executors()

    app.run(debug=1, host=const.HOST, port=const.PORT)
