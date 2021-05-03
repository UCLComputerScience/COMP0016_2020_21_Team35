from main_application.voiceflow_to_json.voiceflow_to_json import GetVoiceflowInformation, VoiceflowToJson
from tests.test_main_application.unit_tests.voiceflow_constants import USERNAME, PASSWORD, WORKSPACE1, WORKSPACE2, PROJECT_ALEXA, PROJECT_GOOGLE

get_voiceflow_information = GetVoiceflowInformation(USERNAME, PASSWORD)

def test_voiceflow_auth():
    headers = get_voiceflow_information.get_auth_header()
    try:
        auth = headers["Authorization"]
    except:
        auth = None

    assert auth

def test_get_workspaces_names():
    headers = get_voiceflow_information.get_auth_header()
    workspaces = get_voiceflow_information.get_workspaces(headers)
    workspace_names = get_voiceflow_information.get_workspace_names(workspaces)

    assert workspace_names == [WORKSPACE1, WORKSPACE2]

def test_project_names():
    headers = get_voiceflow_information.get_auth_header()
    workspaces = get_voiceflow_information.get_workspaces(headers)
    workspace_names = get_voiceflow_information.get_workspace_names(workspaces)
    workspace_id = get_voiceflow_information.get_workspace_id(workspace_names[1], workspaces)
    projects = get_voiceflow_information.get_projects(headers, workspace_id)
    project_names = get_voiceflow_information.get_project_names(projects)

    assert project_names == [PROJECT_ALEXA, PROJECT_GOOGLE]

def test_get_intents():
    headers = get_voiceflow_information.get_auth_header()
    project_name = PROJECT_GOOGLE
    workspace_name = WORKSPACE2

    voiceflow_to_json = VoiceflowToJson(workspace_name, project_name, headers)
    intents = voiceflow_to_json.get_intents()

    assert intents == {'v02t265u': 'yes', 'za3026aa': 'no'}






