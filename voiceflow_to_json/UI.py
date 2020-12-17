import sys
import json

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QErrorMessage
from PyQt5.QtWidgets import QComboBox

from voiceflow_to_json import Voiceflow_To_Json
from voiceflow_to_json import Get_Voiceflow_Information

class Project_Window(QDialog):

    def __init__(self, voiceflow_api, headers):
        super().__init__()
        self.setWindowTitle("Project Selection")
        self.dlgLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow('Choose Workspace and Project:', QLabel())
        self.workspace_combo_box = QComboBox(self)
        self.projects_combo_box = QComboBox(self)
        formLayout.addRow('Workspace:', self.workspace_combo_box)
        formLayout.addRow('Projects:', self.projects_combo_box)
        self.dlgLayout.addLayout(formLayout)
        self.voiceflow_api = voiceflow_api
        self.headers = headers
        self.workspaces = self.voiceflow_api.get_workspaces(headers)
        self.projects = []
        self.project_names = []
        self.workspace_name = ""
        self.project_name = ""
        workspace_names = self.voiceflow_api.get_workspace_names(self.workspaces)
        self.workspace_combo_box.addItem("Select")
        self.workspace_combo_box.addItems(workspace_names)
        self.workspace_combo_box.currentTextChanged.connect(self.on_workspace_changed)
        self.projects_combo_box.currentTextChanged.connect(self.on_project_changed)
        self.dlgLayout.addWidget(self.workspace_combo_box)
        get_json_button = QPushButton('Get Config', self)
        get_json_button.clicked.connect(self.get_json)
        self.dlgLayout.addWidget(get_json_button)
        self.setLayout(self.dlgLayout)

    def get_json(self):
        voiceflow_json = Voiceflow_To_Json(self.workspace_name, self.project_name, self.headers)
        simplified_json = voiceflow_json.simplified_json()
        with open('/home/max/Documents/GP_IVR/voiceflow.json', 'w') as fp:
             json.dump(simplified_json, fp)
        self.close()

    def on_project_changed(self, value):
        self.project_name = value

    def on_workspace_changed(self, value):
        self.workspace_name = value
        workspace_id = self.voiceflow_api.get_workspace_id(value, self.workspaces)
        self.projects = self.voiceflow_api.get_projects(self.headers, workspace_id)
        project_names = self.voiceflow_api.get_project_names(self.projects)
        self.projects_combo_box.clear()
        self.projects_combo_box.addItem("Select")
        self.projects_combo_box.addItems(project_names)

class Login_Window(QDialog):

    """Dialog."""

    def __init__(self):
        """Initializer."""
        super().__init__()
        self.setWindowTitle('Voiceflow Login')
        self.dlgLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow('Voiceflow Credentials:', QLabel())
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        formLayout.addRow('Email:', self.email)
        formLayout.addRow('Password:', self.password)
        self.dlgLayout.addLayout(formLayout)

        login_button = QPushButton('Login', self)
        login_button.clicked.connect(self.project_window)
        self.dlgLayout.addWidget(login_button)
        self.setLayout(self.dlgLayout)

    def project_window(self):
        voiceflow_api = Get_Voiceflow_Information(email=self.email.text(), password=self.password.text())
        auth_token = voiceflow_api.get_auth_header()
        if auth_token == "None":
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Voiceflow Credentials are Incorrect')
            self.dlgLayout.addWidget(error_dialog)
            self.setLayout(self.dlgLayout)
        else:
            self.w = Project_Window(voiceflow_api, auth_token)
            self.w.show()
            self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = Login_Window()
    dlg.show()
    sys.exit(app.exec_())

