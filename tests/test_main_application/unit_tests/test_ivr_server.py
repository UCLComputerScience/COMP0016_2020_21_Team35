import docker
from main_application.constants.docker_constants import DOCKER_CONTAINER_NAME
from main_application.settings_modifications.ivr_server import IVRServerStatus

client = docker.from_env()

ivr_server = IVRServerStatus(test=True)

def check_ivr_state():
    ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)
    ivr_container_state = ivr_container.attrs
    ivr_server_online = ivr_container_state["State"]["Status"] == "running"
    return ivr_server_online

def test_build_and_run_ivr():
    try:
        ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)
    except:
        ivr_container = None

    if ivr_container != None:
        ivr_container.stop()
        ivr_container.remove()

    ivr_server.build_and_run_ivr()
    assert client.containers.get(DOCKER_CONTAINER_NAME)

def test_turn_on_ivr():
    ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)
    ivr_server_online = check_ivr_state()

    if ivr_server_online:
        ivr_container.stop()

    ivr_server.turn_on_ivr()
    ivr_server_online = check_ivr_state()
    assert ivr_server_online

def test_turn_off_ivr():
    ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)
    ivr_server_online = check_ivr_state()

    if not ivr_server_online:
        ivr_container.start()

    ivr_server.turn_off_ivr()
    ivr_server_online = check_ivr_state()
    assert not ivr_server_online

def test_check_ivr_status_online():
    ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)
    ivr_server_online = check_ivr_state()

    if not ivr_server_online:
        ivr_container.start()

    status = ivr_server.check_ivr_status()
    assert status

def test_check_ivr_status_offline():
    ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)
    ivr_server_online = check_ivr_state()

    if ivr_server_online:
        ivr_container.stop()

    status = ivr_server.check_ivr_status()
    assert not status

def test_check_ivr_status_build():
    ivr_container = client.containers.get(DOCKER_CONTAINER_NAME)

    ivr_container.stop()
    ivr_container.remove()

    status = ivr_server.check_ivr_status()
    assert status == "build"

