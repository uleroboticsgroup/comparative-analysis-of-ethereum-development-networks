# Comparative analysis of Ethereum development networks for accountability in autonomous systems purposes
The goal of this repository is to automate a comparative analysis of different Ethereum development networks for accountability in autonomous systems purposes. The accountability solution is ACOLYTE, which is available at GitHub [https://github.com/uleroboticsgroup/ACOLYTE](https://github.com/uleroboticsgroup/ACOLYTE). The proposed Ethereum development networks are the following ones:

- Ganache
- Hardhat node
- Anvil
- Geth --dev

The orchestratory.py script reads the `network.yaml` configuration file and for each Ethereum development network read, all the rosbag files located in `docker/accountability/files/rosbags` directory are traversed. The script executes a Docker Compose command to build and run two containers for each pair of network and rosbag file. One container is responsible for managing the Ethereum development network and another one is responsible for the accountability solution execution. The second container awaits until the network container is ready and executes the `monitor.sh` script with a particular ACOLYTE command for the specified development network and rosbag file. Once the `monitor.sh` execution is complete, the ACOLYTE logs and the script output folders are copied to a host folder. The script waits for the accountability container to end, and then it stops all the containers and continues with the next pair of network and rosbag file.

## Getting Started

### Create and activate a virtual environment (recommended)

```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Install the requirements
```
(.venv) pip install -r requirements.txt
```

### Configure the networks
Configure the networks to be executed in the `networks.yaml` file.

## Execute `orchestrator.py`

The basic execution of the `orchestrator.py` script is executing the following command:

```
(.venv) python3 orchestrator.py
```

This command will build and run the accountability container and a network container each time as many files (rosbags and CSV files) and networks are configured. The rosbag files used will be located in the `docker/accountability/files/rosbags` directory and the networks used will be configured in the `networks.yaml` file.

### Unzipping a Zenodo file

Download the Zenodo file from [https://zenodo.org/records/19469198](https://zenodo.org/records/19469198) and place the zip file in the `docker/accountability/files` directory. Then, execute the following command:

```
(.venv) python3 orchestrator.py -u
```

The file to be unzipped by default is `docker/accountability/files/19469198.zip`. This command will remove the files in the `docker/accountability/files/rosbags` directory, unzip the downloaded zip file, remove the unnecessary extracted files, and prepare the new rosbags in the `docker/accountability/files/rosbags` directory. Then, it will build and run the accountability container and a network container each time as many files (rosbags and CSV files) and networks are configured.

#### Unzipping a file that is different from the file named `docker/accountability/files/19469198.zip`

Execute the following command:

```
(.venv) python3 orchestrator.py -u -fu docker/accountability/files/<zip_file_name>.zip
```

### Splitting a Kaggle CSV file by specific days

Download the Kaggle file from [https://www.kaggle.com/datasets/cephasax/obdii-ds3?select=exp1_14drivers_14cars_dailyRoutes.csv](https://www.kaggle.com/datasets/cephasax/obdii-ds3?select=exp1_14drivers_14cars_dailyRoutes.csv) and place the file file in the `docker/accountability/files` directory. Then, execute the following command:

```
(.venv) python3 orchestrator.py -s
```

The file to be splitted by default is `docker/accountability/files/exp1_14drivers_14cars_dailyRoutes.csv`. This command will remove the files in the `docker/accountability/files/csv` directory, split the downloaded CSV file, and prepare the new CSV files in the `docker/accountability/files/csv` directory. Then, it will build and run the accountability container and a network container each time as many files (rosbags and CSV files) and networks are configured.

#### Splitting a file that is different from the file named `docker/accountability/files/exp1_14drivers_14cars_dailyRoutes.csv`

Execute the following command:

```
(.venv) python3 orchestrator.py -s -fs docker/accountability/files/<csv_file_name>.csv
```

## Logging

The `orchestrator.py` script creates a log file each day that it is run. This file can be found in the `./logs` directory.
