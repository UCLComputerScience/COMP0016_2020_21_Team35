import sys

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon

from voiceflow_to_json import Get_Voiceflow_Information, Voiceflow_To_Json, VoiceflowFileToJson
from json_to_dialplan.json_to_dialplan import Dialplan


class ProjectWindow(QDialog):

    def __init__(self, voiceflow_api, headers):
        super().__init__()
        self.voiceflow_api = voiceflow_api
        self.headers = headers
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.form_layout.addRow('Choose Workspace and Project:', QLabel())
        self.workspace_combo_box = QComboBox(self)
        self.projects_combo_box = QComboBox(self)
        self.set_projects()
        self.set_workspaces()
        self.form_layout.addRow('Workspace:', self.workspace_combo_box)
        self.form_layout.addRow('Projects:', self.projects_combo_box)

        self.layout.addLayout(self.form_layout)

        self.workspace_combo_box.addItem("Select")
        self.workspace_combo_box.addItems(self.workspace_names)

        self.layout.addWidget(self.workspace_combo_box)
        self.create_ivr_button = QPushButton('Get Config', self)

        self.layout.addWidget(self.create_ivr_button)
        self.setLayout(self.layout)

    def set_projects(self):
        self.projects = []
        self.project_names = []
        self.project_name = ""

    def set_workspaces(self):
        self.workspaces = self.voiceflow_api.get_workspaces(self.headers)
        self.workspace_name = ""
        self.workspace_names = self.voiceflow_api.get_workspace_names(self.workspaces)

    def create_ivr(self):
        voiceflow_json = Voiceflow_To_Json(self.workspace_name, self.project_name, self.headers)
        simplified_json = voiceflow_json.simplified_json()
        create_ivr = Dialplan("/etc/asterisk/extensions.conf", simplified_json)
        create_ivr.create_config()
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

class FileEdit(QLineEdit):
    def __init__(self, parent):
        super(FileEdit, self).__init__(parent)

        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            filepath = str(urls[0].path())[1:]
            # Only accept voiceflow files
            if filepath[-3:].lower() == ".vf":
                self.setText(filepath)
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle("Error: Invalid File")
                dialog.setText("Only .vf files are accepted")
                dialog.setIcon(QMessageBox.Warning)
                dialog.exec_()

class ChooseVoiceflowFileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.browse_button = QPushButton("Browse", self)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(QLabel("Or Drag and Drop File:"))
        self.file_edit = FileEdit(self)
        self.layout.addWidget(self.file_edit)
        self.create_ivr_button = QPushButton("Create IVR", self)
        self.layout.addWidget(self.create_ivr_button)
        self.setLayout(self.layout)

    def get_files(self):
        filepath = QFileDialog.getOpenFileName(self, 'Single File', "~", '*.vf')
        self.file_edit.setText(filepath[0])

    def create_ivr(self):
        print(self.file_edit.text())
        voiceflow_json = VoiceflowFileToJson(self.file_edit.text())
        simplified_json = voiceflow_json.simplified_json()
        create_ivr = Dialplan("/etc/asterisk/extensions.conf", simplified_json)
        create_ivr.create_config()
        self.close()


class LoginWidget(QWidget):

    """Dialog."""

    def __init__(self):
        """Initializer."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.form_layout.addRow('Voiceflow Credentials:', QLabel())
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow('Email:', self.email)
        self.form_layout.addRow('Password:', self.password)
        self.layout.addLayout(self.form_layout)

        self.login_button = QPushButton('Login', self)
        self.layout.addWidget(self.login_button)
        self.setLayout(self.layout)


    def project_window(self):
        self.voiceflow_api = Get_Voiceflow_Information(email=self.email.text(), password=self.password.text())
        self.auth_token = self.voiceflow_api.get_auth_header()
        if self.auth_token == "None":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error\n\nVoiceflow Credentials were Incorrect")
            msg.setWindowTitle("Error")
            msg.exec_()
            return False
        else:
            return True


class IvrGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Options:"))
        self.voiceflow_to_json_button = QPushButton('Use Voiceflow Login', self)
        self.json_file_button = QPushButton('Use Downloaded Voiceflow File', self)
        self.layout.addWidget(self.voiceflow_to_json_button)
        self.layout.addWidget(self.json_file_button)
        self.setLayout(self.layout)

class ProgramUi(QMainWindow):
    """PyCalc's View (GUI)."""
    def __init__(self):
        """View initializer."""
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GP IVR")
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        login_action = QAction("Generate IVR", self)
        login_action.triggered.connect(lambda: self.ivr_generator_setup())


        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Menu')
        fileMenu.addAction(exitAct)
        fileMenu.addAction(login_action)

        self.setGeometry(300, 300, 300, 200)

    def ivr_generator_setup(self):
        self.ivr_generator = IvrGeneratorWidget()
        self.setCentralWidget(self.ivr_generator)
        self.setWindowTitle("IVR Generation")
        self.ivr_generator_events()

    def login_setup(self):
        self.login = LoginWidget()
        self.setCentralWidget(self.login)
        self.setWindowTitle("Login")
        self.login_events()

    def choose_voiceflow_file_setup(self):
        self.choose_voiceflow_file = ChooseVoiceflowFileWidget()
        self.setCentralWidget(self.choose_voiceflow_file)
        self.setWindowTitle("Choose Voiceflow File")
        self.choose_voiceflow_file_events()

    def project_setup(self):
        if(self.login.project_window()):
            self.project = ProjectWindow(self.login.voiceflow_api, self.login.auth_token)
            self.setCentralWidget(self.project)
            self.setWindowTitle("Project Selection")
            self.project_events()

    def choose_voiceflow_file_events(self):
        self.choose_voiceflow_file.browse_button.clicked.connect(lambda: self.choose_voiceflow_file.get_files())
        self.choose_voiceflow_file.create_ivr_button.clicked.connect(lambda: self.choose_voiceflow_file.create_ivr())


    def ivr_generator_events(self):
        self.ivr_generator.voiceflow_to_json_button.clicked.connect(lambda: self.login_setup())
        self.ivr_generator.json_file_button.clicked.connect(lambda: self.choose_voiceflow_file_setup())

    def login_events(self):
        self.login.login_button.clicked.connect(lambda: self.project_setup())

    def project_events(self):
        self.project.workspace_combo_box.currentTextChanged.connect(lambda: self.project.on_workspace_changed(self.project.workspace_combo_box.currentText()))
        self.project.projects_combo_box.currentTextChanged.connect(lambda: self.project.on_project_changed(self.project.projects_combo_box.currentText()))
        self.project.create_ivr_button.clicked.connect(lambda: self.project.create_ivr())




def main():
    """Main function."""
    app = QApplication(sys.argv)
    view = ProgramUi()
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
