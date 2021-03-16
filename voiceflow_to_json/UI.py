import sys

from PyQt5.QtWidgets import QDialog, QGroupBox, QMainWindow, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QComboBox, QWidget, QApplication, QAction, qApp, QButtonGroup, QFileDialog, QMessageBox, QLineEdit, QSizePolicy
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon, QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


from voiceflow_to_json import Get_Voiceflow_Information, Voiceflow_To_Json, VoiceflowFileToJson, GetVoiceflowSettings
from json_to_dialplan.json_to_dialplan import Dialplan
from settings_to_pjsip import SettingsToPjsip
from settings_to_dialplan import SettingsToDialplan
from extract_data import return_daily_data, return_weekly_data


class ProjectWindow(QDialog):

    def __init__(self, voiceflow_api, headers):
        super().__init__()
        self.voiceflow_api = voiceflow_api
        self.headers = headers
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("Choose Workspace and Project:")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.workspace_combo_box = QComboBox(self)
        self.projects_combo_box = QComboBox(self)
        self.set_projects()
        self.set_workspaces()
        self.form_layout.addRow('', QLabel())
        self.form_layout.addRow('Workspace:', self.workspace_combo_box)
        self.form_layout.addRow('', QLabel())
        self.form_layout.addRow('Projects:', self.projects_combo_box)
        self.form_layout.addRow('', QLabel())

        self.v_box.addLayout(self.form_layout)

        self.workspace_combo_box.addItem("Select")
        self.workspace_combo_box.addItems(self.workspace_names)

        self.create_ivr_button_layout = QHBoxLayout()
        self.create_ivr_button_layout.addWidget(QLabel())
        self.create_ivr_button = QPushButton('Get Config', self)
        self.create_ivr_button_layout.addWidget(self.create_ivr_button)

        self.settings = QSettings("simplified_voiceflow", "GP_IVR_Settings")

        self.v_box.addLayout(self.create_ivr_button_layout)
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
        self.settings.setValue("simplified json", simplified_json)
        create_ivr = Dialplan("asterisk_docker/conf/asterisk-build/extensions.conf", simplified_json)
        create_ivr.create_config()

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
        self.settings = QSettings("simplified_voiceflow", "GP_IVR_Settings")

        self.button_group = QGroupBox("Drag and Drop File:")
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.file_edit = FileEdit(self)
        self.v_box.addWidget(self.file_edit)
        self.v_box.addWidget(QLabel())

        self.button_layout = QHBoxLayout()
        self.create_ivr_button = QPushButton("Create IVR", self)
        self.browse_button = QPushButton("Browse", self)
        self.button_layout.addWidget(self.browse_button)
        self.button_layout.addWidget(self.create_ivr_button)
        self.v_box.addLayout(self.button_layout)

        self.layout.addLayout(self.v_box)

        self.setLayout(self.layout)

    def get_files(self):
        filepath = QFileDialog.getOpenFileName(self, 'Single File', "~", '*.vf')
        self.file_edit.setText(filepath[0])

    def create_ivr(self):
        voiceflow_json = VoiceflowFileToJson(self.file_edit.text())
        simplified_json = voiceflow_json.simplified_json()
        self.settings.setValue("simplified json", simplified_json)
        create_ivr = Dialplan("asterisk_docker/conf/asterisk-build/extensions.conf", simplified_json)
        create_ivr.create_config()


