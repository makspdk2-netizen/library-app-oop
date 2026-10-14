from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QLabel, QLineEdit,
    QMessageBox, QVBoxLayout,
)

from models import Book
from widgets import HoverButton, LoginEdit, YearSpin, make_title


class BookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.year_spin = YearSpin()
        self.isbn_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Название:", self.title_edit)
        form.addRow("Автор:", self.author_edit)
        form.addRow("Год:", self.year_spin)
        form.addRow("ISBN:", self.isbn_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def make_book(self):
        return Book(self.title_edit.text(), self.author_edit.text(),
                    self.year_spin.value(), self.isbn_edit.text())


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход")
        self.login_edit = LoginEdit()
        self.login_edit.setPlaceholderText("Ваш логин")
        self.login_edit.returnPressed.connect(self.try_accept)

        ok_button = HoverButton("Войти")
        ok_button.clicked.connect(self.try_accept)

        layout = QGridLayout(self)
        layout.addWidget(make_title("Библиотека"), 0, 0, 1, 2)
        layout.addWidget(QLabel("Логин:"), 1, 0)
        layout.addWidget(self.login_edit, 1, 1)
        layout.addWidget(ok_button, 2, 0, 1, 2)

    def login(self):
        return self.login_edit.text().strip()

    def try_accept(self):
        if self.login() == "":
            QMessageBox.warning(self, "Вход", "Введите логин")
            return
        self.accept()
