import tkinter as tk
from tkinter import messagebox
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


class App:
    def __init__(self, root, inventory_manager):
        self.root = root
        self.inventory_manager = inventory_manager
        self.user_manager = inventory_manager.user_manager

        self.root.title("Hotel Management System")

        self.create_widgets()

    def create_widgets(self):
        # Login Frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=10)

        tk.Label(self.login_frame, text="Username").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Password").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=5)

        # Admin Actions Frame
        self.admin_frame = tk.Frame(self.root)
        self.admin_frame.pack(pady=10)

        self.create_admin_button = tk.Button(self.admin_frame, text="Create Admin", command=self.create_admin)
        self.create_admin_button.grid(row=0, columnspan=2, pady=5)

        self.add_hotel_button = tk.Button(self.admin_frame, text="Add Hotel", command=self.add_hotel)
        self.add_hotel_button.grid(row=1, columnspan=2, pady=5)

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=2, columnspan=2, pady=5)

        self.admin_frame.pack_forget()  # Hide admin actions initially

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.user_manager.login(username, password):
            messagebox.showinfo("Login", "Login successful!")
            self.login_frame.pack_forget()
            self.admin_frame.pack(pady=10)
        else:
            messagebox.showerror("Login", "Login failed! Try again.")

    def logout(self):
        self.user_manager.logout()
        self.admin_frame.pack_forget()
        self.login_frame.pack(pady=10)
        messagebox.showinfo("Logout", "Logged out successfully!")

    def create_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.user_manager.create_admin(username, password)
        messagebox.showinfo("Create Admin", f"Administrator '{username}' successfully created.")

    def add_hotel(self):
        if self.user_manager.is_admin():
            hotel_window = tk.Toplevel(self.root)
            hotel_window.title("Add Hotel")

            tk.Label(hotel_window, text="Hotel Name").grid(row=0, column=0, padx=5, pady=5)
            name_entry = tk.Entry(hotel_window)
            name_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(hotel_window, text="Stars (1-5)").grid(row=1, column=0, padx=5, pady=5)
            stars_entry = tk.Entry(hotel_window)
            stars_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(hotel_window, text="Address ID").grid(row=2, column=0, padx=5, pady=5)
            address_id_entry = tk.Entry(hotel_window)
            address_id_entry.grid(row=2, column=1, padx=5, pady=5)

            def submit_hotel():
                name = name_entry.get()
                stars = int(stars_entry.get())
                address_id = int(address_id_entry.get())
                self.inventory_manager.add_hotel(name, stars, address_id)
                hotel_window.destroy()

            submit_button = tk.Button(hotel_window, text="Submit", command=submit_hotel)
            submit_button.grid(row=3, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can add new hotels.")


if __name__ == "__main__":
    db_file = "../data/database.db"
    inventory_manager = InventoryManager(db_file)

    root = tk.Tk()
    app = App(root, inventory_manager)
    root.mainloop()
