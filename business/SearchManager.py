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

        # Subquery für gebuchte Räume
        subquery_booked_rooms = select(RoomAlias.id).join(BookingAlias).where(
            or_(
                BookingAlias.start_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                BookingAlias.end_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                and_(BookingAlias.start_date < start_date, BookingAlias.end_date > end_date)
            )
        )

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

    def search_hotels_by_city_guests_stars_wo_avlblty(self, city=None, max_guest=1, stars=None):

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

        query_booked_rooms = select(Room.id).join(Booking).where(
            or_(
                Booking.start_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                Booking.end_date.between(start_date - timedelta(hours=1), end_date + timedelta(hours=1)),
                and_(Booking.start_date < start_date, Booking.end_date > end_date)
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


if __name__ == "__main__":
    db_file = "../data/database.db"
        # Initialisierung der Datenbankverbindung
    database_path = Path('../data/database.db')
    if not database_path.is_file():
        init_db(str(database_path), generate_example_data=True)
    engine = create_engine(f"sqlite:///{database_path}", echo=False)

    session = scoped_session(sessionmaker(bind=engine))
    search_manager = SearchManager(session)

    # app = HotelReservationApp(search_manager)
    # app.mainloop()

    def get_valid_date(prompt):
        while True:
            date_str = input(prompt)
            if not date_str:  # Überprüfung, ob die Eingabe leer ist
                print("Date cannot be empty. Please enter a valid date.")
                continue
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

#Terminal UI (zum Aktivieren # bei allen Zeilen entfernen):
    print("Welcome to the hotel search!")
    choice_1 = input("Would you like to check availability of hotels (otherwise all "
                     "matching hotels will be shown)? (Y/N)")

    if choice_1.lower() == "n" or choice_1.lower() == "no" or choice_1.lower() == "nein":
        print("You chose to look at hotels regardless of availability.")
        print("Please enter the desired attributes.")
        city = input("City: ")
        if city == "":
            city = None
        max_guest = input("Number of guests: ")
        if max_guest == "":
            max_guest = 1
        else:
            max_guest = int(max_guest)
        stars = input("Number of stars: ")
        if stars == "":
            stars = None
        else:
            stars = int(stars)

        matching_hotels = search_manager.search_hotels_by_city_guests_stars_wo_avlblty(city, max_guest, stars)
        if not matching_hotels:
            print("No hotels found for your criteria.")
            exit()

        print("Please select a hotel by ID:")
        hotel_id = int(input("Hotel ID: "))
        selected_hotel = next((hotel for hotel in matching_hotels if hotel.id == hotel_id), None)
        if not selected_hotel:
            print("Invalid hotel ID.")
            exit()

        print(f"Searching for matching rooms in {selected_hotel.name}.")
        start_date = datetime(2099, 12, 30)
        end_date = datetime(2099, 12, 31)
        matching_rooms = search_manager.search_rooms_by_availability(start_date, end_date, selected_hotel)
        if not matching_rooms:
            print("No matching rooms found.")
        else:
            for room in matching_rooms:
                print(f"Room ID: {room.id} - {room.number} - {room.max_guests} guests - {room.description}")

    else:
        print("You chose to search for available hotel rooms.")
        print("Please enter the desired attributes.")
        city = input("City: ")
        if city == "":
            city = None
        max_guest = input("Number of guests: ")
        if max_guest == "":
            max_guest = 1
        else:
            max_guest = int(max_guest)
        stars = input("Number of stars: ")
        if stars == "":
            stars = None
        else:
            stars = int(stars)

        start_date = get_valid_date("Start date (YYYY-MM-DD): ")
        end_date = get_valid_date("End date (YYYY-MM-DD): ")

        print(f"Searching for hotels in {city} for {max_guest} guests with {stars} stars from {start_date} to {end_date}.")

        hotels = search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
        if not hotels:
            print("No hotels found for your criteria.")
            exit()

        print("Please select a hotel by ID:")
        hotel_id = int(input("Hotel ID: "))
        selected_hotel = next((hotel for hotel in hotels if hotel.id == hotel_id), None)
        if not selected_hotel:
            print("Invalid hotel ID.")
            exit()

        print(f"Searching for available rooms in {selected_hotel.name} from {start_date} to {end_date}.")
        available_rooms = search_manager.search_rooms_by_availability(start_date, end_date, selected_hotel)
        if not available_rooms:
            print("No available rooms found.")
        else:
            for room in available_rooms:
                print(f"Room ID: {room.id} - {room.number} - {room.max_guests} guests - {room.description}")

            print("Please select a room by ID:")
            room_id = int(input("Room ID: "))
            selected_room = next((room for room in available_rooms if room.id == room_id), None)
            if not selected_room:
                print("Invalid room ID.")
            else:
                print(
                    f"Selected Room: {selected_room.hotel.name} - ID {selected_room.id} - Room number {selected_room.number} - {selected_room.max_guests} guests - {selected_room.description}")