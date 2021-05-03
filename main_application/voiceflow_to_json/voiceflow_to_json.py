import requests
import json

from main_application.voiceflow_to_json.json_decoder import SimplifiedJson


# HTTP requests to get out key information and authenticate user
class GetVoiceflowInformation:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    # User authentication - gets out token
    def get_auth_header(self):
        AUTH_URL = "https://api.voiceflow.com/session"
        payload = {"user":{"email":self.email,"password":self.password}}
        headers = {"Content-type": "application/json"}
        try:
            auth = requests.put(AUTH_URL, data=json.dumps(payload), headers=headers)
            token = auth.json()["token"]
            header = {"Authorization": token}
        except Exception:
            header = "None"
        return header

    def get_workspaces(self, headers):
        workspaces = []
        WORKSPACE_URL = "https://api.voiceflow.com/workspaces"
        workspace_request = requests.get(WORKSPACE_URL, headers=headers).json()
        for workspace in workspace_request:
            workspaces.append({"name": workspace["name"], "id": workspace["team_id"]})
        return workspaces

    def get_workspace_names(self, workspaces):
        workspace_names = []
        for workspace in workspaces:
            workspace_names.append(workspace["name"])
        return workspace_names

    def get_projects(self, headers, workspace_id):
        projects = []
        PROJECT_URL = "https://api.voiceflow.com/v2/workspaces/" + workspace_id + "/projects"
        project_request = requests.get(PROJECT_URL, headers=headers).json()
        for project in project_request:
            int_id = int(project["devVersion"], 16) + 1
            hex_id = format(int_id, "x")
            project_id = str(hex_id)
            projects.append({"name": project["name"], "id": project_id})
        return projects

    def get_project_names(self, projects):
        project_names = []
        for project in projects:
            project_names.append(project["name"])
        return project_names

    def get_workspace_id(self, workspace_name, workspaces):
        for workspace in workspaces:
            if workspace["name"] == workspace_name:
                return workspace["id"]


# Use HTTP requests to get out Voiceflow JSON - then simplify
class VoiceflowToJson:
    def __init__(self, workspace_name, project_name, headers):
        self.workspace_name = workspace_name
        self.project_name = project_name
        self.headers = headers

    def get_workspace_id(self):
        WORKSPACE_URL = "https://api.voiceflow.com/workspaces"
        workspaces = requests.get(WORKSPACE_URL, headers=self.headers).json()
        for workspace in workspaces:
            if workspace["name"] == self.workspace_name:
                    workspace_id = workspace["team_id"]
                    return workspace_id

    # Intents are choices such as yes and no - get their values out from Voiceflow - use with Google flows
    def get_intents(self):
        project_id = self.get_project_id()
        hex_id = hex(int(project_id, 16) - 1)[2:]
        project_id = str(hex_id)
        VERSIONS_URL = "https://api.voiceflow.com/v2/versions/" + project_id
        versions = requests.get(VERSIONS_URL, headers=self.headers).json()
        intents = {}
        for key in versions["platformData"]["intents"]:
            intents[key["key"]] = key["name"]
        return intents

    def get_project_id(self):
        workspace_id = self.get_workspace_id()
        PROJECT_URL = "https://api.voiceflow.com/v2/workspaces/" + workspace_id + "/projects"
        projects = requests.get(PROJECT_URL, headers=self.headers).json()
        for project in projects:
            if project["name"] == self.project_name:
                int_id = int(project["devVersion"], 16) + 1
                hex_id = format(int_id, "x")
                project_id = str(hex_id)
                return project_id

    def get_diagram_json(self):
        project_id = self.get_project_id()
        DIAGRAM_URL = "https://api.voiceflow.com/v2/diagrams/" + project_id
        diagram_json = requests.get(DIAGRAM_URL, headers=self.headers).json()
        return diagram_json

    def simplified_json(self):
        diagram_json = self.get_diagram_json()
        intents = self.get_intents()
        json_object = SimplifiedJson(diagram_json, intents)
        simplified_json = json_object.simplify_json()
        return simplified_json


# Uses Voiceflow file to create simplified JSON
class VoiceflowFileToJson:
    def __init__(self, filepath):
        self.filepath = filepath

    def assign_json_dict(self):
        with open(self.filepath) as file:
            voiceflow_json = json.load(file)

        return voiceflow_json

    def decode_root_diagram(self, voiceflow_json):
        root_diagram = voiceflow_json["version"]["rootDiagramID"]
        diagram_json = voiceflow_json["diagrams"][root_diagram]
        return diagram_json

    def get_intents(self, voiceflow_json):
        intents = {}
        json_intents = voiceflow_json["version"]["platformData"]["intents"]
        for key in json_intents:
            intents[key["key"]] = key["name"]
        return intents

    def simplified_json(self):
        voiceflow_json = self.assign_json_dict()
        diagram_json = self.decode_root_diagram(voiceflow_json)
        intents = self.get_intents(voiceflow_json)

        json_object = SimplifiedJson(diagram_json, intents)
        simplified_json = json_object.simplify_json()
        return simplified_json