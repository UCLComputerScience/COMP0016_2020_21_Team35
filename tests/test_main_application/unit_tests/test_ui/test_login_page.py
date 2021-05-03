import sys
import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from main_application.ui_modules.UI import LoginWidget

app = QApplication(sys.argv)


class TestLoginPage(unittest.TestCase):
    def setUp(self):
        self.form = LoginWidget()

    def test_username_input(self):
        self.form.email.clear()
        QTest.keyClicks(self.form.email, "test")

        # Push OK with the left mouse button
        login_widget = self.form.login_button
        QTest.mouseClick(login_widget, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 3.5)

    def test_username_input(self):
        self.form.password.clear()
        QTest.keyClicks(self.form.password, "test")

        # Push OK with the left mouse button
        login_widget = self.form.login_button
        QTest.mouseClick(login_widget, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 3.5)



if __name__ == "__main__":
    unittest.main()