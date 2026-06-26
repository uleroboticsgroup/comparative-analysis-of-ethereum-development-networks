import argparse
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import time
import zipfile

from datetime import datetime
from logging import handlers
from prettytable import PrettyTable

import yaml
import pandas
import docker


LOGS_FILE_PATH = "./logs/"
LOG_FORMATTER = "%(asctime)s::%(name)s::%(levelname)s::%(message)s"

CONF_FILE = "networks.yaml"

ENCODING = "utf-8"
READ_MODE = "r"

TMP_FOLDER = "docker/accountability/files/tmp/"
ROSBAGS_FOLDER = "docker/accountability/files/rosbags"
CSV_FOLDER = "docker/accountability/files/csv"

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

METRICS_FOLDER="docker/compose/data/metrics"
METRICS = [
    'timestamp',
    'cpu_pct', 
    'mem_rss_bytes', 
    'mem_pct', 
    'disk_read_bytes', 
    'disk_write_bytes'
]
ROUND_DIGITS = 3


def _get_directories_from_folder(path: str):
    return [file.path for file in os.scandir(path) if file.is_dir()]


def _remove_csv_files():
    logging.info('Removing docker/accountability/files/csv folder files')

    [os.remove(file) for file in os.scandir(CSV_FOLDER) if file.is_file() and '.csv' in file.path]


def _split_csv(csv_file_arg: str):
    _remove_csv_files()

    SELECTED_VEHICLES = ['car1', 'car11'] # TODO: Configure the vehicles by arguments

    data_frame = pandas.read_csv(csv_file_arg, dtype={
        #"TIMESTAMP": int, #NA
        "MARK": str,
        "MODEL": str, 
        #"CAR_YEAR": int, #NA
        "ENGINE_POWER": str, 
        "AUTOMATIC": str, 
        "VEHICLE_ID": str, 
        #"BAROMETRIC_PRESSURE(KPA)": int, #NA
        #"ENGINE_COOLANT_TEMP": int, #NA
        "FUEL_LEVEL": str, 
        "ENGINE_LOAD": str, 
        #"AMBIENT_AIR_TEMP": str, 
        #"ENGINE_RPM": int, #NA
        #"INTAKE_MANIFOLD_PRESSURE": int, #NA
        "MAF": str, 
        "LONG TERM FUEL TRIM BANK 2": str, 
        "FUEL_TYPE": str, 
        #"AIR_INTAKE_TEMP": int, #NA
        #"FUEL_PRESSURE": str, 
        #"SPEED": int, #NA
        "SHORT TERM FUEL TRIM BANK 2": str, 
        "SHORT TERM FUEL TRIM BANK 1": str, 
        "ENGINE_RUNTIME": str, 
        "THROTTLE_POS": str,
        "DTC_NUMBER": str,
        "TROUBLE_CODES": str,
        "TIMING_ADVANCE": str,
        "EQUIV_RATIO": str, 
        #"MIN": int, #NA
        #"HOURS": int, #NA
        #"DAYS_OF_WEEK": int, #NA
        #"MONTHS": int, #NA
        #"YEAR": int, #NA
    })

    data_frame = data_frame[data_frame['VEHICLE_ID'].isin(SELECTED_VEHICLES)]

    # Convertir la columna TIMESTAMP a datetime
    timestamp = pandas.to_datetime(data_frame['TIMESTAMP'], unit='ms', errors='coerce')
    year = timestamp.dt.year
    day = timestamp.dt.dayofyear

    # Agrupar por VEHICLE_ID, año y día usando variables auxiliares
    grouped_vehicles = data_frame.groupby([data_frame['VEHICLE_ID'], year, day]).groups.items()
    for (vehicle_id, year, day), idx in grouped_vehicles:
        group = data_frame.loc[idx]
        filename = f"{CSV_FOLDER}/data_{vehicle_id}_y_{year}_d_{day}.csv"
        group.to_csv(filename, index=False)
        logging.info('Creating file: %s', filename)


def _remove_rosbag_files():
    logging.info('Removing docker/accountability/files/rosbags folder files')

    [shutil.rmtree(folder.path) for folder in os.scandir(ROSBAGS_FOLDER) if folder.is_dir()]


def _unzip_file(zip_file: str, extract_folder: str):
    logging.info('Unzipping file: %s', zip_file)

    with zipfile.ZipFile(zip_file, READ_MODE) as zip_ref:
        zip_ref.extractall(extract_folder)


def _remove_unneeded_files():
    logging.info('Removing unneeded files')

    [shutil.rmtree(f"{folder.path}/") 
     for folder in os.scandir(ROSBAGS_FOLDER) if folder.is_dir() and 'Test_base' in folder.path]

    for folder in os.scandir(ROSBAGS_FOLDER):
        if folder.is_dir():
            for file in os.scandir(folder):
                if 'rosbag' in file.name:
                    os.rename(file.path, f"{ROSBAGS_FOLDER}/{file.name}")
            shutil.rmtree(folder.path) 

    shutil.rmtree(TMP_FOLDER)


