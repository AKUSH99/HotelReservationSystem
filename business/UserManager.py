import sys

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session

from data_access.data_base import init_db
from data_models.models import Login, Role, RegisteredGuest, Address



class UserManager():
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

    def register_user(self, username, password, firstname, lastname, email, street, zip_code, city):  # #geändert
        new_address = Address(street=street, zip=zip_code, city=city)  # #geändert
        new_user = RegisteredGuest(firstname=firstname, lastname=lastname, email=email, address=new_address)  #geändert
        new_login = Login(username=username, password=password, role_id=2)  #geändert
        self._session.add(new_address)  # #geändert
        self._session.add(new_user)  #geändert
        self._session.add(new_login)  # #geändert
        # Verknüpfung des neuen Benutzers mit dem Login, falls erforderlich
        new_user.login = new_login  # #geändert
        self._session.commit()  # #geändert
        return new_user  # #geändert

    def register_guest(self, firstname, lastname, email, street, zip, city):  # #geändert
        try:
            new_address = Address(street=street, zip=zip, city=city)  # #geändert
            guest = RegisteredGuest(
                firstname=firstname,
                lastname=lastname,
                email=email,
                address=new_address
            )  # #geändert
            self._session.add(new_address)  # #geändert
            self._session.add(guest)  # #geändert
            self._session.commit()  # #geändert
            self._session.refresh(guest)  # #geändert
            return guest  # #geändert
        except Exception as e:
            self._session.rollback()
            raise e

    #Registrierte Gäste
    def get_guest_of(self, login):
        query = select(RegisteredGuest).where(RegisteredGuest.login == login)
        registered_guest = self._session.execute(query).scalars().one_or_none()
        return registered_guest

    def create_admin(self, username, password):
        if self._current_login and self._current_login.role.name == "administrator":
            query = select(Role).where(Role.name == "administrator")
            role = self._session.execute(query).scalars().one()
            try:
                admin = Login(username=username, password=password, role=role)
                self._session.add(admin)
                self._session.commit()
            except Exception as e:
                self._session.rollback()
                raise e
        else:
            raise PermissionError("Current user is not authorized to create an admin account")

    def get_current_login(self):
        return self._current_login

    def has_attempts_left(self):
        return self._attempts_left > 0

class RegistrationUI:
    def __init__(self, session):
        self.session = session

if __name__ == '__main__':
    db_file = "../data/database.db"
    database_path = Path(db_file)
    if not database_path.is_file():
        init_db(db_file, generate_example_data=True)
    session = scoped_session(sessionmaker(bind=create_engine(f"sqlite:///{database_path}", echo=False)))
    user_manager = UserManager(session)

    print("Login")
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

    if user_manager._current_login.role and user_manager._current_login.role.name == "administrator":
        register_admin = input("Do you want to register a new admin? (yes/no): ").strip().lower()
        if register_admin == "yes":
            admin_username = input("Enter new admin username: ")
            admin_password = input("Enter new admin password: ")
            try:
                new_admin = user_manager.create_admin(admin_username, admin_password)
                print(f"Admin created successfully.")
            except ValueError as e:
                print(e)
            except PermissionError as e:
                print(e)

    user_manager.logout()
    print("Thank your for visiting. Goodbye!")
    print(user_manager.get_current_login())







