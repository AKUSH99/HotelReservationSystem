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
        query = select(Hotel).join(Address).where(func.lower(Address.city.like(f"%{city}%")))
        hotels = self.__session.execute(query).scalars().all()
        return hotels

    def search_hotels_by_city_date_guests_stars(self, city, start_date, end_date, max_guest, stars=None):
        query = select(Hotel).join(Address).join(Room).join(Booking, isouter=True).where(
            and_(
                func.lower(Address.city) == city.lower(),
                Room.max_guests >= max_guest,
                or_(
                    Booking.id.is_(None),
                    and_(
                        Booking.end_date < start_date,
                        Booking.start_date > end_date
                    )
                )
            )
        ).distinct()

        if stars is not None:
            query = query.where(Hotel.stars == stars)

        result = self.__session.execute(query).scalars().all()
        return result

    def get_hotels_by_city_and_stars(self, city, stars):
        query = select(Hotel).join(Address).where((Address.city.like(f"%{city}%") & (Hotel.stars == stars)))
        hotels = self.__session.execute(query).scalars().all()
        return hotels

    def get_hotels_by_city_room_guest_stars(self, city, max_guest, stars=None):
        query = select(Hotel).join(Address).join(Room).where(
            func.lower(Address.city.like(f"%{city}%")) & (Room.max_guests == max_guest)
        ).distinct()
        if stars is not None:
            query = query.where(Hotel.stars == stars)
        return self.__session.execute(query).scalars().all()

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

    def find_available_rooms(self, hotel_id, start_date, end_date):
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
            or_(
                Booking.start_date <= start_date,
                Booking.end_date >= end_date
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




        print(query)
        result = self.__session.execute(query).scalars().all()
        return result

if __name__ == "__main__":
    sm = SearchManager("../data/database.db")
    hotels = sm.get_all_hotels()
    for hotel in hotels:
        print(hotel)



    # 1. Als Gastnutzer (nicht eingeloggt/registriert):
    # 1.1. Als Gastnutzer möchte ich die verfügbaren Hotels durchsuchen, damit
    # ich dasjenige auswählen kann, welches meinen Wünschen entspricht.

    # User Story 1.1.1.
    # Ich möchte alle Hotels in einer Stadt durchsuchen, damit ich
    # das Hotel nach meinem bevorzugten Standort (Stadt) auswählen kann.
    #TODO: Take User Input
    city = "Olten" #input("Enter city: ")
    hotel_city = sm.get_hotels_by_city(city)
    for hotel in hotel_city:
        print(hotel)


    # User Story 1.1.2
    # Ich möchte alle Hotels in einer Stadt nach der Anzahl der
    # Sterne durchsuchen.
    #TODO: Kommentare entfernen bei der Abgabe
    city = "Olten" #str(input("Enter city: "))
    stars = 3 #int(input("Enter stars 1 to 5: "))
    hotel_stars = sm.get_hotels_by_city_and_stars(city=city, stars=stars)
    if not hotel_stars and stars == stars:
        print("No hotels found with given amount of stars.! ")
    else:
        for hotel in hotel_stars:
            print(hotel)


    # 1.1.3. Ich möchte alle Hotels in einer Stadt durchsuchen, die Zimmer
    # haben, die meiner Gästezahl entsprechen (nur 1 Zimmer pro
    # Buchung), entweder mit oder ohne Anzahl der Sterne.
    city = str(input("Enter city: "))
    max_guest = int(input("Enter max guests: "))
    stars = input("Enter stars 1 to 5 (optional): ")
    if max_guest < 1 or max_guest > 4:
        print("Enter valid number of guests!")

    if stars == "":
        stars = None
    else:
        stars = int(stars)
    hotel_city_max_guest_stars = sm.get_hotels_by_city_room_guest_stars(city=city, max_guest=max_guest, stars=stars)
    for hotel in hotel_city_max_guest_stars:
        print(hotel)
        hotel_name = f"{hotel.name}-->"
        if len(hotel_name) >=100:
            hotel_name = f"{hotel.name[:105]}...-> "
        for room in hotel.rooms:
            print(f"{hotel_name:<20} room number: {room.number} | room type: {room.type} | description: {room.description}| amenities: {room.amenities} | price per night: {room.price} |")



    # 1.1.4. Ich möchte alle Hotels in einer Stadt durchsuchen,
    # die während meines Aufenthaltes ("von" (start_date) und "bis" (end_date)) Zimmer für meine Gästezahl zur Verfügung haben,
    # entweder mit oder ohne Anzahl der Sterne, damit ich nur relevante Ergebnisse sehe.
    # Beispiel: Suche nach Hotels in einer Stadt, die während des Aufenthalts Zimmer für die Gästezahl haben, optional gefiltert nach Sternen
    city = input("Enter city: ")
    start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
    end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
    max_guest = int(input("Enter max guests: "))
    stars = input("Enter stars 1 to 5 (optional): ")

    if stars == "":
        stars = None
    else:
        stars = int(stars)

    hotels = sm.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
    for hotel in hotels:
        print(hotel)

    # 1.1.5. Ich möchte die folgenden Informationen pro Hotel sehen:
    # Name, Adresse, Anzahl der Sterne.
    # TODO: Someone please check :)
    hotel_id = input("Enter the hotel id you want to search for: ")
    hotel_details = sm.get_hotel_details(hotel_id=hotel_id)

    if not hotel_details:
        print("No hotels found!")
    else:
        for detail in hotel_details:
            print(f"Name: {detail['Name']}, Address: {detail['Address']}, Stars: {detail['Stars']}")



    # 1.1.6. Ich möchte ein Hotel auswählen, um die Details zu sehen (z.B.
    # verfügbare Zimmer [siehe 1.2])
    #1.2. Als Gastnutzer möchte ich Details zu verschiedenen Zimmertypen (EZ, DZ, Familienzimmer), die in einem Hotel verfügbar sind, sehen, einschließlich der maximalen Anzahl von Gästen für dieses Zimmer, Beschreibung, Preis und Ausstattung, um eine fundierte Entscheidung zu treffen.
    #1.2.1. Ich möchte die folgenden Informationen pro Zimmer sehen: Zimmertyp, max. Anzahl der Gäste, Beschreibung, Ausstattung, Preis pro Nacht und Gesamtpreis.
    #1.2.2. Ich möchte nur die verfügbaren Zimmer sehen

    # Beispiel: Eingabe der Daten zur Suche nach verfügbaren Zimmern
    hotel_id = input("Enter the hotel ID to search for available rooms: ")
    start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
    end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")

    # Aufrufen der Methode find_available_rooms, um freie Zimmer zu suchen
    available_rooms = sm.find_available_rooms(hotel_id=int(hotel_id), start_date=start_date, end_date=end_date)

    if not available_rooms:
        print("No available rooms found for the period from {} to {}.".format(start_date, end_date))
    else:
        print("Available rooms:")
        for room in available_rooms:
            print("Room Number: {}, Type: {}, Max Guests: {}, Description: {}, Amenities: {}, Price per Night: {}, Total Price for 10 Nights: {}".format(
                room["Room Number"],
                room["Type"],
                room["Max Guests"],
                room["Description"],
                room["Amenities"],
                room["Price per Night"],
                room["Total Price"]
            ))
    # Hinweis: Schritte wiederholen, um verschiedene Hotels und Zeiträume zu prüfen.

