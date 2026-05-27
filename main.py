from collections import UserDict
import datetime
from typing import Callable

class InvalidPhoneError(Exception): pass
class InvalidNameError(Exception): pass

def input_error(func: Callable):

    def inner (*args, **kwargs):

        try:
            return func(*args, **kwargs)
         
        except (ValueError, IndexError):
            return "Missing argument. Use 'help' for correct command format."
        
        except NameError:
            return "Contacts are not created yet. Use 'add' to create one."

        except KeyError:
            return "Contact is missing. Use 'add' to create one."
        
        except InvalidNameError:
            return "Wrong name input format. Use 'help' for correct command format."
        
        except InvalidPhoneError:
            return "Wrong phone input format. Use 'help' for correct command format."   

    return inner

def help():
    
    use_cases = ['hello','add contact', 'update contact', 'list all contacts', 'get phone by username', 'add-birthday', 'change-birthday', 'show-birthday', 'birthdays', 'close/exit program']
    command_examples = ['hello','add johndoe 0987654321', 'change johndoe 0987654321 0123456789', 'all', 'phone johndoe', 'add-birthday johndoe 12.08.1993', 'change-birthday johndoe 02.06.1993', 'show-birthday johndoe', 'birthdays', 'close|exit']
    
    col1_width = len(max(use_cases, key = len))
    col2_width = len(max(command_examples, key = len))
    
    table_header = f"|{'USE CASE'.center(col1_width,' ')}|{'COMMAND EXAMPLE'.center(col2_width,' ')}|"
    table_body = zip(use_cases,command_examples)

    print(table_header)
    print(''.center(len(table_header),"_"))

    for col1_value, col2_value in table_body:
        row = f"|{col1_value.center(col1_width,' ')}|{col2_value.center(col2_width,' ')}|"
        print(row)


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value: str):
        if not value.isalpha():
            raise InvalidNameError
        super().__init__(value)

class Phone(Field):
    def __init__(self, value: str):
        if not (value.isdigit() and len(value) == 10):
            raise InvalidPhoneError
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            self.birthday = datetime.datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(self.birthday)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self, phone: str):
        phone = Phone(phone)
        self.phones.append(phone)

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def remove_phone(self, phone: str):
        phone = self.find_phone(phone)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError(f"Phone {phone} not found")

    def edit_phone(self, old_phone: str, new_phone: str):
        new_phone = Phone(new_phone)

        for i,v in enumerate(self.phones):
            if v.value == old_phone:
                self.phones[i] = new_phone
                return True
            
        raise ValueError(f"Phone {old_phone} not found in this record.")
            
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def change_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def add_record (self, record: Record):
        self.data[record.name.value] = record

    def find (self, name: str):
        return self.data.get(name)
    
    def delete (self, name: str):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self) -> str:
    
        users_to_congratulate = []
        today = datetime.date.today()
        future_date = today + datetime.timedelta(days=7)
        
        for name, record in self.data.items():
            if record.birthday is None:
                continue
                            
            birth_date = record.birthday.value
            birthday_this_year = birth_date.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                        
            if today <= birthday_this_year <= future_date:
                users_to_congratulate.append((record.name.value, birthday_this_year))
        
        if users_to_congratulate:
            for user_name, congrats_date in users_to_congratulate:
                formatted_date = congrats_date.strftime("%d.%m.%Y")
                print(f"{user_name}'s celebration is on {formatted_date}")
        else:
            print("No users to congratulate in the next 7 days!")


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        record.add_phone(phone)
        return "Contact added successfully."
    else:
        record.add_phone(phone)
        return "Phone added to existing contact."

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated successfully."
    raise KeyError

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phones: {'; '.join(p.value for p in record.phones)}"
    raise KeyError

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added successfully."
    raise KeyError

@input_error
def change_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday updated successfully."
    raise KeyError

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
        return f"{name} doesn't have a birthday saved."
    raise KeyError


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        
        if not user_input.strip():
            continue
            
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")
            
        elif command == "help":
            help()

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            if not book.data:
                print("Address book is empty.")
            for record in book.values():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "change-birthday":
            print(change_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            book.get_upcoming_birthdays()

        else:
            print("Invalid command. Use 'help' for available command list.")
        
if __name__ == "__main__":
    main()