def _extract_rosbags(zip_file_arg: str):
    _remove_rosbag_files()

    _unzip_file(zip_file_arg, TMP_FOLDER)

    [_unzip_file(zip_file.path, ROSBAGS_FOLDER) 
     for zip_file in os.scandir(TMP_FOLDER) if zip_file.is_file()]

    _remove_unneeded_files()


def _read_networks_config_file():
    configuration = {}

    with open(CONF_FILE, READ_MODE, encoding=ENCODING) as file:
        try:
            config_dict = yaml.load(file, Loader=yaml.SafeLoader)
            for key in config_dict:
                configuration[key] = config_dict[key]

        except yaml.YAMLError as ex:
            logging.error("%s", ex)

    return configuration


def _get_conf_file_and_file(rosbag: str, configuration):
    path = pathlib.Path(rosbag)
    file_str = str(pathlib.Path(*path.parts[4:]))
    conf_file = configuration['configuration']

    return conf_file, file_str


def _run_and_wait_containers(docker_client, docker_command: str):
    logging.info(docker_command)
    subprocess.run([docker_command], shell=True, check=True)

    acolyte_container = docker_client.containers.get(CONTAINER_ACCOUNTABILITY_NAME)
    while acolyte_container in docker_client.containers.list():
        time.sleep(10)

    logging.info('Container %s ended', acolyte_container.name)
    _stop_containers(docker_client)


def _stop_containers(docker_client):
    for container in docker_client.containers.list():
        if container.name in CONTAINER_NAMES:
            logging.info('Stopping container %s', container.name)
            container.stop()


def _run_containers(docker_client):
    try:
        conf = _read_networks_config_file()

        rosbags = _get_directories_from_folder(ROSBAGS_FOLDER)
        csv_files = [file.path
                     for file in os.scandir(CSV_FOLDER) if file.is_file() and '.csv' in file.path]

        for network, configuration in conf.items():
            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

            logging.info('Starting network %s', network)
            logging.info('=======================================================================')
            logging.info('Total rosbags: %d', len(rosbags))

            i = 1
            for rosbag in rosbags:
                logging.info('-------------------------------------------------------------------')
                logging.info('Rosbag %d / %d', i, len(rosbags))

                conf_file, file = _get_conf_file_and_file(rosbag, configuration)

                var_env = f"NETWORK='{network}' CONF_FILE='{conf_file}' ROSBAG='{file}'"
                docker_command = f"{var_env} docker compose -f docker/compose/compose.yaml --profile {network} up -d"

                _run_and_wait_containers(docker_client, docker_command)

                i += 1

            logging.info('=======================================================================')
            logging.info('Total CSVs: %d', len(csv_files))

            i = 1
            for csv in csv_files:
                logging.info('-------------------------------------------------------------------')
                logging.info('CSV %d / %d', i, len(csv_files))

                conf_file, file = _get_conf_file_and_file(csv, configuration)

                var_env = f"NETWORK='{network}' CONF_FILE='{conf_file}' CSV='{file}'"
                docker_command = f"{var_env} docker compose -f docker/compose/compose.yaml --profile {network} up -d"

                _run_and_wait_containers(docker_client, docker_command)

                i += 1

            logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')

    except KeyboardInterrupt:
        _stop_containers(docker_client)
        logging.info('Stopping orchestrator\n')

        sys.exit()


def _get_rosbag_metrics_folder(file):
    return file.is_dir() and '.csv' not in file.path


def _get_csv_metrics_folder(file):
    return file.is_dir() and '.csv' in file.path


def _get_concat_metrics_by_network(folder, networks: list, conditional_function):
    if len(networks) == 0:
        logging.error('The list of networks is empty')
        return []

    if conditional_function is None or conditional_function == '':
        logging.error('The conditional_function is not valid')
        return []

    total_metrics_by_network = {network: {metric: [] for metric in METRICS} for network in networks}

    network_index = 0
    for metrics_folders_by_network in folder:
        if network_index >= len(networks):
            break
        
        network = networks[network_index]
        if network not in metrics_folders_by_network:
            continue

        metrics_by_network = {metric: [] for metric in METRICS}

        rosbags_metrics_folders = [file.path for file in os.scandir(metrics_folders_by_network)
                                    if conditional_function(file)]
        for rosbag_metric_folder in rosbags_metrics_folders:
            rosbag_metrics_file = os.listdir(rosbag_metric_folder)[0]
            rosbag_metric_csv = os.path.join(rosbag_metric_folder, rosbag_metrics_file)
            data_frame_rosbag_metric = pandas.read_csv(rosbag_metric_csv)
            for metric in METRICS:
                if metric != 'timestamp':
                    metrics_by_network[metric].append(data_frame_rosbag_metric[metric])
                else:
                    elapsed_seconds = pandas.to_datetime(data_frame_rosbag_metric[metric][len(data_frame_rosbag_metric[metric])-1]) - pandas.to_datetime(data_frame_rosbag_metric[metric][0])
                    metrics_by_network[metric].append(pandas.Series({0: elapsed_seconds.seconds}))

        for metric in METRICS:
            # Concatenate pandas objects along a particular axis
            total_metrics_by_network[network][metric] = pandas.concat(metrics_by_network[metric], ignore_index=False)

        network_index += 1

    return total_metrics_by_network


