from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QButtonGroup, QLineEdit, QSizePolicy
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QFont

from voiceflow_to_json.settings_modifications.settings_to_pjsip import SettingsToPjsip
import voiceflow_to_json.constants.asterisk_filepath_constants as asterisk_constants

from voiceflow_to_json.ui_modules.shared_buttons import BackButton


class PstnSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.setup_heading()

        self.button_group = QGroupBox("Mandatory Fields are Marked with *")
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.setup_pstn_settings_form()
        self.v_box.addLayout(self.form_layout)

        self.setup_ip_form()
        self.v_box.addLayout(self.ip_form_layout)

        self.init_settings()

        self.setup_buttons()
        self.v_box.addWidget(QLabel())
        self.v_box.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def setup_buttons(self):
        self.button_layout = QHBoxLayout()

        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()
        self.button_layout.addWidget(self.back_button)

        self.add_ip_address_button = QPushButton("Add IP Address", self)
        self.add_ip_address_button.setToolTip("Add another contact IP address")
        self.button_layout.addWidget(self.add_ip_address_button)

        self.apply_settings_button = QPushButton("Apply")
        self.apply_settings_button.setToolTip(
            "Update Sip Trunk settings for contact between your IVR and telephone provider")
        self.button_layout.addWidget(self.apply_settings_button)

    def setup_ip_form(self):
        self.ip_form_layout = QFormLayout()
        self.ip_addresses = []
        self.delete_button_group = QButtonGroup(self)
        self.delete_layouts = []
        self.settings = QSettings("gp_ivr_settings", "GP_IVR_Settings")

    def setup_pstn_settings_form(self):
        self.form_layout.addRow("", QLabel())

        self.pjsip_port = QLineEdit()
        self.pjsip_port.setToolTip("The port that your telephone provider will connect to the IVR with")
        self.provider_address = QLineEdit()
        self.provider_address.setToolTip("The SIP address that the IVR can contact the telephone provider through")
        self.provider_port = QLineEdit()
        self.provider_port.setToolTip("The port through which the telephone provider uses in communications")

        self.form_layout.addRow("Asterisk PJSIP Port (default is 5160):", self.pjsip_port)
        self.form_layout.addRow("*Provider Contact Address:", self.provider_address)
        self.form_layout.addRow("Provider Contact Port:", self.provider_port)
        grow_label = QLabel()
        self.form_layout.addRow("Provider Contact IP Addresses:", grow_label)
        grow_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def setup_heading(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("SIP Trunk Settings:")
        heading.setFont(heading_font)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)

        page_info = QLabel(
            "You can change your telephone service provider SIP trunk settings here.\nThese settings must be updated from the default before running an IVR.\nMake sure that you have created a SIP trunk with your telephone provider.")
        self.layout.addWidget(page_info)
        self.layout.addWidget(QLabel())

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
        delete_ip_address_button.setToolTip("Remove this contact IP address")
        new_ip_address = QLineEdit()
        new_ip_address.setToolTip("IP address that the telephone provider will contact the IVR with")
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
        create_pjsip = SettingsToPjsip(asterisk_constants.PJSIP_CONF_PATH, pjsip_port_text, self.provider_address.text(), provider_port_text, ip_addresses)
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