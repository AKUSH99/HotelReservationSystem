from data_models.models import *
from data_access.data_base import init_db
from sqlalchemy import select, create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path


class SearchManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def get_all_hotels(self):
        query = select(Hotel)
        hotels = self.__session.execute(query).scalars().all()
        return hotels

    def get_hotels_by_name(self, name):
        query = select(Hotel).where(Hotel.name.like(f"%{name}%"))
        hotels = self.__session.execute(query).scalars().all()
        return hotels

    def get_hotels_by_city(self, city):
        query = select(Hotel).join(Address).where(func.lower(Address.city).like(f"%{city.lower()}%"))
        hotels = self.__session.execute(query).scalars().all()
        return hotels

    def search_hotels_by_city_date_guests_stars(self, city, start_date, end_date, max_guest, stars=None):
        query = select(Hotel).join(Address).join(Room).outerjoin(Booking, Room.number == Booking.room_number).where(
            and_(
                func.lower(Address.city) == city.lower(),
                Room.max_guests >= max_guest,
                or_(
                    Booking.id.is_(None),  # Es gibt keine Buchung für das Zimmer
                    and_(
                        Booking.end_date <= start_date,  # Bestehende Buchungen enden vor dem Startdatum
                        Booking.start_date >= end_date  # Bestehende Buchungen beginnen nach dem Enddatum
                    )
                )
            )
        ).distinct()

        if stars is not None:
            query = query.where(Hotel.stars == stars)

        result = self.__session.execute(query).scalars().all()
        return result

    def get_hotels_by_city_and_stars(self, city, stars):
        query = select(Hotel).join(Address).where(
            and_(func.lower(Address.city).like(f"%{city.lower()}%"), (Hotel.stars == stars)))
        hotels = self.__session.execute(query).scalars().all()
        return hotels

    def get_hotels_by_city_room_guest_stars(self, city, max_guest, stars=None):
        query = select(Hotel).join(Address).join(Room).where(
            and_(func.lower(Address.city).like(f"%{city.lower()}%"), Room.max_guests >= max_guest)
        ).distinct()
        if stars is not None:
            query = query.where(Hotel.stars == stars)
        return self.__session.execute(query).scalars().all()

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
        rooms = self.__session.execute(query).all()
        return [{
            "Room Number": room[0],
            "Type": room[1],
            "Max Guests": room[2],
            "Description": room[3],
            "Amenities": room[4],
            "Price": room[5]
        } for room in rooms]

    def get_hotel_details(self, hotel_id=None):
        query = select(
            Hotel.name,
            Address.street, Address.zip, Address.city,
            Hotel.stars
        ).join(Address, Hotel.address_id == Address.id)

        if hotel_id is not None:
            query = query.where(Hotel.id == hotel_id)

        hotels = self.__session.execute(query).fetchall()
        return [{
            'Name': hotel[0],
            'Address': f"{hotel[1]}, {hotel[2]}, {hotel[3]}",
            'Stars': hotel[4]
        } for hotel in hotels]

    def find_available_rooms_with_date(self, hotel_id, start_date, end_date):
        query = select(
            Room.number.label("Room Number"),
            Room.type.label("Type"),
            Room.max_guests.label("Max Guests"),
            Room.description.label("Description"),
            Room.amenities.label("Amenities"),
            Room.price.label("Price per Night"),
            (Room.price * 10).label("Total Price")
        ).outerjoin(Booking, and_(
            Room.number == Booking.room_number,
            Room.hotel_id == hotel_id,
            or_(
                Booking.start_date >= end_date,
                Booking.end_date <= start_date
            )
        )).where(
            and_(
                Room.hotel_id == hotel_id,
                Booking.id.is_(None)
            )
        )
        available_rooms = self.__session.execute(query).all()
        return [{
            "Room Number": room[0],
            "Type": room[1],
            "Max Guests": room[2],
            "Description": room[3],
            "Amenities": room[4],
            "Price per Night": room[5],
            "Total Price": room[6]
        } for room in available_rooms]

    def find_available_rooms_no_dates(self, hotel_id):
        query = select(
            Room.number.label("Room Number"),
            Room.type.label("Type"),
            Room.max_guests.label("Max Guests"),
            Room.description.label("Description"),
            Room.amenities.label("Amenities"),
            Room.price.label("Price per Night"),
            (Room.price * 10).label("Total Price")
        ).outerjoin(
            Booking,
            and_(
                Room.number == Booking.room_number,
                Room.hotel_id == hotel_id
            )
        ).where(
            and_(
                Room.hotel_id == hotel_id,
                Booking.id.is_(None)  # Room is available if it has no associated booking
            )
        )
        available_rooms = self.__session.execute(query).all()
        return [{
            "Room Number": room[0],
            "Type": room[1],
            "Max Guests": room[2],
            "Description": room[3],
            "Amenities": room[4],
            "Price per Night": room[5],
            "Total Price": room[6]
        } for room in available_rooms]


if __name__ == "__main__":
    sm = SearchManager("../data/database.db")
    hotels = sm.get_all_hotels()
    for hotel in hotels:
        print(hotel)

# User Story 1.1.1.
# Ich möchte alle Hotels in einer Stadt durchsuchen, damit ich
# das Hotel nach meinem bevorzugten Standort (Stadt) auswählen kann.

city = input("Enter city: ")
hotel_city = sm.get_hotels_by_city(city)
for hotel in hotel_city:
    print(hotel)
# %%
# User Story 1.1.2
# Ich möchte alle Hotels in einer Stadt nach der Anzahl der
# Sterne durchsuchen.

