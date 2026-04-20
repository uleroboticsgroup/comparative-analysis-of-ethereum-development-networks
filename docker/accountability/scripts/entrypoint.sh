#!/bin/bash

NETWORK=$(eval echo $1)
CONF_FILE=$(eval echo $2)
ROSBAG=$(eval echo $3)

LOGS_FOLDER="/app/ACOLYTE/logs/"
LOGS_ROSBAG__FOLDER="${LOGS_FOLDER}${NETWORK}/${ROSBAG}/"
ROSBAG_FOLDER="/app/rosbags/${ROSBAG}/"

METRICS_FOLDER="${NETWORK}/${ROSBAG}/"

. /opt/ros/humble/setup.sh
. /app/.venv/bin/activate

cd /app/ACOLYTE
cp ${CONF_FILE} bcubed-config.yaml

if [ ! -d ${LOGS_ROSBAG__FOLDER} ]; then
    mkdir -p ${LOGS_ROSBAG__FOLDER}
fi

sed -i 's\/tf:\/tf_drop:\' topics-config.yaml

# Wait for the blockchain network container to be up
sleep 10

for file_name in ${ROSBAG_FOLDER}/*.mcap;
    do
    ./monitor.sh ${METRICS_FOLDER} acolyte -a store -i ${file_name} -r test -w rosbag
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
