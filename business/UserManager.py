# include all user-related functions here
# login, register, authenticate
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path
from data_models.models import *
from data_access.data_base import init_db


class UserManager:

    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def add_new_user(self):
        new_user = RegisteredGuest(
            firstname="Laura",
            lastname="Mauer",
            email="laura.mauer@gmail.ch",
            address=Address(
                street="Laupenstrasse 35",
                zip="3013",
                city="Bern"
            ),
            login=Login(
                username="laura.mauer1@gmail.ch",
                password="HelloSunshine",
                role=self.__session.query(Role).filter(Role.name == "registered_user").one()
            )
        )
        self.__session.add(new_user)
        self.__session.commit()
        return f"User {new_user.firstname} added as {new_user.login.role.name}."



if __name__ == "__main__":
    DB_FILE = 'path_to_your_database.db'
    user_manager = UserManager("../data/database1.db")
    print("Adding a new user...")

    message = user_manager.add_new_user()
    print(message)
    # user_manager.add_user("email", "username", "password", "role")

    # print(add.user("email", "username", "passwort", "role"))
    # print(add.user("guestUser", "guestPass", "registered_guest"))
    # print(login("adminUser", "adminPass"))
    # print(update_user("guestUser", email="guest@example.com"))
    # print(delete_user("adminUser"))

#1.4. Als Gastnutzer möchte ich möglichst wenig Informationen über mich preisgeben, damit meine Daten privat bleiben.

#1.6. Als Gastbenutzer möchte ich mich mit meiner E-Mail-Adresse und einer persönlichen Kennung (Passwort) registrieren können, um weitere Funktionalitäten nutzen zu können (z.B. Buchungshistorie, Buchungsänderung etc. [siehe 2.1].