import tarfile
from flask import Flask, request
from dotenv import load_dotenv
from config.const import DOCKER_SOCKET_PATH

import docker
import json
from io import BytesIO
import os

load_dotenv()

import config.const as const

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_task():
    data = request.json

    env_id = data.get("data", {}).get("env_id")

    if env_id is not None:
        client = docker.DockerClient(base_url=DOCKER_SOCKET_PATH)
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

            directories = ["executors", "utils", "config"]
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
                "astrikos-dev.com": const.LOCAL_IP,
            },
        )

        client.api.put_archive(container.id, "/app/", tarstream)

        container.start()
        container.wait()
        print(container.logs().decode("utf-8"), flush=True)
        container.remove()
    else:
        from task_handler import task_handler

        task_handler(data)

    return {"success": True}


@app.route("/env/", methods=["POST"])
def create_environment():
    data = request.json
    requirements = data.get("requirements")
    id = data.get("id")

    from string import Template

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

    client.images.build(
        fileobj=tar_stream,
        tag=image_tag,
        rm=True,
        pull=True,
        custom_context=True,
        extra_hosts={
            "astrikos-dev.com": const.LOCAL_IP,
        },
    )

    return {"success": True, "image_tag": image_tag}


if __name__ == "__main__":
    app.config["DEBUG"] = 1
    app.run(debug=1, host=const.HOST, port=const.PORT)
