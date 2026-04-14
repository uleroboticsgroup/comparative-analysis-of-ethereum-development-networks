import argparse
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import time
import zipfile
import yaml
import docker

from datetime import datetime
from logging import handlers


LOGS_FILE_PATH = "./logs/"
LOG_FORMATTER = "%(asctime)s::%(name)s::%(levelname)s::%(message)s"

CONF_FILE = "networks.yaml"

ENCODING = "utf-8"
READ_MODE = "r"

TMP_FOLDER = "docker/accountability/files/tmp/"
ROSBAGS_FOLDERS = "docker/accountability/files/rosbags"

CONTAINER_ACCOUNTABILITY_NAME = 'accountability'
CONTAINER_ANVIL_NAME = 'anvil'
CONTAINER_GANACHE_NAME = 'ganache'
CONTAINER_HARDHAT_NAME = 'hardhat'

CONTAINER_NAMES = [
    CONTAINER_ACCOUNTABILITY_NAME,
    CONTAINER_ANVIL_NAME,
    CONTAINER_GANACHE_NAME,
    CONTAINER_HARDHAT_NAME
]


def __remove_rosbag_files():
    logging.info('Removing docker/accountability/files/rosbags folder files')

    [shutil.rmtree(folder.path)
     for folder in os.scandir(ROSBAGS_FOLDERS)]


def __unzip_file(zip_file: str, extract_folder: str):
    logging.info('Unzipping %s file', zip_file)

    with zipfile.ZipFile(zip_file, READ_MODE) as zip_ref:
        zip_ref.extractall(extract_folder)


def __remove_unneeded_files():
    logging.info('Removing unneeded files')

    [shutil.rmtree(f"{folder.path}/")
     for folder in os.scandir(ROSBAGS_FOLDERS) if folder.is_dir() and 'Test_base' in folder.path]

    for folder in os.scandir(ROSBAGS_FOLDERS):
        if folder.is_dir():
            for file in os.scandir(folder):
                if 'rosbag' in file.name:
                    os.rename(file.path, f"{ROSBAGS_FOLDERS}/{file.name}")
            shutil.rmtree(folder.path) 

    shutil.rmtree(TMP_FOLDER)


def __extract_rosbags(zip_file_arg: str):
    __remove_rosbag_files()

    __unzip_file(zip_file_arg, TMP_FOLDER)

    [__unzip_file(zip_file.path, ROSBAGS_FOLDERS)
     for zip_file in os.scandir(TMP_FOLDER) if zip_file.is_file()]

    __remove_unneeded_files()


def __read_networks_config_file():
    configuration = {}

    with open(CONF_FILE, READ_MODE, encoding=ENCODING) as file:
        try:
            config_dict = yaml.load(file, Loader=yaml.SafeLoader)
            for key in config_dict:
                configuration[key] = config_dict[key]

        except yaml.YAMLError as ex:
            logging.error("%s", ex)

    return configuration


def __stop_containers(docker_client):
    for container in docker_client.containers.list():
        if container.name in CONTAINER_NAMES:
            logging.info('Stopping container %s', container.name)
            container.stop()


def __run_containers(docker_client):
    try:
        conf = __read_networks_config_file()

        rosbags = [file.path for file in os.scandir(ROSBAGS_FOLDERS) if file.is_dir()]

        for network in conf:
            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

            logging.info('Starting network %s', network)
            logging.info('===================================================================================================')
            logging.info('Total rosbags: %d', len(rosbags))

            i = 1
            for rosbag in rosbags:
                logging.info('---------------------------------------------------------------------------------------------------')
                logging.info('Rosbag %d / %d', i, len(rosbags))

                path = pathlib.Path(rosbag)
                rosbag = str(pathlib.Path(*path.parts[4:]))

                var_env = f"NETWORK='{network}' CONF_FILE='{conf[network]['configuration']}' ROSBAG='{rosbag}'"
                docker_command = f"{var_env} docker compose -f docker/compose/compose.yaml --profile {network} up -d"
                logging.info(docker_command)
                subprocess.run([docker_command], shell=True, check=True)

                acolyte_container = docker_client.containers.get(CONTAINER_ACCOUNTABILITY_NAME)
                while acolyte_container in docker_client.containers.list():
                    time.sleep(10)

                logging.info('Container %s ended', acolyte_container.name)
                __stop_containers(docker_client)

                i += 1

            logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')
            
    except KeyboardInterrupt:
        __stop_containers(docker_client)
        logging.info('Stopping orchestrator\n')

        sys.exit()


def __configure_logging():
    log_name = "".join(
        [LOGS_FILE_PATH, datetime.today().strftime('%Y-%m-%d'), ".log"])

    log_formatter = logging.Formatter(LOG_FORMATTER)
    log_formatter.converter = time.gmtime  # UTC time

    log_file_handler = handlers.RotatingFileHandler(
        log_name, maxBytes=10240000, backupCount=10)
    log_file_handler.setFormatter(log_formatter)

    log_terminal_handler = logging.StreamHandler()
    log_terminal_handler.setLevel(logging.INFO)

    logging.basicConfig(level=logging.INFO,
                        handlers=[
                            log_file_handler,
                            log_terminal_handler])


def __parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)

    main_argument_group = parser.add_argument_group(
        "required named arguments")

    main_argument_group.add_argument(
        "-u",
        "--unzip",
        action="store_true",
        help="unzip the specified file (the rosbags folder files will be deleted)"
    )

    main_argument_group.add_argument(
        "-f",
        "--file_to_unzip",
        default='docker/accountability/files/19469198.zip',
        required='unzip' in sys.argv,
        help="path file to unzip"
    )

    return parser.parse_args()


def __validate_arguments(arguments):
    are_valid = True

    if arguments.unzip:
        if arguments.file_to_unzip is (None or '') or not os.path.exists(arguments.file_to_unzip):
            are_valid = False
            logging.error('The specified zip file is not valid. Please review it.')

    return are_valid


def main():
    """
    Main function.
    """

    __configure_logging()

    logging.info('Starting orchestrator...')

    arguments = __parse_arguments()
    arguments_are_valid = __validate_arguments(arguments)
    if not arguments_are_valid:
        logging.error('Arguments are not valid.')
        logging.info('Stopping orchestrator\n')

        sys.exit()

    if arguments.unzip:
        __extract_rosbags(arguments.file_to_unzip)

    docker_client = docker.from_env()
    __run_containers(docker_client)

    logging.info('Stopping orchestrator\n')


if __name__ == "__main__":
    main()
