from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QWidget,
)

from dialogs import BookDialog
from models import Book, KeyValueMap, Reader
from report import SessionReport
from widgets import (
    BookTable, HoverButton, InfoPanel, ReaderCombo, SearchEdit, StatusLabel,
    make_title,
)


class MainWindow(QMainWindow):
    def __init__(self, library, login):
        super().__init__()
        self._library = library
        self._login = login
        self._report = SessionReport(login)
        self._library.add_reader(Reader(login))
        self._visible = []
        self._filters = KeyValueMap([
            ("Все", lambda b: True),
            ("Свободные", lambda b: b.is_free),
            ("Выданные", lambda b: not b.is_free),
        ])

        self.setWindowTitle("Библиотека книг - " + login)
        self.resize(900, 520)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.search = SearchEdit()
        self.search.setPlaceholderText("Поиск по названию или автору")
        self.search.textChanged.connect(self.refresh)

        self.filter_combo = ReaderCombo()
        self.filter_combo.addItems(self._filters.keys())
        self.filter_combo.currentIndexChanged.connect(self.refresh)

        self.reader_combo = ReaderCombo()

        self.table = BookTable()
        self.table.on_issue = self.issue_book
        self.table.on_return = self.return_book
        self.table.on_delete = self.delete_book

        button_row = QHBoxLayout()
        buttons = (("Добавить", self.add_book), ("Удалить", self.delete_book),
                   ("Выдать", self.issue_book), ("Вернуть", self.return_book),
                   ("Сортировать", self.sort_books))
        for text, callback in buttons:
            button = HoverButton(text)
            button.clicked.connect(callback)
            button_row.addWidget(button)

        self.info = InfoPanel()
        info_layout = QHBoxLayout(self.info)
        self.status = StatusLabel("")
        info_layout.addWidget(QLabel("Пользователь: " + self._login))
        info_layout.addStretch()
        info_layout.addWidget(self.status)

        grid = QGridLayout()
        grid.addWidget(make_title("Библиотека книг"), 0, 0, 1, 4)
        grid.addWidget(QLabel("Поиск:"), 1, 0)
        grid.addWidget(self.search, 1, 1)
        grid.addWidget(QLabel("Показать:"), 1, 2)
        grid.addWidget(self.filter_combo, 1, 3)
        grid.addWidget(self.table, 2, 0, 1, 4)
        grid.addWidget(QLabel("Читатель:"), 3, 0)
        grid.addWidget(self.reader_combo, 3, 1)
        grid.addLayout(button_row, 4, 0, 1, 4)
        grid.addWidget(self.info, 5, 0, 1, 4)
        grid.setColumnStretch(1, 1)

        central = QWidget()
        central.setLayout(grid)
        self.setCentralWidget(central)

    def refresh(self):
        text = self.search.text()
        check = self._filters.get(self.filter_combo.currentText(), lambda b: True)
        self._visible = []
        for book in self._library.books:
            if not check(book):
                continue
            if text.strip() != "" and not Book.matches(book, text):
                continue
            self._visible.append(book)
        self.table.fill(self._visible)

        current = self.reader_combo.currentText() or self._login
        self.reader_combo.clear()
        self.reader_combo.addItems([r.name for r in sorted(self._library.readers)])
        self.reader_combo.setCurrentIndex(max(self.reader_combo.findText(current), 0))

        self.status.setText("Книг показано: %d" % len(self._visible))

    def selected_book(self):
        row = self.table.currentRow()
        if 0 <= row < len(self._visible):
            return self._visible[row]
        QMessageBox.information(self, "Библиотека", "Сначала выберите книгу в таблице")
        return None

    def add_book(self):
        dialog = BookDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._library.add_book(dialog.make_book())
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка", str(error))
            return
        self.refresh()

    def delete_book(self):
        book = self.selected_book()
        if book is None:
            return
        answer = QMessageBox.question(self, "Удаление", "Удалить книгу «%s»?" % book.title)
        if answer == QMessageBox.StandardButton.Yes:
            self._library.remove_book(book)
            self.refresh()

    def issue_book(self):
        book = self.selected_book()
        if book is None:
            return
        reader = Reader(self.reader_combo.currentText())
        try:
            self._library.issue(book, reader)
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка", str(error))
            return
        self.refresh()

    def return_book(self):
        book = self.selected_book()
        if book is None:
            return
        try:
            self._library.give_back(book)
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка", str(error))
            return
        self.refresh()

    def sort_books(self):
        self._library.sort_books()
        self.refresh()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_book()
            return
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
            return
        super().keyPressEvent(event)

    def showEvent(self, event):
        self.search.setFocus()
        super().showEvent(event)

    def closeEvent(self, event):
        self._report.save()
        event.accept()