def _get_min(value: float):
    return value.min().round(ROUND_DIGITS)


def _get_max(value: float):
    return value.max().round(ROUND_DIGITS)


def _get_mean(value: float):
    return value.mean().round(ROUND_DIGITS)


def _print_table(header: str, metrics_dictionary: dict, value_function):
    table = PrettyTable()
    table.title = header
    table.field_names = ["network"] + METRICS

    for network in metrics_dictionary.keys():
        mean_metrics = [network]
        for metric in METRICS:
            mean_metrics.append(value_function(metrics_dictionary[network][metric]))

        table.add_row(mean_metrics)

    logging.info(table)


def _manage_data():
    network_folders = _get_directories_from_folder(METRICS_FOLDER)
    networks = [network.split("/")[len(network.split("/"))-1] for network in network_folders]
    if len(networks) == 0:
        logging.error('There is no data available for treatment.')
        return

    total_rosbag_metrics_by_network = _get_concat_metrics_by_network(network_folders, networks, _get_rosbag_metrics_folder)
    #_print_table("ROSBAGS MIN:", total_rosbag_metrics_by_network, _get_min)
    #_print_table("ROSBAGS MAX:", total_rosbag_metrics_by_network, _get_max)
    _print_table("ROSBAGS MEAN:", total_rosbag_metrics_by_network, _get_mean)

    logging.info('\n====================================================================================\n')

    total_csv_metrics_by_network = _get_concat_metrics_by_network(network_folders, networks, _get_csv_metrics_folder)
    #_print_table("CSV MIN:", total_csv_metrics_by_network, _get_min)
    #_print_table("CSV MAX:", total_csv_metrics_by_network, _get_max)
    _print_table("CSV MEAN:", total_csv_metrics_by_network, _get_mean)


def _create_graphics():
    logging.info("Creating graphics...")


def _execute_script(arguments):
    if arguments.unzip:
        _extract_rosbags(arguments.file_to_unzip)

    if arguments.split:
        _split_csv(arguments.file_to_split)

    if arguments.execute:
        docker_client = docker.from_env()
        _run_containers(docker_client)

    if arguments.data:
        _manage_data()

    if arguments.graphics:
        _create_graphics()


def _configure_logging():
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


def _parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)

    main_argument_group = parser.add_argument_group(
        "required named arguments")

    main_argument_group.add_argument(
        "-e",
        "--execute",
        action="store_true",
        help="execute the Docker containers"
    )

    main_argument_group.add_argument(
        "-u",
        "--unzip",
        action="store_true",
        help="unzip the specified file (the rosbags folder files will be deleted)"
    )

    main_argument_group.add_argument(
        "-fu",
        "--file_to_unzip",
        default='docker/accountability/files/19469198.zip',
        required='unzip' in sys.argv,
        help="path file to unzip"
    )

    main_argument_group.add_argument(
        "-s",
        "--split",
        action="store_true",
        help="split the specified file (the csv folder files will be deleted)"
    )

    main_argument_group.add_argument(
        "-fs",
        "--file_to_split",
        default='docker/accountability/files/exp1_14drivers_14cars_dailyRoutes.csv',
        required='split' in sys.argv,
        help="path file to split"
    )

    main_argument_group.add_argument(
        "-d",
        "--data",
        action="store_true",
        help="extract data"
    )

    main_argument_group.add_argument(
        "-g",
        "--graphics",
        action="store_true",
        help="generate graphics from the data"
    )

    return parser.parse_args()


def _validate_arguments(arguments):
    are_valid = True

    if arguments.unzip:
        if arguments.file_to_unzip is (None or '') or not os.path.exists(arguments.file_to_unzip):
            are_valid = False
            logging.error('The specified ZIP file to unzip is not valid. Please review it.')

    if arguments.split:
        if arguments.file_to_split is (None or '') or not os.path.exists(arguments.file_to_split):
            are_valid = False
            logging.error('The specified CSV file to split is not valid. Please review it.')

    return are_valid


def main():
    """
    Main function.
    """

    _configure_logging()

    logging.info('Starting orchestrator...')

    arguments = _parse_arguments()
    arguments_are_valid = _validate_arguments(arguments)
    if not arguments_are_valid:
        logging.critical('Arguments are not valid.')
        logging.info('Stopping orchestrator\n')

        sys.exit()

    _execute_script(arguments)

    logging.info('Stopping orchestrator\n')


if __name__ == "_main_":
    main()
