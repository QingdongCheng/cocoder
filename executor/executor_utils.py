import docker
import os
import uuid
import shutil

from docker.errors import *

IMAGE_NAME = "adongcheng/qboj_executor"
CURRENT_DIR = os.path.dirname(os.path.relpath(__file__))
TEMP_BUILD_DIR = "%s/tmp/" % CURRENT_DIR
CONTAINER_NAME = "%s:latest" % IMAGE_NAME

client = docker.from_env()

SOURCE_FILE_NAMES = {
    "java": "Example.java",
    "python": "example.py"
}
BINARY_NAMES = {
    "java": "Example",
    "python": "example.py"
}
BUILD_COMMANDS = {
    "java": "javac",
    "python": "python"
}
EXECUTE_COMMANDS = {
    "java": "java",
    "python": "python"
}


def load_image():
    try:
        client.images.get(IMAGE_NAME)
    except ImageNotFound:
        print ("Image not found locally. Loading from Dockerhub...")
        client.images.pull(IMAGE_NAME)
    except APIError:
        print ("Image not found locally. DockerHub is not accessible.")
        return
    print("Image:[%s] loaded" % IMAGE_NAME)

def build_and_run(code, lang):
    # docker operations
    result = {'build' : None, 'run': None, 'error' : None}
    source_file_parent_dir_name = uuid.uuid4()
    # '/tmp/uuid/Example.java'
    source_file_host_dir = "%s/%s" % (TEMP_BUILD_DIR, source_file_parent_dir_name)
    source_file_guest_dir = "/test/%s" % (source_file_parent_dir_name)
    make_dir(source_file_host_dir)
    # write code to a file
    with open("%s/%s" %(source_file_host_dir, SOURCE_FILE_NAMES[lang]), 'w') as source_file:
        source_file.write(code)

    # build and run
    try:
        client.containers.run(
            image=IMAGE_NAME,
            command="%s %s" % (BUILD_COMMANDS[lang], SOURCE_FILE_NAMES[lang]),
            volumes={source_file_host_dir: {'bind': source_file_guest_dir, 'mode': 'rw'}},
            working_dir=source_file_guest_dir
        )
        print('source built')
        result['build'] = 'OK'
    except ContainerError as e:
        result['build'] = e.stderr
        shutil.rmtree(source_file_host_dir)
        return result

    # run in the docker
    try:
        log = client.containers.run(
            image=IMAGE_NAME,
            command="%s %s" % (EXECUTE_COMMANDS[lang], BINARY_NAMES[lang]),
            volumes={source_file_host_dir: {'bind': source_file_guest_dir, 'mode': 'rw'}},
            working_dir=source_file_guest_dir
        )
        #log = str(log, 'utf-8')
        result['run'] = log
    except ContainerError as e:
        result['run'] = e.stderr
        shutil.rmtree(source_file_host_dir)
        return result
    shutil.rmtree(source_file_host_dir)
    return result

def make_dir(dir):
    try:
        os.mkdir(dir)
    except OSError:
        print('Error!!')
