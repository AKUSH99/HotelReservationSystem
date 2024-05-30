from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import csv
import re
from data_models.models import Booking, Room, Hotel, Guest, RegisteredGuest, Address, Login, Role
from data_access.data_base import init_db
from pathlib import Path


class ReservationManager:
    def __init__(self, database_file):
        # Initialisierung der Datenbankverbindung
        self.database_path = Path(database_file)
        if not self.database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def is_room_available(self, room_number, start_date, end_date):
        # Überprüft, ob das Zimmer im angegebenen Zeitraum verfügbar ist
        bookings = self.session.query(Booking).filter(
            and_(
                Booking.room_number == room_number,
                or_(
                    and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                    and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                    and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
                )
            )
        ).all()
        return len(bookings) == 0

    def create_booking(self, room_hotel_id, room_number, guest_id, number_of_guests, start_date, end_date, comment=''):
        # User Story 1.3: Erstellt eine Buchung, wenn das Zimmer verfügbar ist
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if self.is_room_available(room_number, start_date, end_date):
            new_booking = Booking(
                room_hotel_id=room_hotel_id,
                room_number=room_number,
                guest_id=guest_id,
                number_of_guests=number_of_guests,
                start_date=start_date,
                end_date=end_date,
                comment=comment
            )
            self.session.add(new_booking)
            self.session.commit()
            return f"Booking successfully created with ID: {new_booking.id}"
        else:
            return "Room is not available for the selected dates."

    def save_booking_details(self, booking):
        # User Story 1.5: Speichert die Buchungsdetails in einer CSV-Datei
        if booking:
            booking_details = [
                ["booking_id", booking.id],
                ["room_hotel_id", booking.room_hotel_id],
                ["room_number", booking.room_number],
                ["guest_id", booking.guest_id],
                ["number_of_guests", booking.number_of_guests],
                ["start_date", booking.start_date.strftime('%Y-%m-%d')],
                ["end_date", booking.end_date.strftime('%Y-%m-%d')],
                ["comment", booking.comment]
            ]
            file_path = f'booking_{booking.id}_details.csv'
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(booking_details)
            return f"Booking details saved to CSV file at {file_path}."
        return "No booking found with the given ID."

    def get_booking_by_id(self, booking_id):
        # Methode, um eine Buchung anhand ihrer ID zu holen
        return self.session.query(Booking).filter_by(id=int(booking_id)).first()

    def create_guest(self, firstname, lastname, email):
        # Erstellt einen temporären Gast mit einer leeren Adresse
        empty_address = Address(street='', zip='', city='')
        self.session.add(empty_address)
        self.session.flush()  # Stellt sicher, dass die Adresse eine ID bekommt
        new_guest = Guest(
            firstname=firstname,
            lastname=lastname,
            email=email,
            address_id=empty_address.id
        )
        self.session.add(new_guest)
        self.session.commit()
        return new_guest.id

    def validate_email(self, email):
        # Validiert die E-Mail-Adresse
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.match(regex, email):
            return True
        return False

    def validate_date(self, date_text):
        # Validiert das Datumsformat
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    from SearchManager import SearchManager

    reservation_manager = ReservationManager('../data/database.db')
    search_manager = SearchManager('../data/database.db')

    # Interaktiver Prozess zur Auswahl der Buchungsoption
    print("Willkommen! Wie möchten Sie fortfahren?")
    print("1. Als Gast mit minimalen Informationen fortfahren")
    print("2. Als neuer Benutzer registrieren")
    print("3. In ein bestehendes Konto einloggen")

    choice = input("Bitte wählen Sie eine Option (1/2/3): ")

    if choice == "1":
        # Buchung als Gast
        firstname = input("Vorname: ")
        lastname = input("Nachname: ")

        while True:
            email = input("Email: ")
            if reservation_manager.validate_email(email):
                break
            else:
                print("Ungültiges E-Mail-Format. Bitte erneut eingeben.")

        guest_id = reservation_manager.create_guest(firstname, lastname, email)

        # Fortsetzen mit der Buchung
        city = input("Enter city for hotel: ")
        max_guest = int(input("Enter max guests: "))

        while True:
            start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(start_date):
                break
            else:
                print("Ungültiges Datumsformat. Bitte erneut eingeben.")

        while True:
            end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(end_date):
                break
            else:
                print("Ungültiges Datumsformat. Bitte erneut eingeben.")

        stars = input("Enter stars 1 to 5 (optional): ")
        if stars == "":
            stars = None
        else:
            stars = int(stars)

        # Hier wird die Methode zum Suchen von Hotels aufgerufen
        hotels = search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
        if not hotels:
            print("No hotels found for your criteria.")
        else:
            for hotel in hotels:
                print(hotel)
            room_hotel_id = int(input("Enter hotel id: "))
            room_number = input("Enter room number: ")

            result = reservation_manager.create_booking(
                room_hotel_id=room_hotel_id,
                room_number=room_number,
                guest_id=guest_id,
                number_of_guests=max_guest,
                start_date=start_date,
                end_date=end_date,
                comment='Booking as guest'
            )
            print(result)

            if "successfully" in result:
                booking_id = result.split()[-1]
                booking = reservation_manager.get_booking_by_id(booking_id)
                save_result = reservation_manager.save_booking_details(booking)
                print(save_result)

    elif choice == "2":
        # Neuer Benutzer (wird in UserManager.py behandelt)
        from UserManager import UserManager

        user_manager = UserManager('../data/database1.db')
        print("Registrierung als neuer Benutzer:")
        firstname = input("Vorname: ")
        lastname = input("Nachname: ")

        while True:
            email = input("Email: ")
            if reservation_manager.validate_email(email):
                break
            else:
                print("Ungültiges E-Mail-Format. Bitte erneut eingeben.")

        username = input("Benutzername: ")
        password = input("Passwort: ")
        street = input("Straße: ")
        zip_code = input("Postleitzahl: ")
        city = input("Stadt: ")

        message = user_manager.add_new_user(firstname, lastname, email, username, password, street, zip_code, city)
        print(message)

        user = user_manager.get_user_by_username(username)
        if user:
            user_manager.save_user_details_to_csv(user)
            print("Benutzerdetails wurden in user_details.csv gespeichert.")

        # Fortsetzen mit der Buchung
        guest_id = user.id
        city = input("Enter city for hotel: ")
        max_guest = int(input("Enter max guests: "))

        while True:
            start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(start_date):
                break
            else:
                print("Ungültiges Datumsformat. Bitte erneut eingeben.")

        while True:
            end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(end_date):
                break
            else:
                print("Ungültiges Datumsformat. Bitte erneut eingeben.")

        stars = input("Enter stars 1 to 5 (optional): ")
        if stars == "":
            stars = None
        else:
            stars = int(stars)

        hotels = search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)
        if not hotels:
            print("No hotels found for your criteria.")
        else:
            for hotel in hotels:
                print(hotel)
            room_hotel_id = int(input("Enter hotel id: "))
            room_number = input("Enter room number: ")

            result = reservation_manager.create_booking(
                room_hotel_id=room_hotel_id,
                room_number=room_number,
                guest_id=guest_id,
                number_of_guests=max_guest,
                start_date=start_date,
                end_date=end_date,
                comment='Booking as new registered user'
            )
            print(result)

            if "successfully" in result:
                booking_id = result.split()[-1]
                booking = reservation_manager.get_booking_by_id(booking_id)
                save_result = reservation_manager.save_booking_details(booking)
                print(save_result)

    elif choice == "3":
        # Code zum Einloggen in ein bestehendes Konto
        print("Einloggen in ein bestehendes Konto")
        # Hier den Login-Prozess und die Buchung für eingeloggte Benutzer implementieren
        pass

    else:
        print("Ungültige Option. Bitte starten Sie das Programm erneut und wählen Sie eine gültige Option.")
