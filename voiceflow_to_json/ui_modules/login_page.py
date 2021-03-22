from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QSizePolicy
from PyQt5.QtGui import QFont

from voiceflow_to_json.settings_modifications.voiceflow_to_json import Get_Voiceflow_Information

from voiceflow_to_json.ui_modules.shared_buttons import BackButton


class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.setup_header()

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.setup_login_form()

        self.setup_buttons()

        self.v_box.addLayout(self.login_layout)

        self.layout.addLayout(self.v_box)
        self.setLayout(self.layout)

    def setup_buttons(self):
        self.login_layout = QHBoxLayout()
        self.login_button = QPushButton('Login', self)
        self.login_button.setToolTip("Log in to Voiceflow and display projects to choose from")

        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()

        self.login_layout.addWidget(self.back_button)
        self.login_layout.addWidget(self.login_button)

    def setup_login_form(self):
        self.form_layout = QFormLayout()

        self.email_layout = QHBoxLayout()
        self.email = QLineEdit()
        self.email_layout.addWidget(QLabel())
        self.email_layout.addWidget(self.email)
        self.email.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.email.setToolTip("Enter your Voiceflow email")

        self.password_layout = QHBoxLayout()
        self.password = QLineEdit()
        self.password_layout.addWidget(QLabel())
        self.password_layout.addWidget(self.password)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.password.setToolTip("Enter your Voiceflow password")

        self.form_layout.addRow('', QLabel())
        self.form_layout.addRow('Email:', self.email_layout)
        self.form_layout.addRow('Password:', self.password_layout)
        self.form_layout.addRow('', QLabel())
        self.v_box.addLayout(self.form_layout)

    def setup_header(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("Voiceflow Credentials:")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)

        page_info = QLabel(
            "Enter your Voiceflow username and password.\nYou can then use a Voiceflow project to generate an IVR")

        self.layout.addWidget(page_info)
        self.layout.addWidget(QLabel())


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