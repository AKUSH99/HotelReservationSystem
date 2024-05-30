from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from pathlib import Path
from data_models.models import *
from data_access.data_base import init_db
import csv


class UserManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def user_exists(self, username):
        # Prüft, ob ein Benutzername bereits in der Datenbank existiert
        return self.__session.query(Login).filter_by(username=username).first() is not None

    def add_new_user(self, firstname, lastname, email, username, password, street, zip, city):
        if self.user_exists(username):
            return "Error: Username already exists. Please choose a different username."

        new_user = RegisteredGuest(
            firstname=firstname,
            lastname=lastname,
            email=email,
            address=Address(
                street=street,
                zip=zip,
                city=city
            ),
            login=Login(
                username=username,
                password=password,
                role=self.__session.query(Role).filter(Role.name == "registered_user").one()
            )
        )
        try:
            self.__session.add(new_user)
            self.__session.commit()
            return f"User {new_user.firstname} added as {new_user.login.role.name}."
        except IntegrityError as e:
            self.__session.rollback()
            return f"Failed to add user due to database error: {e}"

    def get_user_by_username(self, username):
        # Holt einen Benutzer anhand des Benutzernamens über die Login-Tabelle
        return self.__session.query(RegisteredGuest).join(Login).filter(Login.username == username).first()

    def authenticate_user(self, username, password):
        # Authentifiziert einen Benutzer
        user = self.__session.query(Login).filter_by(username=username, password=password).first()
        if user:
            return self.__session.query(RegisteredGuest).filter_by(id=user.guest_id).first()
        return None

    def save_user_details_to_csv(self, user):
        # Speichert die Benutzerdetails in einer CSV-Datei
        headers = ["Firstname", "Lastname", "Email", "Username", "City", "Street", "Zip"]
        user_data = [user.firstname, user.lastname, user.email, user.login.username, user.address.city,
                     user.address.street, user.address.zip]

        with open('user_details.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(user_data)


if __name__ == "__main__":
    DB_FILE = '../data/database1.db'
    user_manager = UserManager(DB_FILE)
    print("Adding a new user...")
    firstname = input("Vorname: ")
    lastname = input("Nachname: ")
    email = input("Email: ")
    username = input("Benutzername: ")
    password = input("Passwort: ")
    street = input("Straße: ")
    zip_code = input("Postleitzahl: ")
    city = input("Stadt: ")

    message = user_manager.add_new_user(firstname, lastname, email, username, password, street, zip_code, city)
    print(message)
