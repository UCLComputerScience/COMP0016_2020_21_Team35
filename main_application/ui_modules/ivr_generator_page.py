import os
import sys

from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QFont

import main_application.constants.image_filepath_constants as image_constants

from main_application.ui_modules.shared_buttons import BackButton


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)


class IvrGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.setup_heading()

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.setup_voiceflow_login_button()
        self.setup_downloaded_voiceflow_button()

        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()
        back_layout = back_button_creator.create_back_layout(self.back_button)

        self.v_box.addWidget(self.voiceflow_to_json_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.json_file_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addLayout(back_layout)

        self.setLayout(self.layout)

    def setup_downloaded_voiceflow_button(self):
        self.json_file_button = QPushButton('Use Downloaded Voiceflow File', self)
        self.json_file_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        file_icon = QIcon(os.path.join(application_path, image_constants.FILE_ICON))
        self.json_file_button.setIcon(file_icon)
        self.json_file_button.setIconSize(QSize(64, 64))
        self.json_file_button.setToolTip("Use This To: Upload a Voiceflow file to turn into and IVR")

    def setup_voiceflow_login_button(self):
        self.voiceflow_to_json_button = QPushButton('Use Voiceflow Login', self)
        self.voiceflow_to_json_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        login_icon = QIcon(os.path.join(application_path, image_constants.LOGIN_ICON))
        self.voiceflow_to_json_button.setIcon(login_icon)
        self.voiceflow_to_json_button.setIconSize(QSize(64, 64))
        self.voiceflow_to_json_button.setToolTip(
            "Use This To: Login to Voiceflow and choose a project to turn into an IVR")

    def setup_heading(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("Generate an IVR:")
        heading.setFont(heading_font)

        page_info1 = QLabel(
            "Our IVR Generator allows you to either use your Voiceflow credentials \nor a downloaded Voiceflow file to generate an IVR.")
        page_info2 = QLabel("Speech files are automatically generated but can be added individually.")

        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)
        self.layout.addWidget(page_info1)
        self.layout.addWidget(page_info2)
        self.layout.addWidget(QLabel())