import requests
import json
import copy

class Simplified_Json:
    def __init__(self, diagram_json, intents=None):
        self.diagram_json = diagram_json
        self.intents = intents

    def get_nodes(self):
        nodes = []
        for node in self.diagram_json["nodes"]:
            nodes.append(node)
        return nodes

    def get_step(self, node):
        step = ""
        node_data = self.diagram_json["nodes"][node]["data"]
        i = 0
        if("steps" in node_data):
            i += 1
            if(i > 1):
                raise Exception("There are more than one step. Not allowed for IVR")
            for step in node_data["steps"]:
                step = step

        return step

    def get_dialogs(self, node):
        dialogs = []
        node_data = self.diagram_json["nodes"][node]["data"]
        if("dialogs" in node_data):
            for dialog in node_data["dialogs"]:
                if("content" in dialog):
                    if dialog["content"]:
                        dialogs.append(dialog["content"])

        return dialogs

    def get_target_nodes(self, node):
        target_nodes = set()
        node_data = self.diagram_json["nodes"][node]["data"]
        if("ports" in node_data):
            for port in node_data["ports"]:
                if("target" in port):
                    child = port["target"]
                    if(child == None):
                        target_nodes.add(child)
                    elif ("steps" in self.diagram_json["nodes"][child]["data"]):
                        target_nodes.add(self.get_step(child))
                    else:
                        target_nodes.add(child)
        return target_nodes

    def get_choices(self, node):
        node = self.get_step(node)
        node_data = self.diagram_json["nodes"][node]["data"]
        choice_nodes = []
        yes_choices = ["AMAZON.YesIntent"]
        no_choices = ["AMAZON.NoIntent"]

        if not self.intents == None:
            for key in self.intents:
                if "yes" in self.intents[key]:
                    yes_choices.append(key)
                elif "no" in self.intents[key]:
                    no_choices.append(key)

        if("choices" in node_data):
            if("ports" in node_data):
                for port in node_data["ports"]:
                    if port["target"] != None:
                        target = port["target"]
                        if ("steps" in self.diagram_json["nodes"][target]["data"]):
                            choice_nodes.append(self.get_step(port["target"]))
                        else:
                            choice_nodes.append(port["target"])
                if(len(choice_nodes) != 2):
                    raise Exception("Only deal with choice commands with 2 options")
            if(node_data["choices"][0]["intent"] in no_choices):
                choice_nodes[0], choice_nodes[1] = choice_nodes[1], choice_nodes[0]
                if(node_data["choices"][1]["intent"] not in yes_choices):
                    print(node_data["choices"][1]["intent"])
                    raise Exception("Must have Yes and No options only for a choice")
            elif(node_data["choices"][0]["intent"] not in yes_choices):
                raise Exception("Must have Yes and No options only for a choice")
        return choice_nodes

    def is_interaction(self, node):
        if(self.diagram_json["nodes"][node]["type"] == "interaction"):
            return True
        else:
            return False

    def reorder_nodes(self, simplified_json):
        temp_map = copy.deepcopy(simplified_json)
        nodes = simplified_json["nodes"]
        for node in simplified_json["nodes"]:
            temp_node = nodes[node]
            if("children" in temp_node):
                try:
                    del temp_map["nodes"][temp_node["children"][0]]
                except:
                    pass
            elif("choices" in temp_node):
                for choice in temp_node["choices"]:
                    try:
                        del temp_map["nodes"][choice]
                    except:
                        pass

        first_node = next(iter(temp_map["nodes"]))
        new_json = {"nodes": {}}
        new_json["nodes"][first_node] = nodes[first_node]
        for node in nodes:
            if node == first_node:
                continue
            else:
                new_json["nodes"][node] = nodes[node]

        return new_json
        # curNode = first_node
        # lastNode = curNode
        # choice_nodes = []
        # while(nodes):
        #     if(curNode in nodes and "children" in nodes[curNode] and nodes[curNode]["children"][0] != None):
        #         curNode = nodes[curNode]["children"][0]
        #     elif(curNode in nodes and "choices" in nodes[curNode]):
        #         choice_nodes.append(nodes[curNode]["choices"][1])
        #         curNode = nodes[curNode]["choices"][0]
        #     elif choice_nodes:
        #         curNode = choice_nodes[-1]
        #         del choice_nodes[-1]
        #
        #     if(curNode in nodes):
        #         print(nodes)
        #         print(curNode)
        #         print(lastNode)
        #         new_json["nodes"][curNode] = nodes[curNode]
        #         if(lastNode in nodes):
        #             del nodes[lastNode]
        #         lastNode = curNode
        # print(new_json)
        # return new_json


# Issue if the output from a choice command is connected to an individual text on voiceflow instead of to the whole box (should fix this).
# Likely fix is to swap so that the nodes in use in the simplified JSON will be the actual nodes containing dialog and the actual choice node.
# This will require some refactoring.
    def simplify_json(self):
        nodes = self.get_nodes()
        node_dict = {}
        node_dict["nodes"] = {}
        for node in nodes:
            node_step = self.get_step(node)
            choices = []
            if(node_step):
                choices = self.get_choices(node)
            if(not self.get_dialogs(node)):
                if(not node_step and not choices):
                    continue
            else:
                continue
            dialogs = []
            children = set()
            if(not self.is_interaction(node_step)):
                dialogs.extend(self.get_dialogs(node_step))
                children = children | self.get_target_nodes(node_step)
            if(not dialogs and not choices):
                continue
            node_dict["nodes"][node_step] = {}
            if(dialogs):
                node_dict["nodes"][node_step]["dialogs"] = dialogs
            if(children):
                node_dict["nodes"][node_step]["children"] = list(children)
            if(choices):
                node_dict["nodes"][node_step]["choices"] = choices

        reordered_dict = self.reorder_nodes(node_dict)
        return reordered_dict

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


class GetVoiceflowSettings:
    def __init__(self, simplified_json):
        self.simplified_json = simplified_json

    def get_redirect_texts(self):
        redirect_texts = {}
        for node in self.simplified_json["nodes"]:
            if (not "children" in self.simplified_json["nodes"][node] or self.simplified_json["nodes"][node]["children"][0] == None) and not "choices" in self.simplified_json["nodes"][node]:
                if "dialogs" in self.simplified_json["nodes"][node]:
                    redirect_text = ""
                    for dialog in self.simplified_json["nodes"][node]["dialogs"]:
                        redirect_text += dialog
                redirect_texts[node] = redirect_text
        return redirect_texts



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

    def get_intents(self):
        project_id = self.get_project_id()
        hex_id = hex(int(project_id, 16) - 1)[2:]
        project_id = str(hex_id)
        VERSIONS_URL = "https://api.voiceflow.com/v2/versions/" + project_id
        versions = requests.get(VERSIONS_URL, headers=self.headers).json()
        intents = {}
        for key in versions["platformData"]["intents"]:
            intents[versions["intents"][key]["key"]] = versions["intents"][key]["name"]
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
        json_object = Simplified_Json(diagram_json, intents)
        simplified_json = json_object.simplify_json()
        return simplified_json

class VoiceflowFileToJson():
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

        json_object = Simplified_Json(diagram_json, intents)
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
