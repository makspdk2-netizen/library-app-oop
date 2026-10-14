from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering


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
