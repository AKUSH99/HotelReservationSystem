import sys

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from data_access.data_base import init_db
from business.UserManager import UserManager

class RegistrationUI:
    def __init__(self, session):
        self.session = session


if __name__ == '__main__':
    db_file = "../data/test.db"
    database_path = Path(db_file)
    if not database_path.is_file():
        init_db(db_file, generate_example_data=True)
    session = scoped_session(sessionmaker(bind=create_engine(f"sqlite:///{database_path}", echo=False)))
    user_manager = UserManager(session)
    registration_ui = RegistrationUI(session)

    print("USERSTORY: Login")
    while user_manager.has_attempts_left():
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if user_manager.login(username, password):
            print("Login successful!")
            break
        else:
            print("Login failed! Try again!")

    if user_manager.get_current_login():
        print(f"Welcome {user_manager.get_current_login().username}")
    else:
        print("No attempts left, program is closed!")
        sys.exit(1)

    user_manager.logout()
    print("Goodbye!")
    print(user_manager.get_current_login())

    print("USERSTORY: Register Guest")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    firstname = input("Enter your fristname: ")
    lastname = input("Enter your lastname: ")
    email = input("Enter your email: ")
    street = input("Enter your street: ")
    zip = input("Enter your zip: ")
    city = input("Enter your city: ")

    user_manager.register_guest(username, password, firstname, lastname, email, street, zip, city)
    print("USERSTORY: Login")
    while user_manager.has_attempts_left():
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if user_manager.login(username, password):
            print("Login successful!")
            break
        else:
            print("Login failed!")

    if user_manager.get_current_login():
        print(f"Welcome {user_manager.get_current_login().username}")
    else:
        print("No attempts left, program is closed!")
        sys.exit(1)