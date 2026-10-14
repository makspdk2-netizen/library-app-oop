import sys

from PyQt6.QtWidgets import QApplication, QDialog

from dialogs import LoginDialog
from main_window import MainWindow
from models import Library


def main():
    app = QApplication(sys.argv)
    dialog = LoginDialog()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return 0
    window = MainWindow(Library.demo(), dialog.login())
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
