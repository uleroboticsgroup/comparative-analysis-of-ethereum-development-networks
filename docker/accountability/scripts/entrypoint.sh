#!/bin/bash

NETWORK=$(eval echo $1)
CONF_FILE=$(eval echo $2)
ROSBAG=$(eval echo $3)
CSV=$(eval echo $4)

LOGS_FOLDER="/app/ACOLYTE/logs/"
LOGS_ROSBAG_FOLDER="${LOGS_FOLDER}${NETWORK}/${ROSBAG}/"
LOGS_CSV_FOLDER="${LOGS_FOLDER}${NETWORK}/${CSV}/"
ROSBAG_FOLDER="/app/rosbags/${ROSBAG}/"
CSV_FILE="/app/csv/${CSV}"

METRICS_ROSBAG_FOLDER="${NETWORK}/${ROSBAG}/"
METRICS_CSV_FOLDER="${NETWORK}/${CSV}/"


. /opt/ros/humble/setup.sh
. /app/.venv/bin/activate

cd /app/ACOLYTE
cp ${CONF_FILE} bcubed-config.yaml

# Wait for the blockchain network container to be up
if [ "${NETWORK}" = "ganache" ]; then
    sleep 10
else
    sleep 4
fi


process_rosbag() {
    if [ ! -d ${LOGS_ROSBAG_FOLDER} ]; then
        mkdir -p ${LOGS_ROSBAG_FOLDER}
    fi

    sed -i 's\/tf:\/tf_drop:\' topics-config.yaml

    for file_name in ${ROSBAG_FOLDER}/*.mcap;
        do

            export ACOLYTE_CONF_FILE=./topics-config.yaml && ./monitor.sh ${METRICS_ROSBAG_FOLDER} acolyte -a store -i ${file_name} -r test -w rosbag
            rm /app/BCubed/src/bcubed/blockchain/solidity/BCubedContract.json

            cd ${LOGS_FOLDER}
            for log_name in ${LOGS_FOLDER}*.log*;
                do 
                    if [ -f ${log_name} ]; then
                        file="$(basename -- ${log_name})"
                        mv ${file} "${NETWORK}/${ROSBAG}/${file}"
                    fi
                done
        done
}

process_csv() {
    if [ ! -d ${LOGS_CSV_FOLDER} ]; then
        mkdir -p ${LOGS_CSV_FOLDER}
    fi

    export ACOLYTE_CONF_FILE=./obd-config.yaml && ./monitor.sh ${METRICS_CSV_FOLDER} acolyte -a store -i ${CSV_FILE} -r test -w obd_excel
    rm /app/BCubed/src/bcubed/blockchain/solidity/BCubedContract.json

    cd ${LOGS_FOLDER}
    for log_name in ${LOGS_FOLDER}*.log*;
        do 
            if [ -f ${log_name} ]; then
                file="$(basename -- ${log_name})"
                mv ${file} "${NETWORK}/${CSV}/${file}"
            fi
        done
}


if [[ ! -z "$ROSBAG" ]] && [[ -z "$CSV" ]]; then
    echo "ROSBAG"
    process_rosbag
elif [[ -z "$ROSBAG" ]] && [[ ! -z "$CSV" ]]; then
    echo "CSV"
    process_csv
elif [[ -z "$ROSBAG" ]] && [[ -z "$CSV" ]]; then
    echo "ERROR: Neither ROSBAG nor CSV was provided."
fi