import sys

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

#from business.ReservationManager import ReservationManager
from data_access.data_base import init_db
from business.UserManager import UserManager
from business.SearchManager import SearchManager

class AdminMenu():
    def __init__(self, main_menu):
        self._main_menu = main_menu

    def run(self):
        print("Go to InventoryManager for the ADMIN Menu!")
        print("You are logout!")

        user_in = input("Choose Option: ")
        match user_in:
            case "1":
                user_manager.logout()
                return self._main_menu

class RegisteredHomeMenu():

    def __init__(self, main_menu):
        self._main_menu = main_menu

    def run(self):
        print("1. Logout")
        print("2. Search Hotels")
        print("3. Exit")

        user_in = input("Choose Option (1-3): ")
        match user_in:
            case "1":
                user_manager.logout()
                return self._main_menu

class Login():
    def __init__(self, main_menu):
        self._registered_home_menu = RegisteredHomeMenu(main_menu)
        self._admin_menu = AdminMenu(main_menu)

    def run(self):
        while user_manager.has_attempts_left():
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            if user_manager.login(username, password):
                print("Login successful!")
                break
            else:
                print("Login failed! Try again!")

        if user_manager.get_current_login():
            if user_manager.get_current_login().role.access_level < sys.maxsize:
                print("You are logged in as registered Guest")
                print(
                    f"Welcome {user_manager.get_guest_of(user_manager.get_current_login()).firstname} {user_manager.get_guest_of(user_manager.get_current_login()).lastname}")
                return self._registered_home_menu

            elif user_manager.get_current_login().role.access_level == sys.maxsize:
                print("You are logged in as Administrator")
            print(f"Welcome {user_manager.get_current_login().username}!")
            return self._admin_menu

        else:
            print("No attempts left, program is closed!")
            sys.exit(1)

class MainMenu():

    def __init__(self, session, back=None):
        self.session = session
        self._login = Login(self)
        self._search_manager = SearchManager(session)

    def run(self):
        print("1. Login")
        print("2. Register as Guest")
        print("3. Search Hotels")
        print("4. Exit")

        user_in = input("Choose Option: ")
        match user_in:
            case "1":
                return self._login

            case "2":
                print("Register as Guest")
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                firstname = input("Enter your firstname: ")
                lastname = input("Enter your lastname: ")
                email = input("Enter your email: ")
                street = input("Enter your street: ")
                zip = input("Enter your zip: ")
                city = input("Enter your city: ")

                print("Registration successful!")
                print("Now you can book a Room for your stay.")

            case "3":
                while True:
                    print("1. Show all Hotels")
                    print("2. Search by Name")
                    print("3. Exit")

                    choice = input("Choose Option (1-3): ")
                    match choice:
                        case "1":
                            hotels = search_manager.get_all_hotels()
                            for hotel in hotels:
                                print(hotel)
                        case "2":
                            searched_name = input("Enter hotel name: ")
                            hotels = search_manager.get_hotels_by_name(searched_name)
                            for hotel in hotels:
                                print(hotel)
                        case "3":
                            print("Thank you for visiting. Goodbye!")
                            return  # Return to the previous menu
                        case _:
                            print("Invalid option, please try again.")

            case "4":
                print("Thank you for visiting. See you next time!")
                sys.exit(0)

class Application():
    def __init__(self, start):
        self._current = start

    def run(self):
        while True:
            if self._current:
                self._current = self._current.run()
            else:
                sys.exit(0)



if __name__ == '__main__':
    print("Start program...")
    db_file = "./data/database.db"
    database_path = Path(db_file)
    if not database_path.is_file():
        init_db(db_file, generate_example_data=True)
    session = scoped_session(sessionmaker(bind=create_engine(f"sqlite:///{database_path}", echo=False)))
    user_manager = UserManager(session)
    search_manager = SearchManager(session)
    #reservations_manager = ReservationManager(session)



    main_menu = MainMenu(session)

    app = Application(main_menu)
    app.run()



