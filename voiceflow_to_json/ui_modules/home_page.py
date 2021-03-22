import os
import sys

from PyQt5.QtWidgets import QDialog, QGroupBox, QMainWindow, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProxyStyle, QStyle
from PyQt5.QtWidgets import QComboBox, QWidget, QApplication, QAction, qApp, QButtonGroup, QFileDialog, QMessageBox, QLineEdit, QSizePolicy, QScrollArea, QDateEdit
from PyQt5.QtCore import QSettings, Qt, QSize, QRect, QPoint, QDateTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

import voiceflow_to_json.constants.image_filepath_constants as image_constants


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)


class HomePageWidget(QWidget):
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

        self.setup_ivr_status_button()
        self.setup_generate_ivr_button()
        self.setup_analytics_button()
        self.setup_pstn_settings_button()
        self.setup_redirect_settings_button()

        self.v_box.addWidget(self.ivr_status_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.generate_ivr_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.stats_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.pstn_settings_button)
        self.v_box.addWidget(QLabel())
        self.v_box.addWidget(self.redirect_settings_button)
        self.setLayout(self.layout)

    def setup_redirect_settings_button(self):
        self.redirect_settings_button = QPushButton('Redirect Settings', self)
        self.redirect_settings_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        redirect_settings_icon = QIcon(os.path.join(application_path, image_constants.REDIRECT_SETTINGS_ICON))
        self.redirect_settings_button.setIcon(redirect_settings_icon)
        self.redirect_settings_button.setIconSize(QSize(64, 64))
        self.redirect_settings_button.setToolTip(
            "Use This To: Update the numbers that users calling the IVR are redirected to")

    def setup_pstn_settings_button(self):
        self.pstn_settings_button = QPushButton('SIP Trunk Settings', self)
        self.pstn_settings_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        pstn_settings_icon = QIcon(os.path.join(application_path, image_constants.PSTN_SETTINGS_ICON))
        self.pstn_settings_button.setIcon(pstn_settings_icon)
        self.pstn_settings_button.setIconSize(QSize(64, 64))
        self.pstn_settings_button.setToolTip(
            "Use This To: Update your PSTN provider settings for your IVR (e.g. Twilio)")

    def setup_analytics_button(self):
        self.stats_button = QPushButton('Analytics', self)
        self.stats_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        analytics_icon = QIcon(os.path.join(application_path, image_constants.ANALYTICS_ICON))
        self.stats_button.setIcon(analytics_icon)
        self.stats_button.setIconSize(QSize(64, 64))
        self.stats_button.setToolTip("Use This To: See Analytics about your currently running IVR")

    def setup_generate_ivr_button(self):
        self.generate_ivr_button = QPushButton('Generate IVR', self)
        self.generate_ivr_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        ivr_icon = QIcon(os.path.join(application_path, image_constants.IVR_LOGO_ICON))
        self.generate_ivr_button.setIcon(ivr_icon)
        self.generate_ivr_button.setIconSize(QSize(64, 64))
        self.generate_ivr_button.setToolTip("Use This To: Turn a Voiceflow file or project into an IVR")

    def setup_ivr_status_button(self):
        self.ivr_status_button = QPushButton("IVR Server Status", self)
        self.ivr_status_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        ivr_status_icon = QIcon(os.path.join(application_path, image_constants.SERVER_STATUS_ICON))
        self.ivr_status_button.setIcon(ivr_status_icon)
        self.ivr_status_button.setIconSize(QSize(64, 64))
        self.ivr_status_button.setToolTip("Use This To: Turn the IVR server on or off and view the status")

    def setup_heading(self):
        header_layout = QHBoxLayout()

        nhs_logo = QLabel()
        pixmap = QPixmap(os.path.join(application_path, image_constants.NHS_LOGO))
        pixmap = pixmap.scaled(170, 170, Qt.KeepAspectRatio)
        nhs_logo.setPixmap(pixmap)

        heading_font = QFont('Arial', 16)
        heading_font.setBold(True)

        sub_heading_font = QFont('Arial', 11)
        sub_heading_font.setBold(True)

        sub_heading = QLabel("Create an automated call triage for patients\nI(nteractive) V(oice) R(esponse)")
        sub_heading.setFont(sub_heading_font)

        heading = QLabel("GP IVR")
        heading.setFont(heading_font)

        header_layout.addWidget(nhs_logo)

        heading_layout = QVBoxLayout()
        heading_layout.addWidget(heading)
        heading_layout.addWidget(sub_heading)

        header_layout.addLayout(heading_layout)

        visit_website = QLabel(
            "*For any queries on how to use the program, please refer to the user manual on our website")

        self.layout.addWidget(QLabel())
        self.layout.addLayout(header_layout)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(visit_website)
        self.layout.addWidget(QLabel())