import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from data_access.data_base import init_db
from data_models.models import Login, Role, RegisteredGuest, Address, Guest, Hotel, Booking, Room
import datetime


class InventoryManager:
    def __init__(self, session):
        self._session = session
        self.user_manager = UserManager(self._session)

    def add_hotel(self, name, stars, street, zip_code, city):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können neue Hotels hinzufügen.")
            return

        session = self._session()
        try:
            # Check if the address already exists
            address = session.query(Address).filter_by(street=street, zip=zip_code, city=city).first()

            # If the address doesn't exist, create a new one
            if not address:
                new_address = Address(street=street, zip=zip_code, city=city)
                session.add(new_address)
                session.commit()
                address_id = new_address.id
            else:
                address_id = address.id

            # Add the new hotel with the address ID
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

        session = self._session()
        try:
            session.execute(delete(Hotel).where(Hotel.id == hotel_id))
            session.commit()
            print(f"Hotel mit ID '{hotel_id}' erfolgreich entfernt.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Entfernen des Hotels: {e}")
        finally:
            session.close()

    def update_hotel_info(self, hotel_id, name=None, stars=None, street=None, zip_code=None, city=None):
        if not self.user_manager.is_admin():
            print("Nur Administratoren können Hotelinformationen aktualisieren.")
            return

        session = self._session()
        try:
            hotel = session.execute(select(Hotel).where(Hotel.id == hotel_id)).scalars().one_or_none()
            if hotel:
                if name:
                    hotel.name = name
                if stars:
                    hotel.stars = stars
                if street and zip_code and city:
                    # Check if the new address already exists
                    address = session.query(Address).filter_by(street=street, zip=zip_code, city=city).first()

                    # If the address doesn't exist, create a new one
                    if not address:
                        new_address = Address(street=street, zip=zip_code, city=city)
                        session.add(new_address)
                        session.commit()
                        address_id = new_address.id
                    else:
                        address_id = address.id

                    # Assign the new address to the hotel
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

        session = self._session()
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

        session = self._session()
        try:
            booking = session.execute(select(Booking).where(Booking.id == booking_id)).scalars().one_or_none()
            if booking:
                if 'start_date' in kwargs:
                    booking.start_date = kwargs['start_date']  # Use date object directly
                if 'end_date' in kwargs:
                    booking.end_date = kwargs['end_date']  # Use date object directly
                if 'guest_id' in kwargs:
                    booking.guest_id = kwargs['guest_id']
                if 'room_id' in kwargs:
                    booking.room_id = kwargs['room_id']
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

        session = self._session()
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

        session = self._session()
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
                query = select(Login).options(joinedload(Login.role)).where(Login.username == username).where(Login.password == password)
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

        self.style = ttk.Style()
        self.style.theme_use('clam')  # Optionally change the theme to 'clam', 'alt', or another ttk theme
        self.style.configure('TLabel', padding=5, font=('Arial', 10))
        self.style.configure('TButton', padding=5, font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', padding=5, font=('Arial', 10))

        self.create_widgets()

    def create_widgets(self):
        # Login Frame
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(pady=20, padx=20)

        ttk.Label(self.login_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.username_entry.focus_set()

        ttk.Label(self.login_frame, text="Password").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2, pady=20)

        self.root.bind('<Return>', lambda event: self.login())

        # Admin Actions Frame
        self.admin_frame = ttk.Frame(self.root)

        self.add_hotel_button = ttk.Button(self.admin_frame, text="Add Hotel", command=self.add_hotel)
        self.add_hotel_button.grid(row=0, columnspan=2, pady=5, padx=5)

        self.remove_hotel_button = ttk.Button(self.admin_frame, text="Remove Hotel", command=self.remove_hotel)
        self.remove_hotel_button.grid(row=1, columnspan=2, pady=5, padx=5)

        self.update_hotel_button = ttk.Button(self.admin_frame, text="Update Hotel Info", command=self.update_hotel)
        self.update_hotel_button.grid(row=2, columnspan=2, pady=5, padx=5)

        self.list_bookings_button = ttk.Button(self.admin_frame, text="List Bookings", command=self.list_bookings)
        self.list_bookings_button.grid(row=3, columnspan=2, pady=5, padx=5)

        self.update_booking_button = ttk.Button(self.admin_frame, text="Update Booking", command=self.update_booking)
        self.update_booking_button.grid(row=4, columnspan=2, pady=5, padx=5)

        self.manage_room_availability_button = ttk.Button(self.admin_frame, text="Manage Room Availability", command=self.manage_room_availability)
        self.manage_room_availability_button.grid(row=5, columnspan=2, pady=5, padx=5)

        self.update_room_price_button = ttk.Button(self.admin_frame, text="Update Room Price", command=self.update_room_price)
        self.update_room_price_button.grid(row=6, columnspan=2, pady=5, padx=5)

        self.logout_button = ttk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=7, columnspan=2, pady=20, padx=5)

        self.admin_frame.pack_forget()  # Hide admin actions initially

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.user_manager.login(username, password):
            messagebox.showinfo("Login", "Login successful!")
            self.login_frame.pack_forget()
            self.admin_frame.pack(pady=20, padx=20)
        else:
            messagebox.showerror("Login", "Login failed! Try again.")

    def logout(self):
        self.user_manager.logout()
        self.admin_frame.pack_forget()
        self.login_frame.pack(pady=20, padx=20)
        messagebox.showinfo("Logout", "Logged out successfully!")

    def add_hotel(self):
        if self.user_manager.is_admin():
            hotel_window = tk.Toplevel(self.root)
            hotel_window.title("Add Hotel")

            ttk.Label(hotel_window, text="Hotel Name").grid(row=0, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(hotel_window)
            name_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="Stars (1-5)").grid(row=1, column=0, padx=5, pady=5)
            stars_entry = ttk.Entry(hotel_window)
            stars_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="Street").grid(row=2, column=0, padx=5, pady=5)
            street_entry = ttk.Entry(hotel_window)
            street_entry.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="ZIP Code").grid(row=3, column=0, padx=5, pady=5)
            zip_entry = ttk.Entry(hotel_window)
            zip_entry.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="City").grid(row=4, column=0, padx=5, pady=5)
            city_entry = ttk.Entry(hotel_window)
            city_entry.grid(row=4, column=1, padx=5, pady=5)

            def submit_hotel():
                name = name_entry.get()
                stars = int(stars_entry.get())
                street = street_entry.get()
                zip_code = zip_entry.get()
                city = city_entry.get()
                self.inventory_manager.add_hotel(name, stars, street, zip_code, city)
                hotel_window.destroy()

            submit_button = ttk.Button(hotel_window, text="Submit", command=submit_hotel)
            submit_button.grid(row=5, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can add new hotels.")

    def remove_hotel(self):
        if self.user_manager.is_admin():
            hotel_window = tk.Toplevel(self.root)
            hotel_window.title("Remove Hotel")

            ttk.Label(hotel_window, text="Hotel ID").grid(row=0, column=0, padx=5, pady=5)
            hotel_id_entry = ttk.Entry(hotel_window)
            hotel_id_entry.grid(row=0, column=1, padx=5, pady=5)

            def submit_removal():
                hotel_id = int(hotel_id_entry.get())
                self.inventory_manager.remove_hotel(hotel_id)
                hotel_window.destroy()

            submit_button = ttk.Button(hotel_window, text="Submit", command=submit_removal)
            submit_button.grid(row=1, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can remove hotels.")

    def update_hotel(self):
        if self.user_manager.is_admin():
            hotel_window = tk.Toplevel(self.root)
            hotel_window.title("Update Hotel Info")

            ttk.Label(hotel_window, text="Hotel ID").grid(row=0, column=0, padx=5, pady=5)
            hotel_id_entry = ttk.Entry(hotel_window)
            hotel_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="New Name (optional)").grid(row=1, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(hotel_window)
            name_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="New Stars (1-5, optional)").grid(row=2, column=0, padx=5, pady=5)
            stars_entry = ttk.Entry(hotel_window)
            stars_entry.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="New Street (optional)").grid(row=3, column=0, padx=5, pady=5)
            street_entry = ttk.Entry(hotel_window)
            street_entry.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="New ZIP Code (optional)").grid(row=4, column=0, padx=5, pady=5)
            zip_entry = ttk.Entry(hotel_window)
            zip_entry.grid(row=4, column=1, padx=5, pady=5)

            ttk.Label(hotel_window, text="New City (optional)").grid(row=5, column=0, padx=5, pady=5)
            city_entry = ttk.Entry(hotel_window)
            city_entry.grid(row=5, column=1, padx=5, pady=5)

            def submit_update():
                hotel_id = int(hotel_id_entry.get())
                name = name_entry.get() if name_entry.get() else None
                stars = int(stars_entry.get()) if stars_entry.get() else None
                street = street_entry.get() if street_entry.get() else None
                zip_code = zip_entry.get() if zip_entry.get() else None
                city = city_entry.get() if city_entry.get() else None

                self.inventory_manager.update_hotel_info(
                    hotel_id, name=name, stars=stars, street=street, zip_code=zip_code, city=city
                )
                hotel_window.destroy()

            submit_button = ttk.Button(hotel_window, text="Submit", command=submit_update)
            submit_button.grid(row=6, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can update hotel info.")

    def list_bookings(self):
        if self.user_manager.is_admin():
            bookings = self.inventory_manager.list_bookings()
            booking_window = tk.Toplevel(self.root)
            booking_window.title("Bookings")

            booking_list = ttk.Treeview(booking_window, columns=("ID", "Guest ID", "Room ID", "Date", "Status"), show='headings')
            booking_list.heading("ID", text="Booking ID")
            booking_list.heading("Guest ID", text="Guest ID")
            booking_list.heading("Room ID", text="Room ID")
            booking_list.heading("Date", text="Date")
            booking_list.heading("Status", text="Status")

            for booking in bookings:
                booking_list.insert('', 'end', values=(booking.id, booking.guest_id, booking.room_hotel_id, booking.start_date, booking.end_date))

            booking_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        else:
            messagebox.showerror("Error", "Only administrators can view bookings.")

    def update_booking(self):
        if self.user_manager.is_admin():
            booking_window = tk.Toplevel(self.root)
            booking_window.title("Update Booking")

            ttk.Label(booking_window, text="Booking ID").grid(row=0, column=0, padx=5, pady=5)
            booking_id_entry = ttk.Entry(booking_window)
            booking_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(booking_window, text="New Guest ID (optional)").grid(row=1, column=0, padx=5, pady=5)
            guest_id_entry = ttk.Entry(booking_window)
            guest_id_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(booking_window, text="New Room ID (optional)").grid(row=2, column=0, padx=5, pady=5)
            room_id_entry = ttk.Entry(booking_window)
            room_id_entry.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(booking_window, text="New Start Date (DD.MM.YYYY, optional)").grid(row=3, column=0, padx=5,
                                                                                         pady=5)
            start_date_entry = ttk.Entry(booking_window)
            start_date_entry.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(booking_window, text="New End Date (DD.MM.YYYY, optional)").grid(row=4, column=0, padx=5, pady=5)
            end_date_entry = ttk.Entry(booking_window)
            end_date_entry.grid(row=4, column=1, padx=5, pady=5)

            def submit_update():
                booking_id = int(booking_id_entry.get())
                updates = {}
                if guest_id_entry.get():
                    updates['guest_id'] = int(guest_id_entry.get())
                if room_id_entry.get():
                    updates['room_id'] = int(room_id_entry.get())
                if start_date_entry.get():
                    try:
                        start_date = datetime.datetime.strptime(start_date_entry.get(), "%d.%m.%Y").date()
                        updates['start_date'] = start_date
                    except ValueError:
                        messagebox.showerror("Error", "Invalid Start Date format. Please use DD.MM.YYYY.")
                        return
                if end_date_entry.get():
                    try:
                        end_date = datetime.datetime.strptime(end_date_entry.get(), "%d.%m.%Y").date()
                        updates['end_date'] = end_date
                    except ValueError:
                        messagebox.showerror("Error", "Invalid End Date format. Please use DD.MM.YYYY.")
                        return
                self.inventory_manager.update_booking_info(booking_id, **updates)
                booking_window.destroy()

            submit_button = ttk.Button(booking_window, text="Submit", command=submit_update)
            submit_button.grid(row=5, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can update bookings.")

    def manage_room_availability(self):
        if self.user_manager.is_admin():
            room_window = tk.Toplevel(self.root)
            room_window.title("Manage Room Availability")

            ttk.Label(room_window, text="Room ID").grid(row=0, column=0, padx=5, pady=5)
            room_id_entry = ttk.Entry(room_window)
            room_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(room_window, text="Is Available (True/False)").grid(row=1, column=0, padx=5, pady=5)
            is_available_entry = ttk.Entry(room_window)
            is_available_entry.grid(row=1, column=1, padx=5, pady=5)

            def submit_availability():
                room_id = int(room_id_entry.get())
                is_available = is_available_entry.get().lower() == 'true'
                self.inventory_manager.manage_room_availability(room_id, is_available)
                room_window.destroy()

            submit_button = ttk.Button(room_window, text="Submit", command=submit_availability)
            submit_button.grid(row=2, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can manage room availability.")

    def update_room_price(self):
        if self.user_manager.is_admin():
            price_window = tk.Toplevel(self.root)
            price_window.title("Update Room Price")

            ttk.Label(price_window, text="Room ID").grid(row=0, column=0, padx=5, pady=5)
            room_id_entry = ttk.Entry(price_window)
            room_id_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(price_window, text="New Price").grid(row=1, column=0, padx=5, pady=5)
            price_entry = ttk.Entry(price_window)
            price_entry.grid(row=1, column=1, padx=5, pady=5)

            def submit_price():
                room_id = int(room_id_entry.get())
                price = float(price_entry.get())
                self.inventory_manager.update_room_price(room_id, price)
                price_window.destroy()

            submit_button = ttk.Button(price_window, text="Submit", command=submit_price)
            submit_button.grid(row=2, columnspan=2, pady=10)

        else:
            messagebox.showerror("Error", "Only administrators can update room prices.")


if __name__ == "__main__":
    db_file = "../data/database.db"
    # Initialisierung der Datenbankverbindung
    database_path = Path('../data/database.db')
    if not database_path.is_file():
        init_db(str(database_path), generate_example_data=True)
    engine = create_engine(f"sqlite:///{database_path}", echo=False)

    session = scoped_session(sessionmaker(bind=engine))
    inventory_manager = InventoryManager(session)

    root = tk.Tk()
    app = App(root, inventory_manager)
    root.mainloop()
