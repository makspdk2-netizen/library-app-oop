from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QPainter
from PyQt6.QtWidgets import (
    QAbstractItemView, QComboBox, QFrame, QHeaderView, QLabel, QLineEdit,
    QMenu, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
)


def make_title(text):
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 6px;")
    return label


class LoginEdit(QLineEdit):
    def focusOutEvent(self, event):
        self.setText(self.text().strip())
        super().focusOutEvent(event)


class SearchEdit(QLineEdit):
    def focusInEvent(self, event):
        self.setStyleSheet("background: #fffbe6;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet("")
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
            return
        super().keyPressEvent(event)


class HoverButton(QPushButton):
    def enterEvent(self, event):
        self.setStyleSheet("background: #dbeafe;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("")
        super().leaveEvent(event)


class ReaderCombo(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class YearSpin(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(1, datetime.now().year)
        self.setValue(2000)

    def wheelEvent(self, event):
        event.ignore()


class StatusLabel(QLabel):
    def mousePressEvent(self, event):
        self.setText("")
        super().mousePressEvent(event)


class InfoPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(0, 0, 5, self.height(), QColor("#3b82f6"))
        painter.end()


class BookTable(QTableWidget):
    COLUMNS = ("Название", "Автор", "Год", "ISBN", "Статус")

    def __init__(self, parent=None):
        super().__init__(0, len(self.COLUMNS), parent)
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.on_issue = None
        self.on_return = None
        self.on_delete = None

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        items = (("Выдать", self.on_issue), ("Вернуть", self.on_return),
                 ("Удалить", self.on_delete))
        for text, callback in items:
            action = QAction(text, menu)
            if callback is not None:
                action.triggered.connect(callback)
            menu.addAction(action)
        menu.exec(event.globalPos())

    def fill(self, books):
        self.setRowCount(len(books))
        for row, book in enumerate(books):
            if book.is_free:
                status = "Свободна"
            else:
                status = "У " + book.borrowed_by
            values = (book.title, book.author, str(book.year), book.isbn, status)
            for col, value in enumerate(values):
                self.setItem(row, col, QTableWidgetItem(value))