city = str(input("Enter city: "))
stars = int(input("Enter stars 1 to 5: "))
hotel_stars = sm.get_hotels_by_city_and_stars(city=city, stars=stars)
if not hotel_stars and stars == stars:
    print("No hotels found with given amount of stars.! ")
else:
    for hotel in hotel_stars:
        print(hotel)
# %%
# 1.1.3. Ich möchte alle Hotels in einer Stadt durchsuchen, die Zimmer
# haben, die meiner Gästezahl entsprechen (nur 1 Zimmer pro
# Buchung), entweder mit oder ohne Anzahl der Sterne.

# Schritt 1: Eingabe der Suchkriterien
city = input("Enter city: ").strip()
max_guest = int(input("Enter max guests: "))
stars = input("Enter stars 1 to 5 (optional): ").strip()
if stars:
    stars = int(stars)
else:
    stars = None

# Schritt 2: Suche nach Hotels
hotels = sm.get_hotels_by_city_room_guest_stars(city=city, max_guest=max_guest, stars=stars)
if not hotels:
    print("No hotels found matching your criteria.")
else:
    print("Hotels found:")
    for i, hotel in enumerate(hotels, start=1):
        print(f"{i}. {hotel.name}, {hotel.address.city} - {hotel.stars} stars")

    # Schritt 3: Auswahl eines Hotels
    hotel_index = int(input("Select a hotel by number: ")) - 1
    if hotel_index < 0 or hotel_index >= len(hotels):
        print("Invalid selection.")
    else:
        selected_hotel = hotels[hotel_index]
        print(f"You selected: {selected_hotel.name}")

        # Schritt 4: Anzeige der Zimmer des ausgewählten Hotels, die mindestens Platz für die gewünschte Anzahl an Personen bieten
        rooms = sm.get_rooms_by_hotel(selected_hotel.id, max_guest)
        if not rooms:
            print("No rooms found for the selected hotel that accommodate the desired number of guests.")
        else:
            print("Rooms in the selected hotel that can accommodate at least the desired number of guests:\n")
            for room in rooms:
                print(
                    f"Room Number: {room['Room Number']}, Type: {room['Type']}, Max Guests: {room['Max Guests']}")
                print(f"Description: {room['Description']}")
                print(f"Amenities: {room['Amenities']}")
                print(f"Price per Night: {room['Price']}\n")


# 1.1.4. Ich möchte alle Hotels in einer Stadt durchsuchen,
# die während meines Aufenthaltes ("von" (start_date) und "bis" (end_date)) Zimmer für meine Gästezahl zur Verfügung haben,
# entweder mit oder ohne Anzahl der Sterne, damit ich nur relevante Ergebnisse sehe.

# Hier setzen Sie die Inputs für die Suche
city = input("Enter city: ")
start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
max_guest = int(input("Enter max guests: "))
stars = input("Enter stars 1 to 5 (optional): ")
if stars == "":
    stars = None
else:
    stars = int(stars)

# Aufruf der Methode
hotels = sm.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
if not hotels:
    print("No hotels found for your criteria.")
else:
    for hotel in hotels:
        print(hotel)

# %%
# 1.1.5. Ich möchte die folgenden Informationen pro Hotel sehen:
# Name, Adresse, Anzahl der Sterne.

hotel_id = input("Enter the hotel id you want to search for: ")
hotel_details = sm.get_hotel_details(hotel_id=hotel_id)

if not hotel_details:
    print("No hotels found!")
else:
    for detail in hotel_details:
        print(f"Name: {detail['Name']}, Address: {detail['Address']}, Stars: {detail['Stars']}")
# %%
# 1.1.6. Ich möchte ein Hotel auswählen, um die Details zu sehen (z.B.
# verfügbare Zimmer [siehe 1.2])

hotel_id = input("Enter the hotel ID to search for available rooms: ")

# Aufrufen der Methode find_available_rooms_no_dates, um alle freien Zimmer zu suchen
available_rooms = sm.find_available_rooms_no_dates(hotel_id=int(hotel_id))

print("Available rooms for hotel id {}:".format(hotel_id))
for room in available_rooms:
    print(
        "Room Number: {} | Type: {} | Max Guests: {} | Description: {} | Amenities: {} | Price per Night: {} | Total Price for 10 Nights: {}".format(
            room["Room Number"],
            room["Type"],
            room["Max Guests"],
            room["Description"],
            room["Amenities"],
            room["Price per Night"],
            room["Total Price"]
        ))

# %%
# 1.2.1. Ich möchte die folgenden Informationen pro Zimmer sehen: Zimmertyp, max. Anzahl der Gäste, Beschreibung, Ausstattung, Preis pro Nacht und Gesamtpreis.
# 1.2.2. Ich möchte nur die verfügbaren Zimmer sehen

# Beispiel: Eingabe der Daten zur Suche nach verfügbaren Zimmern
hotel_id = input("Enter the hotel ID to search for available rooms: ")
start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")

# Aufrufen der Methode find_available_rooms, um freie Zimmer zu suchen
available_rooms = sm.find_available_rooms_with_date(hotel_id=int(hotel_id), start_date=start_date, end_date=end_date)

if not available_rooms:
    print("No available rooms found for the period from {} to {}.".format(start_date, end_date))
else:
    print("Available rooms for hotel id {}:\n".format(hotel_id))
    for room in available_rooms:
        print(
            "Room Number: {} | Type: {} | Max Guests: {} | Description: {} | Amenities: {} | Price per Night: {} | Total Price for 10 Nights: {}".format(
                room["Room Number"],
                room["Type"],
                room["Max Guests"],
                room["Description"],
                room["Amenities"],
                room["Price per Night"],
                room["Total Price"]
            ))
        print()
# Hinweis: Schritte wiederholen, um verschiedene Hotels und Zeiträume zu prüfen.