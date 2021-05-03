import docker
import main_application.constants.docker_constants as ivr_const
import main_application.constants.test_docker_constants as test_ivr_const


# Modify and check IVR status by looking at Docker container status
class IVRServerStatus:
    def __init__(self, test=False):
        self.client = docker.from_env()
        self.test = test

    def build_and_run_ivr(self):
        if not self.test:
            self.client.containers.run(name=ivr_const.DOCKER_CONTAINER_NAME, image=ivr_const.DOCKER_IMAGE_PATH,
                                       command=ivr_const.DOCKER_COMMANDS, volumes=ivr_const.DOCKER_VOLUMES,
                                       network_mode=ivr_const.NETWORK_MODE, detach=True)
        else:
            self.client.containers.run(name=test_ivr_const.DOCKER_CONTAINER_NAME, image=test_ivr_const.DOCKER_IMAGE_PATH,
                                       command=test_ivr_const.DOCKER_COMMANDS, volumes=test_ivr_const.DOCKER_VOLUMES,
                                       network_mode=test_ivr_const.NETWORK_MODE, detach=True)

    def turn_on_ivr(self):
        ivr_container = self.client.containers.get(ivr_const.DOCKER_CONTAINER_NAME)
        ivr_container.start()

    def turn_off_ivr(self):
        ivr_container = self.client.containers.get(ivr_const.DOCKER_CONTAINER_NAME)
        ivr_container.stop()

    def check_ivr_status(self):
        try:
            ivr_container = self.client.containers.get(ivr_const.DOCKER_CONTAINER_NAME)
        except:
            return "build"

        ivr_container_state = ivr_container.attrs
        ivr_server_online = ivr_container_state["State"]["Status"] == "running"

        return ivr_server_online


