# Execution example
The following example illustrates the execution of the `orchestrator.py` script. The following commands were typed to create and activate a virtual environment and install the necessary requirements:

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ (.venv) pip install -r requirements.txt
```

The datasets were then downloaded and located. First, the ROS 2-based dataset was downloaded from [https://zenodo.org/records/19469198](https://zenodo.org/records/19469198). Second, the OBD-II-based dataset was downloaded from [https://www.kaggle.com/datasets/cephasax/obdii-ds3?select=exp1_14drivers_14cars_dailyRoutes.csv](https://www.kaggle.com/datasets/cephasax/obdii-ds3?select=exp1_14drivers_14cars_dailyRoutes.csv). Finally, both datasets were located in the `docker/accountability/files/` directory.

After the datasets were ready, the `orchestrator.py` script was executed with the following command:

```
(.venv) python3 orchestrator.py -u -s -c -e -d
```

The script took several hours to execute. The log of the execution is available in the `example/` folder. The data extracted is available in the `example/data` folder. The CSV files that were generated are available in the `example/csv` folder.
