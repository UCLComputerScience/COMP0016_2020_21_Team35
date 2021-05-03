# Filepaths for running Docker while running tests
import os

path = os.path.dirname(__file__)

DOCKER_CONTAINER_NAME = "gp_ivr"
DOCKER_IMAGE_PATH = "122max122/gp_ivr:gp_ivr"
DOCKER_VOLUMES = {path + "../../../asterisk_docker/conf/asterisk-build/voice":
                      {"bind": "/var/lib/asterisk/sounds/voice/", "mode": "rw"},
                  path + "../../../asterisk_docker/conf/asterisk-build/extensions.conf":
                      {"bind": "/etc/asterisk/extensions.conf", "mode": "rw"},
                  path + "../../../asterisk_docker/conf/asterisk-build/manager.conf":
                      {"bind": "/etc/asterisk/manager.conf", "mode": "rw"},
                  path + "../../../asterisk_docker/conf/asterisk-build/modules.conf":
                      {"bind": "/etc/asterisk/modules.conf", "mode": "rw"},
                  path + "../../../asterisk_docker/conf/asterisk-build/pjsip.conf":
                      {"bind": "/etc/asterisk/pjsip.conf", "mode": "rw"},
                  path + "../../../asterisk_docker/conf/asterisk-build/Master.csv":
                      {"bind": "/var/log/asterisk/cdr-csv/Master.csv", "mode": "rw"}}
DOCKER_COMMANDS = "bash -c 'chown -R :1024 /etc/asterisk && chmod -R 777 /etc/asterisk && chown -R :1024 " \
                  "/var/lib/asterisk/sounds/voice && chmod -R 777 /var/lib/asterisk/sounds/voice && /bin/sh /start.sh'"
NETWORK_MODE = "host"
