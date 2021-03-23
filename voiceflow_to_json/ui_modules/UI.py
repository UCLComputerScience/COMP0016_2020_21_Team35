import sys
import os

from PyQt5.QtWidgets import QDialog, QGroupBox, QMainWindow, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProxyStyle, QStyle
from PyQt5.QtWidgets import QComboBox, QWidget, QApplication, QAction, qApp, QButtonGroup, QFileDialog, QMessageBox, QLineEdit, QSizePolicy, QScrollArea, QDateEdit
from PyQt5.QtCore import QSettings, Qt, QSize, QRect, QPoint, QDateTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

from voiceflow_to_json.ui_modules.add_voice_files_page import AddVoiceFilesWidget
from voiceflow_to_json.ui_modules.choose_voiceflow_file_page import ChooseVoiceflowFileWidget
from voiceflow_to_json.ui_modules.home_page import HomePageWidget
from voiceflow_to_json.ui_modules.ivr_generator_page import IvrGeneratorWidget
from voiceflow_to_json.ui_modules.ivr_server_status_page import IvrServerStatusWidget
from voiceflow_to_json.ui_modules.login_page import LoginWidget
from voiceflow_to_json.ui_modules.project_page import ProjectWidget
from voiceflow_to_json.ui_modules.pstn_settings_page import PstnSettingsWidget
from voiceflow_to_json.ui_modules.redirect_settings_page import RedirectSettingsWidget
from voiceflow_to_json.ui_modules.statistics_page import StatsWidget


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

class ProxyStyle(QProxyStyle):
    def drawControl(self, element, option, painter, widget=None):
        if element == QStyle.CE_PushButtonLabel:
            icon = QIcon(option.icon)
            option.icon = QIcon()
        super(ProxyStyle, self).drawControl(element, option, painter, widget)
        if element == QStyle.CE_PushButtonLabel:
            if not icon.isNull():
                iconSpacing = 4
                mode = (
                    QIcon.Normal
                    if option.state & QStyle.State_Enabled
                    else QIcon.Disabled
                )
                if (
                    mode == QIcon.Normal
                    and option.state & QStyle.State_HasFocus
                ):
                    mode = QIcon.Active
                state = QIcon.Off
                if option.state & QStyle.State_On:
                    state = QIcon.On
                window = widget.window().windowHandle() if widget is not None else None
                pixmap = icon.pixmap(window, option.iconSize, mode, state)
                pixmapWidth = pixmap.width() / pixmap.devicePixelRatio()
                pixmapHeight = pixmap.height() / pixmap.devicePixelRatio()
                iconRect = QRect(
                    QPoint(), QSize(pixmapWidth, pixmapHeight)
                )
                iconRect.moveCenter(option.rect.center())
                iconRect.moveLeft(option.rect.left() + iconSpacing)
                iconRect = self.visualRect(option.direction, option.rect, iconRect)
                iconRect.translate(
                    self.proxy().pixelMetric(
                        QStyle.PM_ButtonShiftHorizontal, option, widget
                    ),
                    self.proxy().pixelMetric(
                        QStyle.PM_ButtonShiftVertical, option, widget
                    ),
                )
                painter.drawPixmap(iconRect, pixmap)

