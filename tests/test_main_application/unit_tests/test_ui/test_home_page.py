import sys
import unittest
from PyQt5.QtWidgets import QApplication
from main_application.ui_modules.UI import HomePageWidget

app = QApplication(sys.argv)


class TestHomePage(unittest.TestCase):
    def setUp(self):
        self.form = HomePageWidget()

    def test_ivr_status_button(self):
        self.form.ivr_status_button.click()
        assert self.form.ivr_status_button.clicked()

    def test_generate_ivr_button(self):
        self.form.generate_ivr_button.click()
        assert self.form.generate_ivr_button.clicked()

    def test_add_voice_files_button(self):
        self.form.add_recorded_voice_files_button.click()
        assert self.form.add_recorded_voice_files_button.clicked

    def test_analytics_button(self):
        self.form.stats_button.click()
        assert self.form.stats_button.clicked()

    def test_sip_trunk_settings_button(self):
        self.form.pstn_settings_button.click()
        assert self.form.pstn_settings_button.clicked()

    def test_redirect_settings_button(self):
        self.form.redirect_settings_button.click()
        assert self.form.ui.redirect_settings_button.clicked()



if __name__ == "__main__":
    unittest.main()