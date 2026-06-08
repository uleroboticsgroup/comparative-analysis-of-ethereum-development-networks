FROM osrf/ros:humble-desktop-full-jammy

WORKDIR /app

ARG NETWORK
ARG CONF_FILE
ARG ROSBAG
ARG CSV

RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3.10-venv pip -y
RUN apt-get install ros-humble-rosbag2-storage-mcap ros-humble-cv-bridge ros-humble-navigation2 -y

RUN useradd -ms /bin/bash admin
RUN chown admin /app

USER admin

RUN git clone https://github.com/uleroboticsgroup/BCubed.git
RUN git clone https://github.com/uleroboticsgroup/ACOLYTE.git

RUN python3 -m venv .venv && . .venv/bin/activate && \
    pip install -r BCubed/requirements.txt && pip install -e BCubed/ && \
    pip install -r ACOLYTE/requirements.txt && pip install -e ACOLYTE/

COPY --chown=admin docker/accountability/scripts/entrypoint.sh /app/
COPY --chown=admin docker/accountability/scripts/monitor.sh /app/ACOLYTE/

COPY --chown=admin docker/accountability/config/config_* /app/ACOLYTE/
COPY --chown=admin docker/accountability/files/rosbags/ /app/rosbags/
COPY --chown=admin docker/accountability/files/csv/ /app/csv/

CMD ["$NETWORK", "$CONF_FILE", "$ROSBAG", "$CSV"]

ENTRYPOINT ["./entrypoint.sh"]