class ProgramUi(QMainWindow):
    """PyCalc's View (GUI)."""
    def __init__(self):
        """View initializer."""
        super().__init__()
        self.initUI()

    def initUI(self):
        exit_act = QAction(QIcon('exit.png'), '&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(qApp.quit)

        home_page_action = QAction("Home Page", self)
        home_page_action.triggered.connect(lambda: self.home_page_setup())

        ivr_server_status_action = QAction("IVR Server Status", self)
        ivr_server_status_action.triggered.connect(lambda : self.ivr_server_status_setuo())

        generate_ivr_action = QAction("Generate IVR", self)
        generate_ivr_action.triggered.connect(lambda: self.ivr_generator_setup())

        pstn_settings_action = QAction("SIP Trunk Settings", self)
        pstn_settings_action.triggered.connect(lambda: self.pstn_settings_setup())

        redirect_settings_action = QAction("Redirect Settings", self)
        redirect_settings_action.triggered.connect(lambda: self.redirect_settings_setup("home"))

        stats_action = QAction("Analytics", self)
        stats_action.triggered.connect(lambda: self.stats_setup())

        add_voice_files_action = QAction("Add Recorded Voice Files", self)
        add_voice_files_action.triggered.connect(lambda: self.add_voice_files_setup())

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Menu')
        fileMenu.addAction(home_page_action)
        fileMenu.addAction(ivr_server_status_action)
        fileMenu.addAction(generate_ivr_action)
        fileMenu.addAction(add_voice_files_action)
        fileMenu.addAction(stats_action)
        fileMenu.addAction(pstn_settings_action)
        fileMenu.addAction(redirect_settings_action)
        fileMenu.addAction(exit_act)

        self.setGeometry(200, 200, 200, 200)

        self.home_page_setup()

    def home_page_setup(self):
        self.resize(600, 700)
        self.home_page = HomePageWidget()
        self.setCentralWidget(self.home_page)
        self.setWindowTitle("Home")
        self.home_page_events()

    def ivr_server_status_setup(self):
        self.resize(600, 150)
        self.ivr_server_status = IvrServerStatusWidget()
        self.setCentralWidget(self.ivr_server_status)
        self.setWindowTitle("IVR Server Status")
        self.ivr_server_status.start_ivr_status_check()
        self.ivr_server_status_events()

    def ivr_generator_setup(self):
        self.resize(600, 500)
        self.ivr_generator = IvrGeneratorWidget()
        self.setCentralWidget(self.ivr_generator)
        self.setWindowTitle("IVR Generation")
        self.ivr_generator_events()

    def add_voice_files_setup(self):
        self.resize(800, 700)
        self.add_voice_files = AddVoiceFilesWidget()

        self.add_voice_files_scroll = QScrollArea()
        self.add_voice_files_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.add_voice_files_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.add_voice_files_scroll.setWidgetResizable(True)
        self.add_voice_files_scroll.setWidget(self.add_voice_files)

        self.setCentralWidget(self.add_voice_files_scroll)
        self.setWindowTitle("Add Recorded Voice Files to IVR")
        self.add_voice_files_events()

    def stats_setup(self):
        self.resize(800, 600)
        self.stats = StatsWidget()
        self.setCentralWidget(self.stats)
        self.setWindowTitle("Analytics")
        self.stats_events()

    def pstn_settings_setup(self):
        self.resize(550, 450)
        self.pstn_settings = PstnSettingsWidget()
        self.setCentralWidget(self.pstn_settings)
        self.setWindowTitle("SIP Trunk Settings")
        self.pstn_settings_events()

    def redirect_settings_setup(self, page):
        self.resize(600, 500)
        self.redirect_settings = RedirectSettingsWidget(page)

        self.redirect_scroll = QScrollArea()
        self.redirect_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.redirect_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.redirect_scroll.setWidgetResizable(True)
        self.redirect_scroll.setWidget(self.redirect_settings)

        self.setCentralWidget(self.redirect_scroll)
        self.setWindowTitle("Redirect Settings")
        self.redirect_settings_events()

    def login_setup(self):
        self.resize(500, 150)
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
        self.resize(500, 150)
        if(self.login.project_window()):
            self.project = ProjectWidget(self.login.voiceflow_api, self.login.auth_token)
            self.setCentralWidget(self.project)
            self.setWindowTitle("Project Selection")
            self.project_events()

    def add_voice_files_forward(self):
        if not self.add_voice_files.error:
            self.add_voice_files.close()
            self.resize(100, 100)
            self.ivr_generator_setup()

    def redirect_settings_forward(self):
        if not self.redirect_settings.error:
            self.redirect_settings.close()
            self.resize(100, 100)
            self.home_page_setup()

    def choose_voiceflow_file_forward(self):
        if not self.choose_voiceflow_file.error:
            self.choose_voiceflow_file.close()
            self.resize(100, 100)
            self.redirect_settings_setup("project")

    def project_forward(self):
        if not self.project.error:
            self.project.close()
            self.resize(100, 100)
            self.redirect_settings_setup("project")

    def choose_voiceflow_file_events(self):
        self.choose_voiceflow_file.browse_button.clicked.connect(lambda: self.choose_voiceflow_file.get_files())
        self.choose_voiceflow_file.create_ivr_button.clicked.connect(lambda: self.choose_voiceflow_file.create_ivr())

        self.choose_voiceflow_file.create_ivr_button.clicked.connect(lambda: self.choose_voiceflow_file_forward())

        self.choose_voiceflow_file.back_button.clicked.connect(lambda: self.choose_voiceflow_file.close())
        self.choose_voiceflow_file.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.choose_voiceflow_file.back_button.clicked.connect(lambda: self.ivr_generator_setup())

    def home_page_events(self):
        self.home_page.ivr_status_button.clicked.connect(lambda: self.home_page.close())
        self.home_page.ivr_status_button.clicked.connect(lambda: self.resize(100, 100))
        self.home_page.ivr_status_button.clicked.connect(lambda: self.ivr_server_status_setup())

        self.home_page.generate_ivr_button.clicked.connect(lambda: self.home_page.close())
        self.home_page.generate_ivr_button.clicked.connect(lambda: self.resize(100, 100))
        self.home_page.generate_ivr_button.clicked.connect(lambda: self.ivr_generator_setup())

        self.home_page.add_recorded_voice_files_button.clicked.connect(lambda: self.home_page.close())
        self.home_page.add_recorded_voice_files_button.clicked.connect(lambda: self.resize(100, 100))
        self.home_page.add_recorded_voice_files_button.clicked.connect(lambda: self.add_voice_files_setup())

        self.home_page.pstn_settings_button.clicked.connect(lambda: self.home_page.close())
        self.home_page.pstn_settings_button.clicked.connect(lambda: self.resize(100, 100))
        self.home_page.pstn_settings_button.clicked.connect(lambda: self.pstn_settings_setup())

        self.home_page.redirect_settings_button.clicked.connect(lambda: self.home_page.close())
        self.home_page.redirect_settings_button.clicked.connect(lambda: self.resize(100, 100))
        self.home_page.redirect_settings_button.clicked.connect(lambda: self.redirect_settings_setup("home"))

        self.home_page.stats_button.clicked.connect(lambda: self.home_page.close())
        self.home_page.stats_button.clicked.connect(lambda: self.resize(100, 100))
        self.home_page.stats_button.clicked.connect(lambda: self.stats_setup())

    def ivr_server_status_events(self):
        self.ivr_server_status.turn_off_button.clicked.connect(lambda: self.ivr_server_status.turn_off_ivr())
        self.ivr_server_status.turn_on_button.clicked.connect(lambda: self.ivr_server_status.turn_on_ivr())

        self.ivr_server_status.back_button.clicked.connect(lambda: self.ivr_server_status.stop_ivr_status_check())
        self.ivr_server_status.back_button.clicked.connect(lambda: self.ivr_server_status.close())
        self.ivr_server_status.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.ivr_server_status.back_button.clicked.connect(lambda: self.home_page_setup())

    def ivr_generator_events(self):
        self.ivr_generator.voiceflow_to_json_button.clicked.connect(lambda: self.ivr_generator.close())
        self.ivr_generator.voiceflow_to_json_button.clicked.connect(lambda: self.resize(100, 100))
        self.ivr_generator.voiceflow_to_json_button.clicked.connect(lambda: self.login_setup())

        self.ivr_generator.json_file_button.clicked.connect(lambda: self.ivr_generator.close())
        self.ivr_generator.json_file_button.clicked.connect(lambda: self.resize(100, 100))
        self.ivr_generator.json_file_button.clicked.connect(lambda: self.choose_voiceflow_file_setup())

        self.ivr_generator.back_button.clicked.connect(lambda: self.ivr_generator.close())
        self.ivr_generator.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.ivr_generator.back_button.clicked.connect(lambda: self.home_page_setup())

    def add_voice_files_events(self):
        self.add_voice_files.apply_settings_button.clicked.connect(lambda: self.add_voice_files.apply_settings())
        self.add_voice_files.browse_button_group.buttonClicked.connect(self.add_voice_files.browse_files)

        self.add_voice_files.apply_settings_button.clicked.connect(lambda: self.add_voice_files_forward())

        self.add_voice_files.back_button.clicked.connect(lambda: self.add_voice_files.close())
        self.add_voice_files.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.add_voice_files.back_button.clicked.connect(lambda: self.home_page_setup())

    def pstn_settings_events(self):
        self.pstn_settings.add_ip_address_button.clicked.connect(lambda: self.pstn_settings.add_ip_address())
        self.pstn_settings.apply_settings_button.clicked.connect(lambda: self.pstn_settings.apply_settings())
        self.pstn_settings.delete_button_group.buttonClicked.connect(self.pstn_settings.delete_ip_address)

        self.pstn_settings.apply_settings_button.clicked.connect(lambda: self.pstn_settings.close())
        self.pstn_settings.apply_settings_button.clicked.connect(lambda: self.resize(100, 100))
        self.pstn_settings.apply_settings_button.clicked.connect(lambda: self.home_page_setup())

        self.pstn_settings.back_button.clicked.connect(lambda: self.pstn_settings.close())
        self.pstn_settings.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.pstn_settings.back_button.clicked.connect(lambda: self.home_page_setup())

    def redirect_settings_events(self):
        self.redirect_settings.apply_settings_button.clicked.connect(lambda: self.redirect_settings.apply_settings())

        self.redirect_settings.apply_settings_button.clicked.connect(lambda: self.redirect_settings_forward())

        if not self.redirect_settings.page == "project":
            self.redirect_settings.back_button.clicked.connect(lambda: self.redirect_settings.close())
            self.redirect_settings.back_button.clicked.connect(lambda: self.resize(100, 100))
            self.redirect_settings.back_button.clicked.connect(lambda: self.home_page_setup())

    def login_events(self):
        self.login.login_button.clicked.connect(lambda: self.project_setup())

        self.login.back_button.clicked.connect(lambda: self.login.close())
        self.login.back_button.clicked.connect(lambda: self.resize(100,100))
        self.login.back_button.clicked.connect(lambda: self.ivr_generator_setup())

    def project_events(self):
        self.project.workspace_combo_box.currentTextChanged.connect(lambda: self.project.on_workspace_changed(self.project.workspace_combo_box.currentText()))
        self.project.projects_combo_box.currentTextChanged.connect(lambda: self.project.on_project_changed(self.project.projects_combo_box.currentText()))
        self.project.create_ivr_button.clicked.connect(lambda: self.project.create_ivr())

        self.project.create_ivr_button.clicked.connect(lambda: self.project_forward())

        self.project.back_button.clicked.connect(lambda: self.project.close())
        self.project.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.project.back_button.clicked.connect(lambda: self.login_setup())

    def stats_events(self):
        self.stats.back_button.clicked.connect(lambda: self.stats.close())
        self.stats.back_button.clicked.connect(lambda: self.resize(100, 100))
        self.stats.back_button.clicked.connect(lambda: self.home_page_setup())


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    proxy_style = ProxyStyle(app.style())
    app.setStyle(proxy_style)
    view = ProgramUi()
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()







