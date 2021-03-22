# All other constants
import sys
import os

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

DOCKER_CONTAINER_NAME = "gp_ivr"
DOCKER_IMAGE_PATH = "122max122/gp_ivr:gp_ivr"
DOCKER_VOLUMES = {application_path + "/asterisk_docker/conf/asterisk-build/voice":
                      {"bind": "/var/lib/asterisk/sounds/voice/", "mode": "rw"},
                  application_path + "/asterisk_docker/conf/asterisk-build/extensions.conf":
                      {"bind": "/etc/asterisk/extensions.conf", "mode": "rw"},
                  application_path + "/asterisk_docker/conf/asterisk-build/manager.conf":
                      {"bind": "/etc/asterisk/manager.conf", "mode": "rw"},
                  application_path + "/asterisk_docker/conf/asterisk-build/modules.conf":
                      {"bind": "/etc/asterisk/modules.conf", "mode": "rw"},
                  application_path + "/asterisk_docker/conf/asterisk-build/pjsip.conf":
                      {"bind": "/etc/asterisk/pjsip.conf", "mode": "rw"},
                  application_path + "/asterisk_docker/conf/asterisk-build/Master.csv":
                      {"bind": "/var/log/asterisk/cdr-csv/Master.csv", "mode": "rw"}}
DOCKER_COMMANDS = "bash -c 'chown -R :1024 /etc/asterisk && chmod -R 777 /etc/asterisk && chown -R :1024 " \
                  "/var/lib/asterisk/sounds/voice && chmod -R 777 /var/lib/asterisk/sounds/voice && /bin/sh /start.sh'"
NETWORK_MODE = "host"
