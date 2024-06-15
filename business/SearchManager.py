from pathlib import Path
from sqlalchemy import create_engine, select, func, and_, or_, not_
from sqlalchemy.orm import sessionmaker, scoped_session, aliased
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from data_models.models import *
from data_access.data_base import init_db


class SearchManager:
    def __init__(self, session):
        self._session = session

    def search_hotels_by_city_date_guests_stars(self, city=None, start_date=None, end_date=None, max_guest=1,
                                                stars=None):
        # Aliase für die Tabellen
        HotelAlias = aliased(Hotel, name='hotel_alias')
        AddressAlias = aliased(Address, name='address_alias')
        RoomAlias = aliased(Room, name='room_alias')
        BookingAlias = aliased(Booking, name='booking_alias')

        # Hauptabfrage für Hotels
        query = select(HotelAlias).distinct()

        if stars is not None:
            query = query.where(HotelAlias.stars >= stars)
        if city is not None:
            query = query.join(AddressAlias).where(func.lower(AddressAlias.city) == city.lower())

        if start_date is not None:
            # Subquery für gebuchte Räume
            subquery_booked_rooms = select(RoomAlias.id).join(BookingAlias).where(
                or_(
                    BookingAlias.start_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                    BookingAlias.end_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                    and_(BookingAlias.start_date < start_date, BookingAlias.end_date > end_date)
                )
            )
        else:
            subquery_booked_rooms = select(RoomAlias.id).join(BookingAlias).where(RoomAlias.id == 998877665544)

        # Hauptabfrage für verfügbare Räume
        available_rooms_query = select(RoomAlias).join(HotelAlias).where(not_(RoomAlias.id.in_(subquery_booked_rooms)))

        if max_guest != 1:
            available_rooms_query = available_rooms_query.where(RoomAlias.max_guests >= max_guest)

        if city is not None:
            available_rooms_query = available_rooms_query.join(AddressAlias).where(
                func.lower(AddressAlias.city) == city.lower())
        if stars is not None:
            available_rooms_query = available_rooms_query.where(HotelAlias.stars >= stars)

        # Execute the query and get available rooms
        available_rooms = self._session.execute(available_rooms_query).scalars().all()

        # Get unique hotels with available rooms
        hotel_ids_with_available_rooms = {room.hotel_id for room in available_rooms}

        # Filter the hotels query to only include hotels with available rooms
        if hotel_ids_with_available_rooms:
            query = query.where(HotelAlias.id.in_(hotel_ids_with_available_rooms))

        # Execute the query and return the results
        hotels_with_available_rooms = self._session.execute(query).scalars().all()

        for h in hotels_with_available_rooms:
            print(f"ID: {h.id} - {h.name} - {h.stars} Sterne - {h.address.street}, {h.address.zip} {h.address.city}")

        return hotels_with_available_rooms

    def search_hotels_by_city_guests_stars_wo_avlblty(self, city=None, max_guest=1,
                                                stars=None):

        # Hauptabfrage für Hotels
        query = select(Hotel).distinct()

        if stars is not None:
            query = query.where(Hotel.stars >= stars)
        if city is not None:
            query = query.join(Address).where(func.lower(Address.city) == city.lower())

        if max_guest != 1:
            query = query.join(Room).where(Room.max_guests >= max_guest)

        hotels_with_matching_rooms = self._session.execute(query).scalars().all()

        # Eindeutige hotel_ids extrahieren
        distinct_hotel_ids = list(set(hotels_with_matching_rooms))

        # Ergebnisse anzeigen
        for h in distinct_hotel_ids:
            print(f"ID: {h.id} - {h.name} - {h.stars} Sterne - {h.address.street}, {h.address.zip} {h.address.city}")
        return distinct_hotel_ids

    def search_rooms_by_availability(self, start_date: datetime, end_date: datetime, hotel: Hotel = None):
        query = select(Room)
        if hotel is not None:
            query = query.where(Room.hotel_id == hotel.id)

        if start_date is not None:
            query_booked_rooms = select(Room.id).join(Booking).where(
                or_(
                    Booking.start_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                    Booking.end_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                    and_(Booking.start_date < start_date, Booking.end_date > end_date)
                )
            )
        else:
            query_booked_rooms = select(Room.id).join(Booking).where(Room.id == 998877665544)
        if hotel is not None:
            query_booked_rooms = query_booked_rooms.where(Room.hotel_id == hotel.id)

        query = query.where(Room.id.not_in(query_booked_rooms))
        results = self._session.execute(query).scalars().all()
        return results

    def get_rooms_by_hotel(self, hotel_id, max_guest):
        query = select(
            Room.number,
            Room.type,
            Room.max_guests,
            Room.description,
            Room.amenities,
            Room.price
        ).where(
            and_(
                Room.hotel_id == hotel_id,
                Room.max_guests >= max_guest
            )
        )
        rooms = self._session.execute(query).all()
        return [{
            "Room Number": room[0],
            "Type": room[1],
            "Max Guests": room[2],
            "Description": room[3],
            "Amenities": room[4],
            "Price": room[5]
        } for room in rooms]



    def get_hotels_by_name(self, name):
        query = select(Hotel).where(Hotel.name == name)
        hotels = self._session.execute(query).scalars().all()
        return hotels

    def get_all_hotels(self):
        query = select(Hotel)
        hotels = self._session.execute(query).scalars().all()
        return hotels

