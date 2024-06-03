import sys
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session

from data_access.data_base import init_db
from data_models.models import Login, Role, RegisteredGuest, Address


class UserManager(object):
    def __init__(self, session):
        self._max_attempts = 3
        self._current_login = None
        self._attempts_left = self._max_attempts
        self._session = session

    def login(self, username, password):
        self._attempts_left -= 1
        if self._attempts_left >= 0:
            if self._current_login is None:
                query = select(Login).where(Login.username == username).where(Login.password == password)
                result = self._session.execute(query).scalars().one_or_none()
                self._current_login = result
                return self._current_login

            else:
                return None

        else:
            return None

    def logout(self):
        self._attempts_left = self._max_attempts
        self._current_login = None

    def register_guest(self, username, password, firstname, lastname, email, street, zip, city):
        query = select(Role).where(Role.name == "registered_user")
        role = self._session.execute(query).scalars().one()
        try:
            registered_guest = RegisteredGuest(
                firstname=firstname,
                lastname=lastname,
                email=email,
                address=Address(street=street, zip=zip, city=city),
                login=Login(username=username, password=password, role=role)
            )
            self._session.add(registered_guest)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e

    def get_guest_of(self, login:login):
        query = select(RegisteredGuest).where(RegisteredGuest.login == login)
        registered_guest = self._session.execute(query).scalars().one_or_none()
        return registered_guest

    def create_admin(self, username, password):
        query = select(Role).where(Role.name == "administrator")
        role = self._session.execute(query).scalars().one()
        try:
            admin = Login(username=username, password=password, role=role)
            self._session.add(admin)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e

    def get_current_login(self):
        return self._current_login

    def has_attempts_left(self):
        return self._attempts_left > 0

if __name__ == '__main__':
    db_file = "../data/test.db"
    database_path = Path(db_file)
    if not database_path.is_file():
        init_db(db_file, generate_example_data=True)
    session = scoped_session(sessionmaker(bind=create_engine(f"sqlite:///{database_path}", echo=False)))
    user_manager = UserManager(session)

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
            print("Login failed! Try again!")

    if user_manager.get_current_login():
        print(f"Welcome {user_manager.get_current_login().username}")
    else:
        print("No attempts left, program is closed!")
        sys.exit(1)