class LoginWidget(QWidget):

    """Dialog."""

    def __init__(self):
        """Initializer."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("Voiceflow Credentials:")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.form_layout = QFormLayout()

        self.email_layout = QHBoxLayout()
        self.email = QLineEdit()
        self.email_layout.addWidget(QLabel())
        self.email_layout.addWidget(self.email)
        self.email.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.password_layout = QHBoxLayout()
        self.password = QLineEdit()
        self.password_layout.addWidget(QLabel())
        self.password_layout.addWidget(self.password)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.form_layout.addRow('', QLabel())
        self.form_layout.addRow('Email:', self.email_layout)
        self.form_layout.addRow('Password:', self.password_layout)
        self.form_layout.addRow('', QLabel())
        self.v_box.addLayout(self.form_layout)

        self.login_layout = QHBoxLayout()
        self.login_layout.addWidget(QLabel())
        self.login_button = QPushButton('Login', self)
        self.login_layout.addWidget(self.login_button)
        self.v_box.addLayout(self.login_layout)

        self.layout.addLayout(self.v_box)
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

        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("Options:")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)
        
        self.voiceflow_to_json_button = QPushButton('Use Voiceflow Login', self)
        self.voiceflow_to_json_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.json_file_button = QPushButton('Use Downloaded Voiceflow File', self)
        self.json_file_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)


        self.v_box.addWidget(self.voiceflow_to_json_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.json_file_button)
        self.setLayout(self.layout)

class HomePageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        heading_font = QFont('Arial', 14)
        heading_font.setBold(True)

        heading = QLabel("GP IVR")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading, alignment=Qt.AlignCenter)
        self.layout.addWidget(QLabel())

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.generate_ivr_button = QPushButton('Generate IVR', self)
        self.generate_ivr_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.pstn_settings_button = QPushButton('PSTN Settings', self)
        self.pstn_settings_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.redirect_settings_button = QPushButton('Redirect Settings', self)
        self.redirect_settings_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stats_button = QPushButton('Statistics', self)
        self.stats_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)


        self.v_box.addWidget(self.generate_ivr_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.stats_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.pstn_settings_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.redirect_settings_button)
        self.setLayout(self.layout)

class RedirectSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.settings = QSettings("redirect_settings", "GP_IVR_Settings")

        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        rules_font = QFont('Arial', 10)
        rules_font.setItalic(True)

        self.layout.addWidget(QLabel())
        heading = QLabel("Redirect Phone Numbers:")
        heading.setFont(heading_font)
        self.layout.addWidget(heading)
        uk_number_rules = QLabel("* UK Numbers Only")
        uk_number_rules.setFont(rules_font)
        self.layout.addWidget(uk_number_rules)
        no_extension_rule = QLabel("* Don't add Extension")
        no_extension_rule.setFont(rules_font)
        self.layout.addWidget(no_extension_rule)

        self.voiceflow_settings = QSettings("simplified_voiceflow", "GP_IVR_Settings")
        self.redirect_numbers = {}
        self.setup_redirects_form()
        self.init_settings()

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(QLabel())
        self.button_layout.addWidget(QLabel())

        self.apply_settings_button = QPushButton("Apply")
        self.button_layout.addWidget(self.apply_settings_button)

        self.layout.addWidget(QLabel())
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def init_settings(self):
        provider_number = self.settings.value("provider number")
        if provider_number:
            self.provider_number.setText(provider_number)
        for node in self.redirect_numbers:
            node_value = self.settings.value(node)
            if node_value:
                self.redirect_numbers[node].setText(node_value)

    def setup_redirects_form(self):
        voiceflow_settings = GetVoiceflowSettings(self.voiceflow_settings.value("simplified json"))
        redirect_texts = voiceflow_settings.get_redirect_texts()
        self.provider_number = QLineEdit()
        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QHBoxLayout()
        self.button_group.setLayout(self.v_box)
        self.v_box.addWidget(QLabel("Provider Telephone Number:"))
        self.v_box.addWidget(self.provider_number, alignment=Qt.AlignRight)
        for node in redirect_texts:
            self.add_redirects(redirect_texts[node], node)

    def add_redirects(self, redirect_text, redirect_node):
        redirect_text = QLabel(redirect_text)
        redirect_text.setWordWrap(True)
        redirect_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        redirect_number = QLineEdit()
        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QHBoxLayout()
        self.button_group.setLayout(self.v_box)
        self.v_box.addWidget(redirect_text)
        self.v_box.addWidget(redirect_number, alignment=Qt.AlignRight)
        self.redirect_numbers[redirect_node] = redirect_number

    def apply_settings(self):
        self.save_settings()
        phone_numbers = []
        node_ids = []

        if not self.provider_number.text().isnumeric():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error\n\nProvider Number is Not in Correct Format")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        for node in self.redirect_numbers:
            node_ids.append(node)

            if not self.redirect_numbers[node].text().isnumeric():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error\n\nPhone Number is Not in Correct Format")
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            phone_numbers.append(self.redirect_numbers[node].text())

        modify_dialplan = SettingsToDialplan("asterisk_docker/conf/asterisk-build/extensions.conf", node_ids, phone_numbers, self.provider_number.text())
        modify_dialplan.configure_dialplan()

    def save_settings(self):
        self.settings.setValue("provider number", self.provider_number.text())
        for node in self.redirect_numbers:
            self.settings.setValue(node, self.redirect_numbers[node].text())

class PstnSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("PSTN Settings:")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.form_layout.addRow("", QLabel())
        self.form_layout.addRow("Mandatory Fields are Marked with *", QLabel())
        self.pjsip_port = QLineEdit()
        self.provider_address = QLineEdit()
        self.provider_port = QLineEdit()
        self.form_layout.addRow("Asterisk PJSIP Port (default is 5160):", self.pjsip_port)
        self.form_layout.addRow("*Provider Contact Address:", self.provider_address)
        self.form_layout.addRow("Provider Contact Port:", self.provider_port)
        self.form_layout.addRow("Provider Contact IP Addresses:", QLabel())
        self.v_box.addLayout(self.form_layout)

        self.ip_form_layout = QFormLayout()
        self.ip_addresses = []
        self.delete_button_group = QButtonGroup(self)
        self.delete_layouts = []
        self.settings = QSettings("gp_ivr_settings", "GP_IVR_Settings")
        self.v_box.addLayout(self.ip_form_layout)

        self.init_settings()

        self.button_layout = QHBoxLayout()

        self.add_ip_address_button = QPushButton("Add IP Address", self)
        self.button_layout.addWidget(self.add_ip_address_button)

        self.apply_settings_button = QPushButton("Apply")
        self.button_layout.addWidget(self.apply_settings_button)

        self.v_box.addWidget(QLabel())
        self.v_box.addLayout(self.button_layout)

        self.layout.addLayout(self.v_box)

        self.setLayout(self.layout)

    def init_settings(self):
        self.pjsip_port.setText(self.settings.value("pjsip port"))
        self.provider_address.setText(self.settings.value("provider contact address"))
        self.provider_port.setText(self.settings.value("provider contact port"))
        saved_ip_addresses = self.settings.value("provider ip addresses")

        if saved_ip_addresses is not None:
            new_ip_addresses = list(saved_ip_addresses.split(","))
            del new_ip_addresses[-1]
            for ip_address in new_ip_addresses:
                self.add_ip_address(value=ip_address)

    def add_ip_address(self, value=None):
        layout = QHBoxLayout()
        delete_ip_address_button = QPushButton("Delete", self)
        new_ip_address = QLineEdit()
        layout.addWidget(new_ip_address)
        layout.addWidget(delete_ip_address_button)
        if value is not None:
            new_ip_address.setText(value)
        self.ip_form_layout.addRow("IP Address " + str(len(self.ip_addresses)), layout)
        self.ip_addresses.append(new_ip_address)
        self.delete_button_group.addButton(delete_ip_address_button)

    def apply_settings(self):
        self.save_settings()
        ip_addresses = []

        if not self.pjsip_port.text():
            pjsip_port_text = "5160"
        else:
            pjsip_port_text = self.pjsip_port.text()

        if not self.provider_port.text():
            provider_port_text = "5060"
        else:
            provider_port_text = self.provider_port.text()

        for ip_address in self.ip_addresses:
            ip_addresses.append(ip_address.text())
        create_pjsip = SettingsToPjsip("asterisk_docker/conf/asterisk-build/pjsip.conf", pjsip_port_text, self.provider_address.text(), provider_port_text, ip_addresses)
        create_pjsip.create_config()

    def save_settings(self):
        self.settings.setValue("pjsip port", self.pjsip_port.text())
        self.settings.setValue("provider contact address", self.provider_address.text())
        self.settings.setValue("provider contact port", self.provider_port.text())
        ip_address_list = ""
        for ip_address in self.ip_addresses:
            ip_address_list += ip_address.text() + ","
        if ip_address_list is not None:
            self.settings.setValue("provider ip addresses", ip_address_list)

    def delete_ip_address(self, button):
        ip_index = - 2 - self.delete_button_group.id(button)
        self.ip_form_layout.removeRow(ip_index)
        del self.ip_addresses[ip_index]
        for button in self.delete_button_group.buttons():
            button_id = self.delete_button_group.id(button)
            if(button_id < - 2 - ip_index):
                self.delete_button_group.setId(button, button_id + 1)

class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.button1 = QPushButton('DAILY')
        self.button2 = QPushButton('WEEKLY')
        self.plot1()

        self.button1.clicked.connect(self.plot1)
        self.button2.clicked.connect(self.plot2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self.button1)
        sublayout.addWidget(self.button2)

        main_layout.addLayout(sublayout)

        self.setLayout(main_layout)

    def plot1(self):
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        self.figure.clear()

        ax = self.figure.add_subplot()

        dates, outcomes = return_daily_data(10)

        x = np.arange(len(dates))
        width = 0.2

        rects1 = ax.bar(x - 3 * width / 2, outcomes[0], width, label='Answered')
        rects2 = ax.bar(x - width / 2, outcomes[1], width, label='No Answer')
        rects3 = ax.bar(x + width / 2, outcomes[2], width, label='Busy')
        rects4 = ax.bar(x + 3 * width / 2, outcomes[3], width, label='Failed')

        ax.set_ylabel('Number of Calls')
        ax.set_title('Calls Outcome')
        ax.set_xticks(x)
        ax.set_xticklabels(dates[:10])
        ax.xaxis_date()
        ax.legend()

        self.figure.autofmt_xdate()

        self.figure.tight_layout()

        plt.grid(linestyle='--', linewidth=0.3)

        self.canvas.draw()

    def plot2(self):
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

        self.figure.clear()

        ax = self.figure.add_subplot()

        dates, outcomes = return_weekly_data(6)

        x = np.arange(len(dates))
        width = 0.2

        rects1 = ax.bar(x - 3 * width / 2, outcomes[0], width, label='Answered')
        rects2 = ax.bar(x - width / 2, outcomes[1], width, label='No Answer')
        rects3 = ax.bar(x + width / 2, outcomes[2], width, label='Busy')
        rects4 = ax.bar(x + 3 * width / 2, outcomes[3], width, label='Failed')

        ax.set_ylabel('Number of Calls')
        ax.set_title('Calls Outcome')
        ax.set_xticks(x)
        ax.set_xticklabels(dates[:10])
        ax.xaxis_date()
        ax.legend()

        self.figure.autofmt_xdate()

        self.figure.tight_layout()

        plt.grid(linestyle='--', linewidth=0.3)

        self.canvas.draw()


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

        home_page_action = QAction("Home Page", self)
        home_page_action.triggered.connect(lambda: self.home_page_setup())

        login_action = QAction("Generate IVR", self)
        login_action.triggered.connect(lambda: self.ivr_generator_setup())

        pstn_settings_action = QAction("PSTN Settings", self)
        pstn_settings_action.triggered.connect(lambda: self.pstn_settings_setup())

        redirect_settings_action = QAction("Redirect Settings", self)
        redirect_settings_action.triggered.connect(lambda: self.redirect_settings_setup())

        stats_action = QAction("Statistics", self)
        stats_action.triggered.connect(lambda:self.stats_setup())


        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Menu')
        fileMenu.addAction(home_page_action)
        fileMenu.addAction(login_action)
        fileMenu.addAction(stats_action)
        fileMenu.addAction(pstn_settings_action)
        fileMenu.addAction(redirect_settings_action)
        fileMenu.addAction(exitAct)

        self.setGeometry(300, 300, 300, 200)
        self.home_page_setup()

    def home_page_setup(self):
        self.resize(400, 550)
        self.home_page = HomePageWidget()
        self.setCentralWidget(self.home_page)
        self.setWindowTitle("Home")
        self.home_page_events()

    def ivr_generator_setup(self):
        self.resize(400, 200)
        self.ivr_generator = IvrGeneratorWidget()
        self.setCentralWidget(self.ivr_generator)
        self.setWindowTitle("IVR Generation")
        self.ivr_generator_events()

    def stats_setup(self):
        self.resize(800, 500)
        self.stats = StatsWidget()
        self.setCentralWidget(self.stats)
        self.setWindowTitle("Stats")

    def pstn_settings_setup(self):
        self.resize(550, 400)
        self.pstn_settings = PstnSettingsWidget()
        self.setCentralWidget(self.pstn_settings)
        self.setWindowTitle("PSTN Settings")
        self.pstn_settings_events()

    def redirect_settings_setup(self):
        self.resize(500, 400)
        self.redirect_settings = RedirectSettingsWidget()
        self.setCentralWidget(self.redirect_settings)
        self.setWindowTitle("Redirect Settings")
        self.redirect_settings_events()

    def login_setup(self):
        self.resize(400, 150)
        self.login = LoginWidget()
        self.setCentralWidget(self.login)
        self.setWindowTitle("Login")
        self.login_events()

    def choose_voiceflow_file_setup(self):
        self.resize(500, 200)
        self.choose_voiceflow_file = ChooseVoiceflowFileWidget()
        self.setCentralWidget(self.choose_voiceflow_file)
        self.setWindowTitle("Choose Voiceflow File")
        self.choose_voiceflow_file_events()

    def project_setup(self):
        self.resize(400, 150)
        if(self.login.project_window()):
            self.project = ProjectWindow(self.login.voiceflow_api, self.login.auth_token)
            self.setCentralWidget(self.project)
            self.setWindowTitle("Project Selection")
            self.project_events()

    def choose_voiceflow_file_events(self):
        self.choose_voiceflow_file.browse_button.clicked.connect(lambda: self.choose_voiceflow_file.get_files())
        self.choose_voiceflow_file.create_ivr_button.clicked.connect(lambda: self.choose_voiceflow_file.create_ivr())
        self.choose_voiceflow_file.create_ivr_button.clicked.connect(lambda: self.redirect_settings_setup())

    def home_page_events(self):
        self.home_page.generate_ivr_button.clicked.connect(lambda: self.ivr_generator_setup())
        self.home_page.pstn_settings_button.clicked.connect(lambda: self.pstn_settings_setup())
        self.home_page.redirect_settings_button.clicked.connect(lambda: self.redirect_settings_setup())
        self.home_page.stats_button.clicked.connect(lambda: self.stats_setup())

    def ivr_generator_events(self):
        self.ivr_generator.voiceflow_to_json_button.clicked.connect(lambda: self.login_setup())
        self.ivr_generator.json_file_button.clicked.connect(lambda: self.choose_voiceflow_file_setup())

    def pstn_settings_events(self):
        self.pstn_settings.add_ip_address_button.clicked.connect(lambda: self.pstn_settings.add_ip_address())
        self.pstn_settings.apply_settings_button.clicked.connect(lambda: self.pstn_settings.apply_settings())
        self.pstn_settings.delete_button_group.buttonClicked.connect(self.pstn_settings.delete_ip_address)
        self.pstn_settings.apply_settings_button.clicked.connect(lambda: self.home_page_setup())

    def redirect_settings_events(self):
        self.redirect_settings.apply_settings_button.clicked.connect(lambda: self.redirect_settings.apply_settings())
        self.redirect_settings.apply_settings_button.clicked.connect(lambda: self.home_page_setup())

    def login_events(self):
        self.login.login_button.clicked.connect(lambda: self.project_setup())

    def project_events(self):
        self.project.workspace_combo_box.currentTextChanged.connect(lambda: self.project.on_workspace_changed(self.project.workspace_combo_box.currentText()))
        self.project.projects_combo_box.currentTextChanged.connect(lambda: self.project.on_project_changed(self.project.projects_combo_box.currentText()))
        self.project.create_ivr_button.clicked.connect(lambda: self.project.create_ivr())
        self.project.create_ivr_button.clicked.connect(lambda: self.redirect_settings_setup())




def main():
    """Main function."""
    app = QApplication(sys.argv)
    view = ProgramUi()
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
