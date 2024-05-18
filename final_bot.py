from collections import UserDict
import datetime
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    def __init__(self, value):
        try:
            value = datetime.datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.phones = [p for p in self.phones if p.value != old_phone]
        self.phones.append(Phone(new_phone))

    def find_phone(self):
        phones_list = []
        for number in self.phones:
            phones_list.append(number.value)
        return phones_list

    def add_birthday(self, birthday):
        if self.birthday:
            return "Birthday already exists."
        self.birthday = Birthday(birthday)
        return "Birthday successfully added."

    def remove_birthday(self):
        if self.birthday:
            self.birthday = None
        else:
            return "Birthday was not set."

    def edit_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        return "Birthday successfully edited"


class AddressBook(UserDict):
    def __init__(self):
        self.data = {}
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value] = record
        return "Record successfully added"

    def find(self, name):
        if name in self.data:
            return self.data[name]

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
            return "Record deleted"
        else:
            return "Record not found"

    def get_upcoming_birthdays(self):
        close_birthdays = []  # Створюємо пустий список для днів народження
        today = datetime.datetime.today().date()  # Отримуємо сьогоднішню дату
        curr_year = datetime.datetime.today().year
        for name, record in self.data.items():
            if record.birthday:
                bday = record.birthday.value
                bday_this_year = bday.replace(year=curr_year)  # Замінюємо рік на поточний
                difference = bday_this_year - today  # Знаходимо, наскільки далеко день народження
                if 0 <= difference.days <= 7:
                    bday_celebration = bday_this_year.strftime("%d.%m.%Y")  # Робимо з об'єкта рядок
                    close_birthdays.append({"name": record.name.value, "birthday_celebration": bday_celebration})  # Створюємо та додаємо словник до списку
        if close_birthdays:
            return close_birthdays
        else:
            return "No upcoming birthdays found"


def input_error(func):  # Функція генератор для обробки помилок
    def wrapper(*args, **kwargs):  # Функція обгортка
        try:
            return func(*args, **kwargs)
        except ValueError:  # Якщо введена не вірна кількість аргументів
            return "Please enter the info according to the instructions. To see instructions, enter 'help'"
        except Exception as e:  # Для обробки інших типів помилок
            return f"An error occurred: {e}"
    return wrapper


@input_error
def add_contact(args, book):  # Функція для додавання контактів
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):  # Функція для зміни номера для існуючого контакту
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    else:
        record.edit_phone(old_phone, new_phone)
        return "Contact successfully updated."


@input_error
def show_phone(args, book):  # Функція для виведення номеру телефону для існуючого контакту
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    else:
        return record.find_phone()


@input_error
def show_all_contacts(book):
    for name in book.data:
        record = book.find(name)
        print(record)


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    else:
        return record.add_birthday(birthday)


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    else:
        return record.birthday


@input_error
def show_upcoming_birthdays(book):
    return book.get_upcoming_birthdays()


def get_help():
    help_speech = """                     Here's the valid syntax for using the bot commands:
                     1. add [name] [phone]. Phone number MUST contain 10 digits only.
                     2. change [name] [old phone] [new phone]. Same rules apply for the phone numbers.
                     3. phone [name] - shows all the phone numbers for a given name
                     4. 'all' - shows all the records in the Address Book
                     5. add-birthday [name] [birthday]. Birthday format MUST be DD-MM-YYYY
                     6. show-birthday [name] - gets the birthday for a given name.
                     7. birthdays - gets all upcoming birthdays for the next week.
                     8. 'hello' - greets the bot
                     9. 'close' or 'exit' for exiting the program.\n"""
    return help_speech


def parse_input(user_input):  # Функція для парсингу введеного користувачем рядка
    cmd, *args = user_input.split()  # Розділяємо рядок на команду і список аргументів
    cmd = cmd.strip().lower()  # Зводимо команду до нижнього регістру
    return cmd, *args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Goodbye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "help":
            print(get_help())

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            show_all_contacts(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_upcoming_birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
