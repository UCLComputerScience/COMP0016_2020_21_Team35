from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QWidget, QButtonGroup, QFileDialog, QMessageBox, QLineEdit, QSizePolicy
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QFont

from pathlib import Path

from voiceflow_to_json.settings_modifications.voiceflow_to_json import GetVoiceflowSettings
from voiceflow_to_json.settings_modifications.modify_voice_files import ModifyVoiceFiles
import voiceflow_to_json.constants.asterisk_filepath_constants as asterisk_constants

from voiceflow_to_json.ui_modules.shared_buttons import BackButton


class WavFileEdit(QLineEdit):
    def __init__(self, parent):
        super(WavFileEdit, self).__init__(parent)

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
            if filepath[-4:].lower() == ".wav":
                self.setText(filepath)
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle("Error: Invalid File")
                dialog.setText("Only .wav files are accepted")
                dialog.setIcon(QMessageBox.Warning)
                dialog.exec_()


class AddVoiceFilesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.settings = QSettings("voice_file_settings", "GP_IVR_Settings")

        self.error = False

        self.browse_button_group = QButtonGroup(self)

        self.setup_heading()

        self.voiceflow_settings = QSettings("simplified_voiceflow", "GP_IVR_Settings")
        self.voice_files = {}
        self.node_ids = []
        self.setup_voice_files_form()
        self.init_settings()

        self.setup_buttons()

        self.setLayout(self.layout)

    def setup_heading(self):
        heading_font = QFont('Arial', 12)
        heading_font.setBold(True)

        rules_font = QFont('Arial', 10)
        rules_font.setItalic(True)

        self.layout.addWidget(QLabel())
        heading = QLabel("Add IVR Voice Files:")
        heading.setFont(heading_font)

        page_info = QLabel(
            "You can add personal recorded voice files in place of the automatically\n generated voice files for each "
            "question in the IVR.")

        file_type_rule = QLabel("* WAV Files Only")
        file_type_rule.setFont(rules_font)

        self.layout.addWidget(heading)
        self.layout.addWidget(page_info)
        self.layout.addWidget(file_type_rule)

    def setup_buttons(self):
        button_layout = QHBoxLayout()

        back_button_creator = BackButton()
        self.back_button = back_button_creator.create_back_button()
        button_layout.addWidget(self.back_button)

        self.apply_settings_button = QPushButton("Apply")
        self.apply_settings_button.setToolTip("Replace IVR voice files with updated files")
        button_layout.addWidget(self.apply_settings_button)

        self.layout.addWidget(QLabel())
        self.layout.addLayout(button_layout)

    def init_settings(self):
        for node in self.voice_files:
            node_value = self.settings.value(node)
            if node_value:
                self.voice_files[node].setText(node_value)

    def setup_voice_files_form(self):
        voiceflow_settings = GetVoiceflowSettings(self.voiceflow_settings.value("simplified json"))
        ivr_texts = voiceflow_settings.get_ivr_texts()

        if ivr_texts == -1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error\n\nYou have not set up an IVR")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        for node in ivr_texts:
            self.add_voice_file_input(ivr_texts[node], node)

    def add_voice_file_input(self, ivr_text, ivr_node):
        ivr_text = QLabel(ivr_text)
        ivr_text.setWordWrap(True)
        voice_file = WavFileEdit(self)

        self.button_group = QGroupBox()
        self.layout.addWidget(self.button_group)
        self.v_box = QHBoxLayout()
        self.button_group.setLayout(self.v_box)
        browse_files_button = QPushButton("Browse", self)
        browse_files_button.setToolTip("Browse file manager for WAV file")

        self.v_box.addWidget(ivr_text)
        grow_label = QLabel()
        self.v_box.addWidget(grow_label)
        grow_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.v_box.addWidget(voice_file)
        self.v_box.addWidget(browse_files_button)

        self.voice_files[ivr_node] = voice_file
        self.browse_button_group.addButton(browse_files_button)
        self.node_ids.append(ivr_node)

    def get_files(self, voice_file_edit):
        filepath = QFileDialog.getOpenFileName(self, 'Single File', "~", '*.wav')
        voice_file_edit.setText(filepath[0])

    def apply_settings(self):
        self.save_settings()
        voice_file_paths = []
        node_ids = []

        for node in self.voice_files:

            voice_file_path_text = self.voice_files[node].text()
            voice_file_path = Path(voice_file_path_text)

            if not voice_file_path.is_file():
                if not voice_file_path_text:
                    continue
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error\n\nThe Path Specified is not a File")
                msg.setWindowTitle("Error")
                msg.exec_()
                self.error = True
                return

            node_ids.append(node)
            voice_file_paths.append(self.voice_files[node].text())
        if voice_file_paths:
            modify_voice_files = ModifyVoiceFiles(asterisk_constants.VOICE_FILE_PATH, node_ids, voice_file_paths)
            modify_voice_files.replace_asterisk_voice_files()

    def save_settings(self):
        self.settings.clear()
        for node in self.voice_files:
            if self.voice_files[node].text():
                self.settings.setValue(node, self.voice_files[node].text())

    def browse_files(self, button):
        voice_file_index = - 2 - self.browse_button_group.id(button)
        self.get_files(self.voice_files[self.node_ids[voice_file_index]])