import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import sessionmaker, scoped_session

# Importiere die Modelle (stellen Sie sicher, dass diese korrekt importiert sind)
from data_access.data_base import init_db
from data_models.models import Login, Role, RegisteredGuest, Address, Guest, Hotel, Booking, Room


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

    def remove_hotel(self, hotel_id):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können Hotels entfernen.")
            return

        session = self.__Session()
        try:
            session.execute(delete(Hotel).where(Hotel.id == hotel_id))
            session.commit()
            print(f"Hotel mit ID '{hotel_id}' erfolgreich entfernt.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Entfernen des Hotels: {e}")
        finally:
            session.close()

    def update_hotel_info(self, hotel_id, name=None, stars=None, address_id=None):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können Hotelinformationen aktualisieren.")
            return

        session = self.__Session()
        try:
            hotel = session.execute(select(Hotel).where(Hotel.id == hotel_id)).scalars().one_or_none()
            if hotel:
                if name:
                    hotel.name = name
                if stars:
                    hotel.stars = stars
                if address_id:
                    hotel.address_id = address_id
                session.commit()
                print(f"Hotel mit ID '{hotel_id}' erfolgreich aktualisiert.")
            else:
                print(f"Hotel mit ID '{hotel_id}' nicht gefunden.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Aktualisieren des Hotels: {e}")
        finally:
            session.close()

    def list_bookings(self):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können Buchungen anzeigen.")
            return

        session = self.__Session()
        try:
            bookings = session.execute(select(Booking)).scalars().all()
            return bookings
        except Exception as e:
            print(f"Fehler beim Abrufen der Buchungen: {e}")
        finally:
            session.close()

    def update_booking_info(self, booking_id, **kwargs):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können Buchungsinformationen aktualisieren.")
            return

        session = self.__Session()
        try:
            booking = session.execute(select(Booking).where(Booking.id == booking_id)).scalars().one_or_none()
            if booking:
                for key, value in kwargs.items():
                    setattr(booking, key, value)
                session.commit()
                print(f"Buchung mit ID '{booking_id}' erfolgreich aktualisiert.")
            else:
                print(f"Buchung mit ID '{booking_id}' nicht gefunden.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Aktualisieren der Buchung: {e}")
        finally:
            session.close()

    def manage_room_availability(self, room_id, is_available):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können die Zimmerverfügbarkeit verwalten.")
            return

        session = self.__Session()
        try:
            room = session.execute(select(Room).where(Room.id == room_id)).scalars().one_or_none()
            if room:
                room.is_available = is_available
                session.commit()
                print(f"Verfügbarkeit des Zimmers mit ID '{room_id}' erfolgreich aktualisiert.")
            else:
                print(f"Zimmer mit ID '{room_id}' nicht gefunden.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Aktualisieren der Zimmerverfügbarkeit: {e}")
        finally:
            session.close()

    def update_room_price(self, room_id, price):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können Zimmerpreise aktualisieren.")
            return

        session = self.__Session()
        try:
            room = session.execute(select(Room).where(Room.id == room_id)).scalars().one_or_none()
            if room:
                room.price = price
                session.commit()
                print(f"Preis des Zimmers mit ID '{room_id}' erfolgreich aktualisiert.")
            else:
                print(f"Zimmer mit ID '{room_id}' nicht gefunden.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Aktualisieren des Zimmerpreises: {e}")
        finally:
            session.close()


