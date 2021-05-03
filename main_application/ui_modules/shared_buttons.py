from PyQt5.QtWidgets import QDialog, QGroupBox, QMainWindow, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProxyStyle, QStyle
from PyQt5.QtWidgets import QComboBox, QWidget, QApplication, QAction, qApp, QButtonGroup, QFileDialog, QMessageBox, QLineEdit, QSizePolicy, QScrollArea, QDateEdit
from PyQt5.QtCore import QSettings, Qt, QSize, QRect, QPoint, QDateTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

import main_application.constants.image_filepath_constants as image_constants

import os
import sys

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)


# Shared back button - same for every page
class BackButton:
    def create_back_button(self):
        back_button = QPushButton("Back")
        back_icon = QIcon(os.path.join(application_path, image_constants.BACK_BUTTON_ICON))
        back_button.setIcon(back_icon)
        back_button.setIconSize(QSize(16, 16))
        back_button.setToolTip("Go To Previous Page")

        return back_button

    def create_back_layout(self, back_button):
        back_layout = QHBoxLayout()
        back_layout.addWidget(back_button)
        back_layout.addWidget(QLabel())
        back_layout.addWidget(QLabel())
        back_layout.addWidget(QLabel())

        return back_layout