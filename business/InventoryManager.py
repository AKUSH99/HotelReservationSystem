import sys
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session

from data_access.data_base import init_db
from data_models.models import Login, Role, RegisteredGuest, Address, Guest, Hotel


class InventoryManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__Session = scoped_session(sessionmaker(bind=self.__engine))
        self.user_manager = UserManager(self.__Session)

    def add_hotel(self, name, stars, address_id):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können neue Hotels hinzufügen.")
            return

        session = self.__Session()
        try:
            new_hotel = Hotel(name=name, stars=stars, address_id=address_id)
            session.add(new_hotel)
            session.commit()
            print(f"Hotel '{name}' erfolgreich hinzugefügt.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Hinzufügen des Hotels: {e}")
        finally:
            session.close()


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

    def get_guest_of(self, login: Login):
        query = select(RegisteredGuest).where(RegisteredGuest.login == login)
        registered_guest = self._session.execute(query).scalars().one_or_none()
        return registered_guest

    def create_admin(self, username, password):
        # Check if username already exists
        existing_user = self._session.execute(select(Login).where(Login.username == username)).scalars().one_or_none()
        if existing_user:
            print(f"Fehler: Benutzername '{username}' existiert bereits.")
            return

        query = select(Role).where(Role.name == "administrator")
        role = self._session.execute(query).scalars().one()
        try:
            admin = Login(username=username, password=password, role=role)
            self._session.add(admin)
            self._session.commit()
            print(f"Administrator '{username}' erfolgreich erstellt.")
        except Exception as e:
            self._session.rollback()
            raise e

    def get_current_login(self):
        return self._current_login

    def has_attempts_left(self):
        return self._attempts_left > 0

    def is_admin(self):
        if self._current_login and self._current_login.role.name == "administrator":
            return True
        return False


if __name__ == "__main__":
    db_file = "/mnt/data/database.db"
    inventory_manager = InventoryManager(db_file)

    # Example: Logging in as admin
    print("USERSTORY: Login as admin")
    while inventory_manager.user_manager.has_attempts_left():
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if inventory_manager.user_manager.login(username, password):
            print("Login successful!")
            break
        else:
            print("Login failed! Try again!")

    if inventory_manager.user_manager.get_current_login():
        print(f"Welcome {inventory_manager.user_manager.get_current_login().username}")
    else:
        print("No attempts left, program is closed!")
        sys.exit(1)

    # Example: Adding a hotel
    if inventory_manager.user_manager.is_admin():
        print("USERSTORY: Add a Hotel")
        name = input("Enter the hotel name: ")
        stars = int(input("Enter the hotel stars (1-5): "))
        address_id = int(input("Enter the address ID: "))
        inventory_manager.add_hotel(name, stars, address_id)
    else:
        print("Nur Administratoren können neue Hotels hinzufügen.")

    inventory_manager.user_manager.logout()
    print("Goodbye!")