class UserManager:
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
        self.username_entry.focus_set()

        tk.Label(self.login_frame, text="Password").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=5)

        self.root.bind('<Return>', lambda event: self.login())

        # Admin Actions Frame
        self.admin_frame = tk.Frame(self.root)
        self.admin_frame.pack(pady=10)

        self.add_hotel_button = tk.Button(self.admin_frame, text="Add Hotel", command=self.add_hotel)
        self.add_hotel_button.grid(row=0, columnspan=2, pady=5)

        self.remove_hotel_button = tk.Button(self.admin_frame, text="Remove Hotel", command=self.remove_hotel)
        self.remove_hotel_button.grid(row=1, columnspan=2, pady=5)

        self.update_hotel_button = tk.Button(self.admin_frame, text="Update Hotel Info", command=self.update_hotel)
        self.update_hotel_button.grid(row=2, columnspan=2, pady=5)

        self.list_bookings_button = tk.Button(self.admin_frame, text="List Bookings", command=self.list_bookings)
        self.list_bookings_button.grid(row=3, columnspan=2, pady=5)

        self.update_booking_button = tk.Button(self.admin_frame, text="Update Booking", command=self.update_booking)
        self.update_booking_button.grid(row=4, columnspan=2, pady=5)

        self.manage_room_availability_button = tk.Button(self.admin_frame, text="Manage Room Availability", command=self.manage_room_availability)
        self.manage_room_availability_button.grid(row=5, columnspan=2, pady=5)

        self.update_room_price_button = tk.Button(self.admin_frame, text="Update Room Price", command=self.update_room_price)
        self.update_room_price_button.grid(row=6, columnspan=2, pady=5)

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=7, columnspan=2, pady=5)

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

    def remove_hotel(self):
        if self.user_manager.is_admin():
            hotel_window = tk.Toplevel(self.root)
            hotel_window.title("Remove Hotel")

            tk.Label(hotel_window, text="Hotel ID").grid(row=0, column=0, padx=5, pady=5)
            hotel_id_entry = tk.Entry(hotel_window)
            hotel_id_entry.grid(row=0, column=1, padx=5, pady=5)

            def submit_removal():
                hotel_id = int(hotel_id_entry.get())
                self.inventory_manager.remove_hotel(hotel_id)
                hotel_window.destroy()

            submit_button = tk.Button(hotel_window, text="Submit", command=submit_removal)
            submit_button.grid(row=1, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can remove hotels.")

    def update_hotel(self):
        if self.user_manager.is_admin():
            hotel_window = tk.Toplevel(self.root)
            hotel_window.title("Update Hotel Info")

            tk.Label(hotel_window, text="Hotel ID").grid(row=0, column=0, padx=5, pady=5)
            hotel_id_entry = tk.Entry(hotel_window)
            hotel_id_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(hotel_window, text="New Name (optional)").grid(row=1, column=0, padx=5, pady=5)
            name_entry = tk.Entry(hotel_window)
            name_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(hotel_window, text="New Stars (1-5, optional)").grid(row=2, column=0, padx=5, pady=5)
            stars_entry = tk.Entry(hotel_window)
            stars_entry.grid(row=2, column=1, padx=5, pady=5)

            tk.Label(hotel_window, text="New Address ID (optional)").grid(row=3, column=0, padx=5, pady=5)
            address_id_entry = tk.Entry(hotel_window)
            address_id_entry.grid(row=3, column=1, padx=5, pady=5)

            def submit_update():
                hotel_id = int(hotel_id_entry.get())
                name = name_entry.get() if name_entry.get() else None
                stars = int(stars_entry.get()) if stars_entry.get() else None
                address_id = int(address_id_entry.get()) if address_id_entry.get() else None
                self.inventory_manager.update_hotel_info(hotel_id, name=name, stars=stars, address_id=address_id)
                hotel_window.destroy()

            submit_button = tk.Button(hotel_window, text="Submit", command=submit_update)
            submit_button.grid(row=4, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can update hotel info.")

    def list_bookings(self):
        if self.user_manager.is_admin():
            bookings = self.inventory_manager.list_bookings()
            booking_window = tk.Toplevel(self.root)
            booking_window.title("Bookings")

            for i, booking in enumerate(bookings):
                tk.Label(booking_window, text=f"Booking ID: {booking.id}, Guest ID: {booking.guest_id}, Room ID: {booking.room_hotel_id}, start_date: {booking.start_date}, end_date: {booking.end_date}").pack()

        else:
            messagebox.showerror("Error", "Only administrators can view bookings.")

    def update_booking(self):
        if self.user_manager.is_admin():
            booking_window = tk.Toplevel(self.root)
            booking_window.title("Update Booking")

            tk.Label(booking_window, text="Booking ID").grid(row=0, column=0, padx=5, pady=5)
            booking_id_entry = tk.Entry(booking_window)
            booking_id_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(booking_window, text="New Guest ID (optional)").grid(row=1, column=0, padx=5, pady=5)
            guest_id_entry = tk.Entry(booking_window)
            guest_id_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(booking_window, text="New Room ID (optional)").grid(row=2, column=0, padx=5, pady=5)
            room_id_entry = tk.Entry(booking_window)
            room_id_entry.grid(row=2, column=1, padx=5, pady=5)

            tk.Label(booking_window, text="New Status (optional)").grid(row=3, column=0, padx=5, pady=5)
            status_entry = tk.Entry(booking_window)
            status_entry.grid(row=3, column=1, padx=5, pady=5)

            def submit_update():
                booking_id = int(booking_id_entry.get())
                updates = {}
                if guest_id_entry.get():
                    updates['guest_id'] = int(guest_id_entry.get())
                if room_id_entry.get():
                    updates['room_id'] = int(room_id_entry.get())
                if status_entry.get():
                    updates['status'] = status_entry.get()
                self.inventory_manager.update_booking_info(booking_id, **updates)
                booking_window.destroy()

            submit_button = tk.Button(booking_window, text="Submit", command=submit_update)
            submit_button.grid(row=4, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can update bookings.")

    def manage_room_availability(self):
        if self.user_manager.is_admin():
            room_window = tk.Toplevel(self.root)
            room_window.title("Manage Room Availability")

            tk.Label(room_window, text="Room ID").grid(row=0, column=0, padx=5, pady=5)
            room_id_entry = tk.Entry(room_window)
            room_id_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(room_window, text="Is Available (True/False)").grid(row=1, column=0, padx=5, pady=5)
            is_available_entry = tk.Entry(room_window)
            is_available_entry.grid(row=1, column=1, padx=5, pady=5)

            def submit_availability():
                room_id = int(room_id_entry.get())
                is_available = is_available_entry.get().lower() == 'true'
                self.inventory_manager.manage_room_availability(room_id, is_available)
                room_window.destroy()

            submit_button = tk.Button(room_window, text="Submit", command=submit_availability)
            submit_button.grid(row=2, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can manage room availability.")

    def update_room_price(self):
        if self.user_manager.is_admin():
            price_window = tk.Toplevel(self.root)
            price_window.title("Update Room Price")

            tk.Label(price_window, text="Room ID").grid(row=0, column=0, padx=5, pady=5)
            room_id_entry = tk.Entry(price_window)
            room_id_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(price_window, text="New Price").grid(row=1, column=0, padx=5, pady=5)
            price_entry = tk.Entry(price_window)
            price_entry.grid(row=1, column=1, padx=5, pady=5)

            def submit_price():
                room_id = int(room_id_entry.get())
                price = float(price_entry.get())
                self.inventory_manager.update_room_price(room_id, price)
                price_window.destroy()

            submit_button = tk.Button(price_window, text="Submit", command=submit_price)
            submit_button.grid(row=2, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can update room prices.")


if __name__ == "__main__":
    db_file = "../data/database.db"
    inventory_manager = InventoryManager(db_file)

    root = tk.Tk()
    app = App(root, inventory_manager)
    root.mainloop()
