from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QLineEdit, QSizePolicy
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QFont

from pathlib import Path

from voiceflow_to_json.settings_modifications.voiceflow_to_json import VoiceflowFileToJson
from voiceflow_to_json.json_to_dialplan.json_to_dialplan import Dialplan
import voiceflow_to_json.constants.asterisk_filepath_constants as asterisk_constants

from voiceflow_to_json.ui_modules.shared_buttons import BackButton


class VfFileEdit(QLineEdit):
    def __init__(self, parent):
        super(VfFileEdit, self).__init__(parent)

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
            filepath = str(urls[0].path())
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
        self.error = False

        self.setup_heading()

        self.button_group = QGroupBox("Drag and Drop File:")
        self.layout.addWidget(self.button_group)
        self.v_box = QVBoxLayout()
        self.button_group.setLayout(self.v_box)

        self.setup_file_edit()

        self.setup_buttons()

        self.layout.addLayout(self.v_box)

        self.setLayout(self.layout)

    def setup_file_edit(self):
        self.file_edit = VfFileEdit(self)
        self.v_box.addWidget(self.file_edit)
        grow_label = QLabel()
        self.v_box.addWidget(grow_label)
        grow_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.file_edit.setToolTip("Add a .vf file - use either 'Browse' or drag and drop")

    def setup_heading(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        rule_font = QFont("Arial", 10)
        rule_font.setItalic(True)

        heading = QLabel("Add Voiceflow File:")
        heading.setFont(heading_font)
        page_info = QLabel("Upload a Voiceflow file to be transformed into an IVR.")
        file_type_rule = QLabel("*File Type Must be .vf")

        self.layout.addWidget(QLabel())
        self.layout.addWidget(heading)
        self.layout.addWidget(page_info)
        self.layout.addWidget(file_type_rule)
        self.layout.addWidget(QLabel())

    def setup_buttons(self):
        self.button_layout = QHBoxLayout()
        self.create_ivr_button = QPushButton("Create IVR", self)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.setToolTip("Browse file manager for .vf file")
        self.create_ivr_button.setToolTip("Generate an IVR from Voiceflow file and replace your current IVR")

        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()

        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.browse_button)
        self.button_layout.addWidget(self.create_ivr_button)
        self.v_box.addLayout(self.button_layout)

    def get_files(self):
        filepath = QFileDialog.getOpenFileName(self, 'Single File', "~", '*.vf')
        self.file_edit.setText(filepath[0])

    def create_ivr(self):
        filepath = Path(self.file_edit.text())

        if not filepath.is_file():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error\n\nThe Path Specified is not a File")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.error = True
            return
        voiceflow_json = VoiceflowFileToJson(self.file_edit.text())
        simplified_json = voiceflow_json.simplified_json()
        self.settings.setValue("simplified json", simplified_json)
        create_ivr = Dialplan(asterisk_constants.EXTENSIONS_CONF_PATH, simplified_json)
        create_ivr.create_config()