import requests
import json
import getpass

class Simplified_Json:
    def __init__(self, diagram_json):
        self.diagram_json = diagram_json

    def get_nodes(self):
        nodes = []
        for node in self.diagram_json["nodes"]:
            nodes.append(node)
        return nodes

    def get_steps(self, node):
        steps = []
        node_data = self.diagram_json["nodes"][node]["data"]
        if("steps" in node_data):
            for step in node_data["steps"]:
                steps.append(step)
        return steps

    def get_dialogs(self, node):
        dialogs = []
        node_data = self.diagram_json["nodes"][node]["data"]
        if("dialogs" in node_data):
            for dialog in node_data["dialogs"]:
                if("content" in dialog):
                    dialogs.append(dialog["content"])

        return dialogs

    def get_target_nodes(self, node):
        target_nodes = set()
        node_data = self.diagram_json["nodes"][node]["data"]
        if("ports" in node_data):
            for port in node_data["ports"]:
                if("target" in port):
                    target_nodes.add(port["target"])

        return target_nodes

    def get_choices(self, node):
        node = self.diagram_json["nodes"][node]["data"]["steps"][0]
        node_data = self.diagram_json["nodes"][node]["data"]
        choice_nodes = []
        if("choices" in node_data):
            if("ports" in node_data):
                for port in node_data["ports"]:
                    if port["target"] != None:
                        choice_nodes.append(port["target"])
                if(len(choice_nodes) != 2):
                    raise Exception("Only deal with choice commands with 2 options")
            if(node_data["choices"][0]["intent"] == "AMAZON.NoIntent"):
                choice_nodes[0], choice_nodes[1] = choice_nodes[1], choice_nodes[0]
                if(node_data["choices"][1]["intent"] != "AMAZON.YesIntent"):
                    raise Exception("Must have Yes and No options only for a choice")
            elif(node_data["choices"][0]["intent"] != "AMAZON.YesIntent"):
                raise Exception("Must have Yes and No options only for a choice")
        return choice_nodes

    def is_interaction(self, node):
        if(self.diagram_json["nodes"][node]["type"] == "interaction"):
            return True
        else:
            return False

# Issue if the output from a choice command is connected to an individual text on voiceflow instead of to the whole box (should fix this).
# Likely fix is to swap so that the nodes in use in the simplified JSON will be the actual nodes containing dialog and the actual choice node.
# This will require some refactoring.
    def simplify_json(self):
        nodes = self.get_nodes()
        node_dict = {}
        node_dict["nodes"] = {}
        for node in nodes:
            node_steps = self.get_steps(node)
            choices = []
            if(node_steps):
                choices = self.get_choices(node)
            if(not self.get_dialogs(node)):
                if(not node_steps and not choices):
                    continue
            else:
                continue
            dialogs = []
            children = set()
            for step in node_steps:
                if(not self.is_interaction(step)):
                    dialogs.extend(self.get_dialogs(step))
                    children = children | self.get_target_nodes(step)
            if(not dialogs and not choices):
                continue
            node_dict["nodes"][node] = {}
            if(dialogs):
                node_dict["nodes"][node]["dialogs"] = dialogs
            if(children):
                node_dict["nodes"][node]["children"] = list(children)
            if(choices):
                node_dict["nodes"][node]["choices"] = choices

        return node_dict

class Get_Voiceflow_Information:
    def __init__(self, email, password):
        self.email = email
        self.password = password

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


class Voiceflow_To_Json:
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
        json_object = Simplified_Json(diagram_json)
        simplified_json = json_object.simplify_json()
        return simplified_json




# email = input("Email: ")
# password = getpass.getpass(prompt="Password: ")
# workspace = input("Workspace: ")
# project = input("Project: ")
# test = Voiceflow_To_Json(email, password, workspace, project)
# print(test.get_auth_header())
#test1 = test.simplified_json(test.get_auth_header())

# with open('/home/max/Documents/GP_IVR/voiceflow.json', 'w') as fp:
#     json.dump(test1, fp)
