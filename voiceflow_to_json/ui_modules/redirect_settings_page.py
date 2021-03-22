from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QSizePolicy
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont

from voiceflow_to_json.settings_modifications.voiceflow_to_json import GetVoiceflowSettings
from voiceflow_to_json.settings_modifications.settings_to_dialplan import SettingsToDialplan
import voiceflow_to_json.constants.asterisk_filepath_constants as asterisk_constants

from voiceflow_to_json.ui_modules.shared_buttons import BackButton


class RedirectSettingsWidget(QWidget):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.settings = QSettings("redirect_settings", "GP_IVR_Settings")
        self.error = False

        self.setup_heading()

        self.voiceflow_settings = QSettings("simplified_voiceflow", "GP_IVR_Settings")
        self.redirect_numbers = {}
        self.setup_redirects_form()
        self.init_settings()

        self.setup_buttons()
        self.layout.addWidget(QLabel())
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def setup_buttons(self):
        self.button_layout = QHBoxLayout()

        if not self.page == "project":
            back_button_creator = BackButton()
            self.back_button = back_button_creator.create_back_button()
            self.button_layout.addWidget(self.back_button)
        else:
            self.button_layout.addWidget(QLabel())

        self.apply_settings_button = QPushButton("Apply")
        self.apply_settings_button.setToolTip("Update telephone numbers that users calling the IVR are redirected to")
        self.button_layout.addWidget(self.apply_settings_button)

    def setup_heading(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        rules_font = QFont('Arial', 10)
        rules_font.setItalic(True)

        self.layout.addWidget(QLabel())
        heading = QLabel("Redirect Phone Numbers:")
        heading.setFont(heading_font)
        self.layout.addWidget(heading)

        page_info = QLabel(
            "Here you can change the phone numbers that users are redirected\nto after reaching particular message end-points in the IVR.\nIf you don't want a user redirected, leave the value blank.")
        self.layout.addWidget(page_info)
        self.layout.addWidget(QLabel())

        uk_number_rules = QLabel("* UK Numbers Only")
        uk_number_rules.setFont(rules_font)
        self.layout.addWidget(uk_number_rules)
        no_extension_rule = QLabel("* Don't add Extension")
        no_extension_rule.setFont(rules_font)
        self.layout.addWidget(no_extension_rule)

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
        if redirect_texts == -1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error\n\nYou have not set up an IVR")
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        self.provider_number = QLineEdit()
        self.provider_number.setToolTip("Enter the telephone number users should call to access your IVR - you must own this number")
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
        redirect_number = QLineEdit()
        redirect_number.setToolTip("Enter a UK telephone number without extension")
        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QHBoxLayout()
        self.button_group.setLayout(self.v_box)
        self.v_box.addWidget(redirect_text)
        grow_label = QLabel()
        self.v_box.addWidget(grow_label)
        grow_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
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
            self.error = True
            return

        for node in self.redirect_numbers:
            node_ids.append(node)

            if not self.redirect_numbers[node].text().isnumeric():
                if not self.redirect_numbers[node].text():
                    phone_numbers.append("-1")
                    continue
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error\n\nPhone Number is Not in Correct Format")
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            phone_numbers.append(self.redirect_numbers[node].text())

        modify_dialplan = SettingsToDialplan(asterisk_constants.EXTENSIONS_CONF_PATH, node_ids, phone_numbers, self.provider_number.text())
        modify_dialplan.configure_dialplan()

    def save_settings(self):
        self.settings.clear()
        self.settings.setValue("provider number", self.provider_number.text())
        for node in self.redirect_numbers:
            self.settings.setValue(node, self.redirect_numbers[node].text())