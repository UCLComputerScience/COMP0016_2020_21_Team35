import os
import sys

from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

import voiceflow_to_json.constants.image_filepath_constants as image_constants

from voiceflow_to_json.settings_modifications.ivr_server import IVRServerStatus
from voiceflow_to_json.ui_modules.shared_buttons import BackButton


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)


class IvrServerStatusWidget(QWidget):
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

        self.ivr_server = IVRServerStatus()

        self.status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        status_label.setToolTip("Status of the IVR server - Online or Offline")
        self.status_layout.addWidget(status_label)
        self.ivr_status_text = QLabel()
        self.ivr_status_icon = QLabel()
        self.status_layout.addWidget(self.ivr_status_text)
        self.status_layout.addWidget(self.ivr_status_icon)

        self.button_layout = QHBoxLayout()

        self.setup_buttons()

        self.grow_label_upper = QLabel()
        self.grow_label_upper.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.grow_label_lower = QLabel()
        self.grow_label_lower.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.v_box.addLayout(self.status_layout)
        self.v_box.addWidget(self.grow_label_upper)
        self.v_box.addWidget(self.grow_label_lower)
        self.v_box.addLayout(self.button_layout)

        self.setLayout(self.layout)

    def setup_buttons(self):
        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()
        self.button_layout.addWidget(self.back_button)

        self.turn_on_button = QPushButton("Turn ON IVR Server")
        self.turn_on_button.setToolTip("This will turn on the IVR server, allowing users to call the IVR")
        self.button_layout.addWidget(self.turn_on_button)

        self.turn_off_button = QPushButton("Turn OFF IVR Server")
        self.turn_off_button.setToolTip(
            "This will turn off the IVR server - users will no longer be able to call the IVR")
        self.button_layout.addWidget(self.turn_off_button)

    def setup_heading(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        heading = QLabel("IVR Server Status:")
        heading.setFont(heading_font)

        subHeading = QLabel("Here you can see and set the status of your IVR server.")

        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)
        self.layout.addWidget(subHeading)

    def start_ivr_status_check(self):
        ivr_online = self.check_ivr_status()
        self.set_ivr_status_layout(ivr_online)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_ivr_status_check)
        self.timer.start(5000)

    def stop_ivr_status_check(self):
        self.timer.stop()

    def set_ivr_status_layout(self, ivr_online):
        self.status_layout.removeWidget(self.ivr_status_text)
        self.ivr_status_text.deleteLater()
        self.ivr_status_text = None

        self.status_layout.removeWidget(self.ivr_status_icon)
        self.ivr_status_icon.deleteLater()
        self.ivr_status_icon = None

        if ivr_online:
            self.ivr_status_text = QLabel("Online")
            self.status_layout.addWidget(self.ivr_status_text, alignment=Qt.AlignRight)

            self.ivr_status_icon = QLabel()
            ivr_status_pixmap = QPixmap(os.path.join(application_path, image_constants.ONLINE_ICON))
            ivr_status_pixmap = ivr_status_pixmap.scaled(16, 16, Qt.KeepAspectRatio)
            self.ivr_status_icon.setPixmap(ivr_status_pixmap)
            self.status_layout.addWidget(self.ivr_status_icon, alignment=Qt.AlignRight)

            self.turn_on_button.setEnabled(False)
            self.turn_off_button.setEnabled(True)
        else:
            self.ivr_status_text = QLabel("Offline")
            self.status_layout.addWidget(self.ivr_status_text, alignment=Qt.AlignRight)

            self.ivr_status_icon = QLabel()
            ivr_status_pixmap = QPixmap(os.path.join(application_path, image_constants.OFFLINE_ICON))
            ivr_status_pixmap = ivr_status_pixmap.scaled(16, 16, Qt.KeepAspectRatio)
            self.ivr_status_icon.setPixmap(ivr_status_pixmap)
            self.status_layout.addWidget(self.ivr_status_icon, alignment=Qt.AlignRight)

            self.turn_on_button.setEnabled(True)
            self.turn_off_button.setEnabled(False)

    def turn_off_ivr(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Warning\n\nTurning OFF the IVR server will mean users can no longer call the IVR.\n\n Are you sure you want to proceed?")
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return_value = msg.exec_()

        if return_value == QMessageBox.Yes:
            self.ivr_server.turn_off_ivr()

    def turn_on_ivr(self):
        self.ivr_server.turn_on_ivr()

    def check_ivr_status(self):
        ivr_online = self.ivr_server.check_ivr_status()
        return ivr_online