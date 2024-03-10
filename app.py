from collections import UserDict
from dataclasses import dataclass
import datetime as dt
from datetime import datetime as dtdt
import re
import pickle
import os
from flask import Flask

app = Flask(__name__)

# обробляємо помилки введення користувача
def _input_error(func):
    def inner(*args, **kwargs):
        function_name = str(func).split(" ")[1].split(".")[1]
        try:
            return func(*args, **kwargs)
        except ValueError:
            if function_name == "add_record":
                return  "\nPlease, enter again your command to add contact correctly. \
                \nGive me name and phone please\n"
            elif function_name == "change_record":
                return  "\nPlease, enter again your command to change contact correctly. \
                \nGive me name and phone please\n"
            elif function_name == "add_birthday":
                return  "\nPlease, enter again your command to add birthday correctly. \
                \nGive me name and birthday date please\n"
        except IndexError:
            if function_name == "show_record":
                return "\nPlease, enter again your command to show contact correctly. \
                \nGive me name please\n"
            elif function_name == "show_birthday":
                return "\nPlease, enter again your command to show birthday correctly. \
                \nGive me name please\n"
        except KeyError:
            if function_name == "show_record":
                return "\nThere is no such contact yet. Add it please.\n"
            elif function_name == "show_birthday":
                return "\nThere is no such contact yet. Add it please.\n"
    return inner

@dataclass
class Field:
    value: str

@dataclass
class Name(Field):
    # реалізація класу
	value: str

@dataclass
class Phone(Field):
    # реалізація класу
    def __init__(self, number: int):
        if len(number) == 10 \
            and str(number).isdigit():
            self.value = number
    def __str__(self):
        return f"{self.value}"

@dataclass
class Birthday(Field):
    def __init__(self, value):
        try:
            # перевірка коректності даних
            # та перетворення рядку на об'єкт datetime
            if re.search(r'(\d{2})\.(\d{2})\.(\d{4})', value):
                self.value = dtdt.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

@dataclass
class Record:
    name = Name
    
    def __init__(self, name: int):
        self.name = name
        self.phones = []
        self.birthday = None

    # реалізація класу
    def __str__(self):
        return f"\nContact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}"
    def __repr__(self):
        return f"\nContact name: {self.name}, phones: {self.phones}"
    
    # додавання телефону
    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
        return "Phone added.\n"
    
    # видалення телефону
    def remove_phone(self, phone: Phone):
        if type(phone)==Phone:
            self.phones = [p for p in self.phones if p.value != phone]
            return "Phone deleted.\n"
        else:
            return "Please use Phone object to remove phone number."
        
    # редагування телефону
    def edit_phone(self, old_phone_number: str, new_phone_number: str):
        if old_phone_number.isdigit() and new_phone_number.isdigit():
            index_of_phone_record = self.phones.index(Phone(old_phone_number))
            self.phones[index_of_phone_record] = Phone(new_phone_number)
            return "Phone changed.\n"
        else:
            return "Please use two digits to edit phone number."
        
    # пошук телефона
    def find_phone(self, phone: str):
        if phone.isdigit():
            if Phone(phone) in self.phones:
                return phone
            else:
                return f"The phone {phone} is not found."
        else:
            return "Please use digits to find phone number."
        
    # додавання дня народження
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

