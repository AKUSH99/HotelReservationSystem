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
        HotelAlias = aliased(Hotel, name='hotel_alias')
        AddressAlias = aliased(Address, name='address_alias')
        RoomAlias = aliased(Room, name='room_alias')
        BookingAlias = aliased(Booking, name='booking_alias')

        query = select(HotelAlias).distinct()

        if stars is not None:
            query = query.where(HotelAlias.stars >= stars)
        if city is not None:
            query = query.join(AddressAlias).where(func.lower(AddressAlias.city) == city.lower())

        if start_date and end_date:
            subquery_booked_rooms = select(RoomAlias.id).join(BookingAlias).where(
                or_(
                    BookingAlias.start_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                    BookingAlias.end_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                )
            )
            available_rooms_query = select(RoomAlias).join(HotelAlias).where(
                not_(RoomAlias.id.in_(subquery_booked_rooms)))
        else:
            available_rooms_query = select(RoomAlias).join(HotelAlias)

        if max_guest != 1:
            available_rooms_query = available_rooms_query.where(RoomAlias.max_guests >= max_guest)

        if city is not None:
            available_rooms_query = available_rooms_query.join(AddressAlias).where(
                func.lower(AddressAlias.city) == city.lower())
        if stars is not None:
            available_rooms_query = available_rooms_query.where(HotelAlias.stars >= stars)

        available_rooms = self._session.execute(available_rooms_query).scalars().all()
        hotel_ids_with_available_rooms = {room.hotel_id for room in available_rooms}

        if hotel_ids_with_available_rooms:
            query = query.where(HotelAlias.id.in_(hotel_ids_with_available_rooms))

        hotels_with_available_rooms = self._session.execute(query).scalars().all()

        return hotels_with_available_rooms

    def search_rooms_by_availability(self, start_date: datetime, end_date: datetime, hotel: Hotel = None):
        query = select(Room)
        if hotel is not None:
            query = query.where(Room.hotel_id == hotel.id)

        query_booked_rooms = select(Room.id).join(Booking).where(
            or_(
                Booking.start_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                Booking.end_date.between(start_date, end_date)
            )
        )
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


class HotelReservationApp(tk.Tk):
    def __init__(self, search_manager):
        super().__init__()
        self.search_manager = search_manager
        self.title("Hotel Reservation System")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Frame für die Sucheinstellungen
        self.search_frame = ttk.LabelFrame(self, text="Search Hotels")
        self.search_frame.pack(pady=20, padx=20, fill="x")

        ttk.Label(self.search_frame, text="City:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.city_entry = ttk.Entry(self.search_frame)
        self.city_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.search_frame, text="Max Guests:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.guests_entry = ttk.Entry(self.search_frame)
        self.guests_entry.grid(row=0, column=3, padx=10, pady=5)

        ttk.Label(self.search_frame, text="Stars:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.stars_entry = ttk.Entry(self.search_frame)
        self.stars_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.search_frame, text="Start Date (DD.MM.YYYY):").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.start_date_entry = ttk.Entry(self.search_frame)
        self.start_date_entry.grid(row=1, column=3, padx=10, pady=5)

        ttk.Label(self.search_frame, text="End Date (DD.MM.YYYY):").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.end_date_entry = ttk.Entry(self.search_frame)
        self.end_date_entry.grid(row=2, column=3, padx=10, pady=5)

        self.search_button = ttk.Button(self.search_frame, text="Search Hotels", command=self.search_hotels)
        self.search_button.grid(row=3, columnspan=4, pady=10)

        # Frame für die Ergebnisanzeige
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.results_tree = ttk.Treeview(self.results_frame, columns=("ID", "Name", "Stars", "Address"),
                                         show="headings")
        self.results_tree.heading("ID", text="Hotel ID")
        self.results_tree.heading("Name", text="Name")
        self.results_tree.heading("Stars", text="Stars")
        self.results_tree.heading("Address", text="Address")
        self.results_tree.pack(fill="both", expand=True)

        self.results_tree.bind("<Double-1>", self.select_hotel)

    def search_hotels(self):
        city = self.city_entry.get()
        if not city:
            city = None

        max_guest = self.guests_entry.get()
        if not max_guest:
            max_guest = 1
        else:
            max_guest = int(max_guest)

        stars = self.stars_entry.get()
        if not stars:
            stars = None
        else:
            stars = int(stars)

        start_date = self.parse_date(self.start_date_entry.get())
        end_date = self.parse_date(self.end_date_entry.get())

        if (self.start_date_entry.get() and not start_date) or (self.end_date_entry.get() and not end_date):
            messagebox.showerror("Invalid Date", "Please enter valid dates in DD.MM.YYYY format.")
            return

        hotels = self.search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest,
                                                                             stars)
        self.display_hotels(hotels)

    def parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            return None

    def display_hotels(self, hotels):
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)

        for hotel in hotels:
            self.results_tree.insert("", "end", values=(hotel.id, hotel.name, hotel.stars,
                                                        f"{hotel.address.street}, {hotel.address.zip} {hotel.address.city}"))

    def select_hotel(self, event):
        selected_item = self.results_tree.selection()[0]
        hotel_id = self.results_tree.item(selected_item, "values")[0]
        selected_hotel = next((hotel for hotel in self.search_manager.get_all_hotels() if hotel.id == int(hotel_id)),
                              None)

        if selected_hotel:
            self.show_available_rooms(selected_hotel)

    def show_available_rooms(self, hotel):
        start_date = self.parse_date(self.start_date_entry.get())
        end_date = self.parse_date(self.end_date_entry.get())

        if not start_date or not end_date:
            messagebox.showinfo("Missing Dates", "Please enter start and end dates to check room availability.")
            return

        available_rooms = self.search_manager.search_rooms_by_availability(start_date, end_date, hotel)
        if not available_rooms:
            messagebox.showinfo("No Rooms Available", "No available rooms found for the selected hotel and dates.")
        else:
            rooms_window = tk.Toplevel(self)
            rooms_window.title(f"Available Rooms in {hotel.name}")

            tree = ttk.Treeview(rooms_window, columns=("ID", "Number", "Max Guests", "Description"), show="headings")
            tree.heading("ID", text="Room ID")
            tree.heading("Number", text="Room Number")
            tree.heading("Max Guests", text="Max Guests")
            tree.heading("Description", text="Description")
            tree.pack(fill="both", expand=True)

            for room in available_rooms:
                tree.insert("", "end", values=(room.id, room.number, room.max_guests, room.description))


if __name__ == "__main__":
    db_file = "../data/database.db"
    database_path = Path('../data/database.db')
    if not database_path.is_file():
        init_db(str(database_path), generate_example_data=True)
    engine = create_engine(f"sqlite:///{database_path}", echo=False)

    session = scoped_session(sessionmaker(bind=engine))
    search_manager = SearchManager(session)

    app = HotelReservationApp(search_manager)
    app.mainloop()