# Zum Nutzen ohne GUI: Teil unten auskommentieren und Terminal UI nicht mehr auskommentieren.
class HotelReservationApp(tk.Tk):
    def __init__(self, search_manager):
        super().__init__()
        self.search_manager = search_manager
        self.title("Hotel Reservation")
        self.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Welcome to the hotel search!").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(self, text="City:").grid(row=1, column=0, sticky=tk.E)
        self.city_entry = tk.Entry(self)
        self.city_entry.grid(row=1, column=1)

        tk.Label(self, text="Number of guests:").grid(row=2, column=0, sticky=tk.E)
        self.guests_entry = tk.Entry(self)
        self.guests_entry.grid(row=2, column=1)

        tk.Label(self, text="Number of stars:").grid(row=3, column=0, sticky=tk.E)
        self.stars_entry = tk.Entry(self)
        self.stars_entry.grid(row=3, column=1)

        tk.Label(self, text="Start date (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.E)
        self.start_date_entry = tk.Entry(self)
        self.start_date_entry.grid(row=4, column=1)

        tk.Label(self, text="End date (YYYY-MM-DD):").grid(row=5, column=0, sticky=tk.E)
        self.end_date_entry = tk.Entry(self)
        self.end_date_entry.grid(row=5, column=1)

        self.search_button = tk.Button(self, text="Search Hotels", command=self.search_hotels)
        self.search_button.grid(row=6, column=0, columnspan=2, pady=10)

    def search_hotels(self):
        city = self.city_entry.get() or None
        max_guest = self.guests_entry.get()
        max_guest = int(max_guest) if max_guest else 1
        stars = self.stars_entry.get()
        stars = int(stars) if stars else None
        start_date = self.get_valid_date(self.start_date_entry.get())
        end_date = self.get_valid_date(self.end_date_entry.get())

        # Remove the requirement for start_date and end_date
        # if not (start_date and end_date):
        #     messagebox.showerror("Invalid date", "Please enter valid start and end dates in YYYY-MM-DD format.")
        #     return

        hotels = self.search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
        if not hotels:
            messagebox.showinfo("No results", "No hotels found for your criteria.")
            return

        self.show_hotels(hotels, start_date, end_date)

    def get_valid_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

    def show_hotels(self, hotels, start_date, end_date):
        self.hotels_window = tk.Toplevel(self)
        self.hotels_window.title("Select a Hotel")
        self.hotels_window.geometry("600x400")

        tk.Label(self.hotels_window, text="Please select a hotel by ID:").grid(row=0, column=0, columnspan=2, pady=10)

        for i, hotel in enumerate(hotels):
            tk.Label(self.hotels_window, text=f"ID: {hotel.id} - {hotel.name}").grid(row=i+1, column=0, sticky=tk.W)

        self.hotel_id_entry = tk.Entry(self.hotels_window)
        self.hotel_id_entry.grid(row=i+2, column=0)
        self.select_hotel_button = tk.Button(self.hotels_window, text="Select Hotel", command=lambda: self.select_hotel(hotels, start_date, end_date))
        self.select_hotel_button.grid(row=i+2, column=1)

    def select_hotel(self, hotels, start_date, end_date):
        hotel_id = int(self.hotel_id_entry.get())
        selected_hotel = next((hotel for hotel in hotels if hotel.id == hotel_id), None)
        if not selected_hotel:
            messagebox.showerror("Invalid ID", "Invalid hotel ID.")
            return

        self.show_rooms(selected_hotel, start_date, end_date)

    def show_rooms(self, hotel, start_date, end_date):
        available_rooms = self.search_manager.search_rooms_by_availability(start_date, end_date, hotel)
        if not available_rooms:
            messagebox.showinfo("No results", "No available rooms found.")
            return

        self.rooms_window = tk.Toplevel(self)
        self.rooms_window.title("Select a Room")
        self.rooms_window.geometry("600x400")

        tk.Label(self.rooms_window, text=f"Rooms available in {hotel.name}:").grid(row=0, column=0, columnspan=2, pady=10)

        for i, room in enumerate(available_rooms):
            tk.Label(self.rooms_window, text=f"ID: {room.id} - {room.number} - {room.max_guests} guests - {room.description}").grid(row=i+1, column=0, sticky=tk.W)

        self.room_id_entry = tk.Entry(self.rooms_window)
        self.room_id_entry.grid(row=i+2, column=0)
        self.select_room_button = tk.Button(self.rooms_window, text="Select Room", command=lambda: self.select_room(available_rooms))
        self.select_room_button.grid(row=i+2, column=1)

    def select_room(self, rooms):
        room_id = int(self.room_id_entry.get())
        selected_room = next((room for room in rooms if room.id == room_id), None)
        if not selected_room:
            messagebox.showerror("Invalid ID", "Invalid room ID.")
            return

        messagebox.showinfo("Room Selected", f"Selected Room: {selected_room.hotel.name} - ID {selected_room.id} - Room number {selected_room.number} - {selected_room.max_guests} guests - {selected_room.description}")

if __name__ == "__main__":
    db_file = "../data/database.db"
    database_path = Path(db_file)
    if not database_path.is_file():
        init_db(str(database_path), generate_example_data=True)
    engine = create_engine(f"sqlite:///{database_path}", echo=False)
    session = scoped_session(sessionmaker(bind=engine))
    search_manager = SearchManager(session)

    app = HotelReservationApp(search_manager)
    app.mainloop()


# if __name__ == "__main__":
#     db_file = "../data/database.db"
#         # Initialisierung der Datenbankverbindung
#     database_path = Path('../data/database.db')
#     if not database_path.is_file():
#         init_db(str(database_path), generate_example_data=True)
#     engine = create_engine(f"sqlite:///{database_path}", echo=False)
#
#     session = scoped_session(sessionmaker(bind=engine))
#     search_manager = SearchManager(session)
#
#     # app = HotelReservationApp(search_manager)
#     # app.mainloop()
#
#     def get_valid_date(prompt):
#         while True:
#             date_str = input(prompt)
#             if not date_str:  # Überprüfung, ob die Eingabe leer ist
#                 return None  # Rückgabe von None, wenn die Eingabe leer ist
#             try:
#                 return datetime.strptime(date_str, "%Y-%m-%d")
#             except ValueError:
#                 print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
#
# #Terminal UI (zum Aktivieren auskommentieren rückgängig machen):
#     print("Welcome to the hotel search!")
#
#     print("Please enter the desired attributes.")
#     city = input("City: ")
#     if city == "":
#         city = None
#     max_guest = input("Number of guests: ")
#     if max_guest == "":
#         max_guest = 1
#     else:
#         max_guest = int(max_guest)
#     stars = input("Number of stars: ")
#     if stars == "":
#         stars = None
#     else:
#         stars = int(stars)
#
#     start_date = get_valid_date("Start date (YYYY-MM-DD): ")
#     end_date = get_valid_date("End date (YYYY-MM-DD): ")
#
#     print(f"Searching for hotels in {city} for {max_guest} guests with {stars} stars from {start_date} to {end_date}.")
#
#     hotels = search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
#     if not hotels:
#         print("No hotels found for your criteria.")
#         exit()
#
#     print("Please select a hotel by ID:")
#     hotel_id = int(input("Hotel ID: "))
#     selected_hotel = next((hotel for hotel in hotels if hotel.id == hotel_id), None)
#     if not selected_hotel:
#         print("Invalid hotel ID.")
#         exit()
#
#     print(f"Searching for available rooms in {selected_hotel.name} from {start_date} to {end_date}.")
#     available_rooms = search_manager.search_rooms_by_availability(start_date, end_date, selected_hotel)
#     if not available_rooms:
#         print("No available rooms found.")
#     else:
#         for room in available_rooms:
#             print(f"Room ID: {room.id} - {room.number} - {room.max_guests} guests - {room.description}")
#
#         print("Please select a room by ID:")
#         room_id = int(input("Room ID: "))
#         selected_room = next((room for room in available_rooms if room.id == room_id), None)
#         if not selected_room:
#             print("Invalid room ID.")
#         else:
#             print(
#                 f"Selected Room: {selected_room.hotel.name} - ID {selected_room.id} - Room number {selected_room.number} - {selected_room.max_guests} guests - {selected_room.description}")