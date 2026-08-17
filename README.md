# Comparative analysis of Ethereum development networks for the purpose of accountability in autonomous systems
The objective of this repository is to automate a comparative analysis of different Ethereum development networks for the purpose of accountability in autonomous systems. The accountability solution, which is employed, is designated ACOLYTE and is available on GitHub [https://github.com/uleroboticsgroup/ACOLYTE](https://github.com/uleroboticsgroup/ACOLYTE). ACOLYTE facilitates the automated extraction of data from autonomous systems through a variety of modules. The selected modules for this comparative are two. The first one reads information through a rosbag file for ROS 2-based robots. A rosbag is defined as a file containing timestamped messages. ROS 2 is the evolution of ROS (Robot Operating System), the de facto standard in robotics. The second module reads information from a CSV file, which contains information extracted from the OBD-II port for vehicles. The term OBD refers to the self-diagnostic and reporting capability of a vehicle. The functionality of an OBD system is to enable the acquisition of data regarding the various sub-systems of a vehicle. It is important to note that, by default, the ROS 2-based dataset utilized in this analysis is [https://zenodo.org/records/19469198](https://zenodo.org/records/19469198), whereas the OBD-II-based dataset is [https://www.kaggle.com/datasets/cephasax/obdii-ds3?select=exp1_14drivers_14cars_dailyRoutes.csv](https://www.kaggle.com/datasets/cephasax/obdii-ds3?select=exp1_14drivers_14cars_dailyRoutes.csv).

The proposed Ethereum development networks are the following ones:

- Ganache
- Hardhat node
- Anvil
- Geth --dev

The `orchestratory.py` script reads the `network.yaml` configuration file and for each Ethereum development network read, all the rosbag files located in `docker/accountability/files/rosbags` and all the CSV files located in `docker/accountability/files/csv` are traversed. The script executes a Docker Compose command to build and run two containers for each pair of network and file (rosbag or CSV file). One container is responsible for managing the Ethereum development network and another one is responsible for the accountability solution execution. The second container awaits until the network container is ready and executes the `monitor.sh` script with a particular ACOLYTE command for the specified development network and file (rosbag or CSV file). The `monitor.sh` script is responsible for monitoring the performance and timing metrics of the ACOLYTE process. Once the execution of the `monitor.sh` script is complete, the ACOLYTE logs and the script output metric folders are copied to a host folder. The `orchestrator.py` script waits for the accountability container to end, and then it stops all the containers and continues with the next pair of network and file (rosbag or CSV file).

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
Configure the networks to be executed in the `networks.yaml` file. The default configuration is as follows:

```
ganache:
  container: ganache
  configuration: config_ganache.yaml

hardhat:
  container: hardhat
  configuration: config_hardhat.yaml

anvil:
  container: anvil
  configuration: config_anvil.yaml

geth:
  container: geth
  configuration: config_geth.yaml
```

## Execute `orchestrator.py`

The basic execution of the `orchestrator.py` script is executing the following command:

```
(.venv) python3 orchestrator.py -e
```

This command will build and run the accountability container and a network container each time as many files (rosbags and CSV files) and networks are configured. The rosbag files used will be located in the `docker/accountability/files/rosbags` directory, the CSV files used will be localted in the `docker/accountability/files/csv` directory, and the networks used will be configured in the `networks.yaml` file.

Two files will be extracted from the accountability Docker container for each configured network and file (rosbag or CSV). The first is the data metrics extracted from the execution of ACOLYTE, i.e. the analysed accountability solution, using the `docker/accountability/scripts/monitor.sh` script. Secondly, the ACOLYTE execution log file.

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

### Process the data metrics by network and type of file (rosbag or CSV) to obtain ACOLYTE performance and timing data
After execute the `orchestrator.py -e` command, the following command can be executed:

```
(.venv) python3 orchestrator.py -d
```

The metrics stored in the `docker/compose/data/metrics/` directory, as well as some data stored in the `docker/compose/data/logs/` directory, will be processed according to the network and file type (rosbag or CSV) in order to obtain ACOLYTE performance and timing data, depending on the network and file type. Output example:

```
INFO:root:Starting orchestrator...
INFO:root:+--------------------------------------------------------------------------------------------------------------------+
|                                                      ROSBAGs                                                       |
+---------+-----------+---------+---------------+---------+---------------+--------------+----------+----------------+
| network | timestamp | cpu_pct | mem_rss_bytes | mem_pct |   disk_rchar  |  disk_wchar  | records  | time_by_record |
+---------+-----------+---------+---------------+---------+---------------+--------------+----------+----------------+
| hardhat |   18.556  |  52.589 | 218866574.222 |   0.63  | 523962740.111 | 11762540.667 | 2528.444 |     0.008      |
|   geth  |   27.222  |  36.687 | 219300750.222 |  0.643  | 524616980.778 | 11763239.556 | 2528.444 |     0.011      |
| ganache |  175.111  |  7.201  |  219844608.0  |  0.666  | 525045918.778 | 11762793.444 | 2528.444 |     0.071      |
|  anvil  |   26.556  |  37.329 | 219895580.444 |  0.645  | 524610850.556 | 11762813.222 | 2528.444 |     0.011      |
+---------+-----------+---------+---------------+---------+---------------+--------------+----------+----------------+
INFO:root:+-------------------------------------------------------------------------------------------------------------------+
|                                                      OBD CSVs                                                     |
+---------+-----------+---------+---------------+---------+--------------+--------------+----------+----------------+
| network | timestamp | cpu_pct | mem_rss_bytes | mem_pct |  disk_rchar  |  disk_wchar  | records  | time_by_record |
+---------+-----------+---------+---------------+---------+--------------+--------------+----------+----------------+
| hardhat |   17.379  |  73.065 | 195561683.862 |  0.568  | 30590592.759 | 11748501.552 | 4251.172 |     0.005      |
|   geth  |   20.379  |  62.235 | 197852901.517 |   0.58  | 30590734.966 | 11748915.241 | 4251.172 |     0.006      |
| ganache |  172.862  |  9.493  | 196507153.655 |  0.599  | 30590507.207 | 11748878.69  | 4251.172 |     0.043      |
|  anvil  |   20.034  |  63.415 |  195907584.0  |  0.574  | 30590644.552 | 11748705.103 | 4251.172 |     0.005      |
+---------+-----------+---------+---------------+---------+--------------+--------------+----------+----------------+
INFO:root:Stopping orchestrator
```

Furthermore, two CSV files are stored: one relating to rosbags (`rosbag_data.csv`) and one relating to CSV files (`obd_csv_data.csv`). These include the minimum, maximum and mean values of each percentage metric the mean of the metrics, the execution time for each network and the time per record.

## Logging

The `orchestrator.py` script creates a log file each day that it is run. This file can be found in the `./logs` directory.
