# include all user-related functions here
# login, register, authenticate

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path
from data_models.models import *
from data_access.data_base import init_db


class UserManager:
    def __init__(self):
        pass

if __name__ == "__main__":
    user_manager = UserManager()

    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    #user=alle die einen account haben
    def add_user(self, email, username, password, role):
        if self.session.query(User).filter_by(email=email).first():
            return "User already exists."
        new_user = User(email=email, username=username, password=password, role=role)
        self.session.add(new_user)
        self.session.commit()
        return f"User {username} added as {role}."


if __name__ == "__main__":
     DB_FILE = 'path_to_your_database.db'
     user_manager = UserManager(DB_FILE)
     print(add_user("email", "username", "password", "role"))

    def update_user(self, email, username, password, role):
        user = self.session.query(User).filter_by(email=email).first()
        if not user:
            return "User not found."


        self.session.commit()
        return f"User {username} updated."

    def delete_user(self, username):
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            return "User not found."
        self.session.delete(user)
        self.session.commit()
        return f"User {username} deleted."

    def login(self, username, password):
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.password == password:
            return f"Login successful for {username}."
        else:
            return "Invalid username or password."

    if __name__ == "__main__":
        user_manager = UserManager()
        print(add.user("email", "username", "passwort", "role"))
        print(add.user("guestUser", "guestPass", "registered_guest"))
        print(login("adminUser", "adminPass"))
        print(update_user("guestUser", email="guest@example.com"))
        print(delete_user("adminUser"))
