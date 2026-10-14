import sys
from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QPainter
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
REPORT_PATH = Path(__file__).with_name("report.txt")


class KeyValueMap:
    def __init__(self, pairs=()):
        self._pairs = []
        for key, value in pairs:
            self.set(key, value)

    def set(self, key, value):
        for i, pair in enumerate(self._pairs):
            if pair[0] == key:
                self._pairs[i] = (key, value)
                return
        self._pairs.append((key, value))

    def get(self, key, default=None):
        for k, v in self._pairs:
            if k == key:
                return v
        return default

    def keys(self):
        return [k for k, v in self._pairs]

    def __len__(self):
        return len(self._pairs)

    def __repr__(self):
        return "KeyValueMap(%r)" % (self._pairs,)


class LibraryEntity(ABC):
    @abstractmethod
    def identity(self):
        pass

    @abstractmethod
    def describe(self):
        pass


@total_ordering
class Book(LibraryEntity):
    def __init__(self, title, author, year, isbn, borrowed_by=""):
        self.title = title
        self.author = author
        self.year = year
        self.isbn = isbn
        self.borrowed_by = borrowed_by

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Название не может быть пустым")
        self._title = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Автор не может быть пустым")
        self._author = value

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        value = int(value)
        if value <= 0 or value > datetime.now().year:
            raise ValueError("Неверный год")
        self._year = value

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("ISBN не может быть пустым")
        self._isbn = value

    @property
    def borrowed_by(self):
        return self._borrowed_by

    @borrowed_by.setter
    def borrowed_by(self, value):
        self._borrowed_by = str(value)

    @property
    def is_free(self):
        return self._borrowed_by == ""

    def identity(self):
        return self._isbn

    def describe(self):
        return "%s - %s (%d)" % (self._title, self._author, self._year)

    @staticmethod
    def matches(book, text):
        text = text.strip().lower()
        return text in book.title.lower() or text in book.author.lower()

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.identity() == other.identity()

    def __lt__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self._title.lower() < other._title.lower()

    def __hash__(self):
        return hash(self.identity())

    def __repr__(self):
        return "Book(%r, %r, %r, %r)" % (self._title, self._author, self._year, self._isbn)

    def __str__(self):
        return self.describe()


@total_ordering
class Reader(LibraryEntity):
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if value == "":
            raise ValueError("Имя не может быть пустым")
        self._name = value

    def identity(self):
        return self._name.lower()

    def describe(self):
        return "Читатель " + self._name

    def __eq__(self, other):
        if not isinstance(other, Reader):
            return NotImplemented
        return self.identity() == other.identity()

    def __lt__(self, other):
        if not isinstance(other, Reader):
            return NotImplemented
        return self.identity() < other.identity()

    def __hash__(self):
        return hash(self.identity())

    def __repr__(self):
        return "Reader(%r)" % self._name

    def __str__(self):
        return self.describe()


class Library:
    def __init__(self):
        self._books = []
        self._readers = []

    @property
    def books(self):
        return list(self._books)

    @property
    def readers(self):
        return list(self._readers)

    def add_book(self, book):
        if book in self._books:
            raise ValueError("Книга с таким ISBN уже есть")
        self._books.append(book)

    def remove_book(self, book):
        self._books.remove(book)

    def add_reader(self, reader):
        if reader not in self._readers:
            self._readers.append(reader)

    def issue(self, book, reader):
        if not book.is_free:
            raise ValueError("Книга уже выдана: " + book.borrowed_by)
        book.borrowed_by = reader.name

    def give_back(self, book):
        if book.is_free:
            raise ValueError("Эта книга не выдана")
        book.borrowed_by = ""

    def sort_books(self):
        self._books.sort()

    @staticmethod
    def demo():
        library = Library()
        books = [
            ("Война и мир", "Лев Толстой", 1869, "978-5-17-000001"),
            ("Преступление и наказание", "Фёдор Достоевский", 1866, "978-5-17-000002"),
            ("Мастер и Маргарита", "Михаил Булгаков", 1967, "978-5-17-000003"),
            ("Евгений Онегин", "Александр Пушкин", 1833, "978-5-17-000004"),
            ("Мёртвые души", "Николай Гоголь", 1842, "978-5-17-000005"),
            ("Отцы и дети", "Иван Тургенев", 1862, "978-5-17-000006"),
            ("Анна Каренина", "Лев Толстой", 1877, "978-5-17-000007"),
            ("Идиот", "Фёдор Достоевский", 1869, "978-5-17-000008"),
            ("Герой нашего времени", "Михаил Лермонтов", 1840, "978-5-17-000009"),
            ("Собачье сердце", "Михаил Булгаков", 1925, "978-5-17-000010"),
        ]
        for b in books:
            library.add_book(Book(*b))
        for name in ("Анна", "Борис", "Виктор", "Галина"):
            library.add_reader(Reader(name))
        return library


class SessionReport:
    HEADER = (
        "+------------------------------------+\n"
        "| login | time_in | time_out |\n"
        "|---------|------------|-------------|\n"
    )

    def __init__(self, login):
        self._login = login
        self._time_in = SessionReport.now()

    @staticmethod
    def now():
        return datetime.now().strftime(TIME_FORMAT)

    def save(self, path=REPORT_PATH):
        is_new = not path.exists() or path.stat().st_size == 0
        row = "|%s | %s | %s |\n" % (self._login, self._time_in, SessionReport.now())
        with open(path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(SessionReport.HEADER)
            f.write(row)


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
