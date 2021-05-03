from main_application.voiceflow_to_json.voiceflow_to_json import GetVoiceflowInformation, VoiceflowToJson
from tests.test_main_application.integration_tests.voiceflow_constants import ALEXA_SIMPLIFIED_JSON, GOOGLE_SIMPLIFIED_JSON
from tests.test_main_application.integration_tests.voiceflow_constants import USERNAME, PASSWORD, WORKSPACE, PROJECT_ALEXA, PROJECT_GOOGLE

get_voiceflow_information = GetVoiceflowInformation(USERNAME, PASSWORD)

# Tests the connection between voiceflow_to_json.py and json_decoder.py

def test_voiceflow_alexa():
    headers = get_voiceflow_information.get_auth_header()
    project_name = PROJECT_ALEXA
    workspace_name = WORKSPACE
    voiceflow_to_json = VoiceflowToJson(workspace_name, project_name, headers)
    simplified_json = voiceflow_to_json.simplified_json()
    assert simplified_json == ALEXA_SIMPLIFIED_JSON

def test_voiceflow_google():
    headers = get_voiceflow_information.get_auth_header()
    project_name = PROJECT_GOOGLE
    workspace_name = WORKSPACE
    voiceflow_to_json = VoiceflowToJson(workspace_name, project_name, headers)
    simplified_json = voiceflow_to_json.simplified_json()
    assert simplified_json == GOOGLE_SIMPLIFIED_JSON