@dataclass
class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
    # функція додавання контакту
    @_input_error
    def add_record(self, args):
        name, phone = args
        if phone.isdigit() and len(phone) == 10:
            our_record = Record(name)
            our_record.add_phone(phone)
            self.data[name] = our_record
            return "Record added.\n" 
        else:
            return "\nPlease use only ten digits.\n"
        
    # функція зміни номера контакту
    @_input_error
    def change_record(self, args):
        name, phone = args
        if phone.isdigit() and len(phone) == 10:
            our_record = Record(name)
            our_record.phones = [Phone(phone)]
            self.data[name] = our_record
            return "Record updated.\n" 
        else:
            return "\nPlease use only ten digits.\n"  
    
    # функція показу номера контакта за його ім'ям
    @_input_error
    def show_record(self, args):
        name = args[0]
        our_record = AddressBook.find(self, name)
        if our_record is not None:
            for phone in our_record.phones:
                our_phones = str(phone.value) + " "
            return f"\nPhone number for user {name} is -> {our_phones}\n"
        else:
            return "\nThere is no such contact yet. Add it please.\n"

    # функція показу всіх контактів
    def show_all(self):
            if len(self.data.items()) > 0:
                for name, record in self.data.items():
                    print(record)
            else: 
                return print("\nYour contacts database is empty!\nAdd contacts please.\n")
        
    # додавання дня народження
    @_input_error
    def add_birthday(self, args):
        name, birth_date = args
        # знаходимо запис і додаємо день народження
        if re.search(r'(\d{2})\.(\d{2})\.(\d{4})', birth_date):
            self.data.get(name) \
                .add_birthday(birth_date)
            return "Birthday added.\n"
        else:
            return "\nInvalid date format. Please use DD.MM.YYYY\n"
        
    # показ дня народження
    @_input_error
    def show_birthday(self, args):
        name = args[0]
        our_record = self.data.get(name)
        if our_record is not None and our_record.birthday is not None: 
            # знаходимо записб і обєкт birthday і дату в ньому і друкуємо
            return f"Birthday for user {name} is -> {self.data.get(name).birthday.value.date()}\n"
        else:
            return f"\nBirthday for user {name} is not added yet.\n"

    # видалення контакту за ім'ям
    def delete(self, name: str):
        if name.isalpha():
            self.data.pop(name)
            return "Record deleted.\n"
        else:
            return "Please use srting name to delete the record."
        
    # пошук контакту
    def find(self, name: str) -> Record:
        if name.isalpha():
            if self.data.get(name) is not None:
                return self.data.get(name)
            else:
                print(f"Record witn name {name} is not found.")
        else:
            print("Please use string name to find the record.")

    # отримуємо список тих, кого треба привітати
    def birthdays(self):
        today_date=dtdt.today().date()
        upcoming_birthdays=[]
        if len(self.data.items()) > 0:
            for name, record in self.data.items():
                birthday_date=record.birthday.value.date()
                birthday_date=str(today_date.year)+str(birthday_date)[4::]
                birthday_date=dtdt.strptime(birthday_date, "%Y-%m-%d").date()
                day_of_week=birthday_date.isoweekday()
                days_difference=(birthday_date-today_date).days
                if 0<=days_difference<7:
                    if day_of_week<6:
                        upcoming_birthdays.append({'name':record.name, 'congratulation_date':birthday_date.strftime("%Y-%m-%d")}) 
                    else:
                        if (birthday_date+dt.timedelta(days=1)).weekday()==0:
                            upcoming_birthdays.append({'name':record.name, 'congratulation_date':(birthday_date+dt.timedelta(days=1)).strftime("%Y-%m-%d")})
                        elif (birthday_date+dt.timedelta(days=2)).weekday()==0:
                            upcoming_birthdays.append({'name':record.name, 'congratulation_date':(birthday_date+dt.timedelta(days=2)).strftime("%Y-%m-%d")})
            return upcoming_birthdays
        else:
            return "\nThere is no birthdays upcoming week.\n"
        
# save data to file
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# return data from gile
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            if os.stat("addressbook.pkl").st_size == 0:
                return AddressBook() # Повернення нової адресної книги, якщо файл empty
            else: 
                return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

# функція розбиття введення користувача на
# окрема команду cmd та
# аргументи *args, введені після команди
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# головна логіка
@app.route('/')
def main():
    book = load_data()
    print("\nWelcome to the assistant bot!\n")
    while True:
        user_input = input("Enter your command: ")
        if user_input is not None:
            if  user_input in ["close", "exit"]:
                save_data(book)
                print("\nGood bye!\n")
                break
            elif user_input=="hello":
                print("\nHow can I help you?\n")
            elif len(user_input)==0:
                print("\nYou entered empty command! Please, try again.\n")
                continue
            else:
                entered_command, *args = parse_input(user_input)
                if entered_command=="add":
                    print(book.add_record(args))
                elif entered_command=="change":
                    print(book.change_record(args))
                elif entered_command=="phone":
                    print(book.show_record(args))
                elif entered_command=="add-birthday":
                    print(book.add_birthday(args))
                elif entered_command=="show-birthday":
                    print(book.show_birthday(args))
                elif entered_command=="all" and len(args)==0:
                    book.show_all()
                elif entered_command=="birthdays" and len(args)==0:
                    print(book.birthdays())
                else:
                    print("\nInvalid command.\n")

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')