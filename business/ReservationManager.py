from pathlib import Path

from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session

from datetime import datetime
import csv
import re

from business.SearchManager import SearchManager
from business.UserManager import UserManager
from data_models.models import Booking, Room, Hotel, Guest, RegisteredGuest, Address, Login, Role
from data_access.data_base import init_db


class ReservationManager:
    def __init__(self, session):
        self.session = session

    def is_room_available(self, room_number, room_hotel_id, start_date, end_date):
        # Überprüft, ob das Zimmer im angegebenen Zeitraum im angegebenen Hotel verfügbar ist
        bookings = self.session.query(Booking).filter(
            and_(
                Booking.room_number == room_number,
                Booking.room_hotel_id == room_hotel_id,
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
        #start_date = datetime.strptime(start_date, '%Y-%m-%d')
        #end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if self.is_room_available(room_number, room_hotel_id, start_date, end_date):
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
        new_address = Address(street=street, zip=zip, city=city)
        self.session.flush()  # Stellt sicher, dass die Adresse eine ID bekommt
        new_guest = Guest(
            firstname=firstname,
            lastname=lastname,
            email=email,
            address=new_address
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
    db_file = "../data/database.db"
    database_path = Path(db_file)
    if not database_path.is_file():
        init_db(db_file, generate_example_data=True)
    session = scoped_session(sessionmaker(bind=create_engine(f"sqlite:///{database_path}", echo=False)))

    Session = session()
    reservation_manager = ReservationManager(session)
    search_manager = SearchManager(session)
    user_manager = UserManager(reservation_manager.session)

    # Interaktiver Prozess zur Auswahl der Buchungsoption
    print("Welcome! How would you like to proceed?")
    print("1. Proceed as a guest with minimal information")
    print("2. Register as a new user")
    print("3. Log in to an existing account")

    choice = input("Please select an option (1/2/3): ")

    if choice == "1":
        # Buchung als Gast
        firstname = input("Firstname: ")
        lastname = input("Lastname: ")

        while True:
            email = input("Email: ")
            if reservation_manager.validate_email(email):
                break
            else:
                print("Invalid e-mail format. Please enter again.")
        street = input("Enter your street: ")
        zip = input("Enter your zip: ")
        city = input("Enter your city: ")
        guest_id = reservation_manager.create_guest(firstname, lastname, email)

        # Fortsetzen mit der Buchung
        city = input("Enter city for hotel: ")
        max_guest = int(input("Enter max guests: "))

        while True:
            start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(start_date):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                break
            else:
                print("Invalid date format. Please enter again.")

        while True:
            end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(end_date):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                break
            else:
                print("Invalid date format. Please enter again.")

        stars = input("Enter stars 1 to 5 (optional): ")
        if stars == "":
            stars = None
        else:
            stars = int(stars)

        # Hier wird die Methode zum Suchen von Hotels aufgerufen
        search_manager = SearchManager(reservation_manager.session)
        hotels = search_manager.search_hotels_by_city_date_guests_stars(city, start_date, end_date, max_guest, stars)

        if not hotels:
            print("No hotels found for your criteria.")
        else:
            for hotel in hotels:
                print(
                    f"Hotel ID: {hotel.id}, name: {hotel.name}, {hotel.stars} stars, address: {hotel.address.street}, {hotel.address.city}")
            room_hotel_id = int(input("Enter Hotel ID: "))

            matching_rooms = search_manager.get_rooms_by_hotel(room_hotel_id, max_guest)

            valid_room_numbers = []

            for room in matching_rooms:
                if reservation_manager.is_room_available(room['Room Number'], room_hotel_id, start_date, end_date):
                    valid_room_numbers.append(room['Room Number'])
                    print(
                        f"Room No.: {room['Room Number']}, up to {room['Max Guests']} people, description: {room['Description']}, price per night: {room['Price']} Hotel: {hotel.name}, {hotel.address.city}")

            if not valid_room_numbers:
                print("No available rooms found for your criteria.")
            else:
                while True:
                    room_number = input("Enter room number: ")
                    if room_number in valid_room_numbers:
                        break
                    else:
                        print(
                            f"Invalid room number. Please choose from the available rooms: {', '.join(valid_room_numbers)}")

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
                    booking_id = int(
                    result.split()[-1])
                    booking = reservation_manager.get_booking_by_id(booking_id)
                    save_result = reservation_manager.save_booking_details(booking)
                    print(save_result)

    elif choice == "2":

        print("Registration as a new user:")
        firstname = input("Firstname: ")
        lastname = input("Lastname: ")

        while True:
            email = input("Email: ")
            if reservation_manager.validate_email(email):
                break
            else:
                print("Invalid e-mail format. Please enter again.")

        username = input("Username: ")
        password = input("Password: ")
        street = input("Street: ")
        zip_code = input("Zip: ")
        city = input("City: ")

        user = user_manager.register_user(username, password, firstname, lastname, email, street, zip_code, city)
        if user:
            print("User successfully registered.")
        else:
            print("User registration failed.")

        user = user_manager.get_guest_of(user.login)
        if user:
            print("Benutzerdetails wurden erfolgreich registriert.")

        # Fortsetzen mit der Buchung
        guest_id = user.id
        city = input("Enter city for hotel: ")
        max_guest = int(input("Enter max guests: "))

        while True:
            start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(start_date):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                break
            else:
                print("Invalid date format. Please enter again.")

        while True:
            end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
            if reservation_manager.validate_date(end_date):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                break
            else:
                print("Invalid date format. Please enter again.")

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
                print(
                    f"Hotel ID: {hotel.id}, name: {hotel.name}, {hotel.stars} stars, address: {hotel.address.street}, {hotel.address.city}")
            room_hotel_id = int(input("Enter hotel ID: "))

            matching_rooms = search_manager.get_rooms_by_hotel(room_hotel_id, max_guest)

            valid_room_numbers = []

            for room in matching_rooms:
                if reservation_manager.is_room_available(room['Room Number'], room_hotel_id, start_date, end_date):
                    valid_room_numbers.append(room['Room Number'])
                    print(
                        f"Room No.: {room['Room Number']}, up to {room['Max Guests']} people, description: {room['Description']}, price per night: {room['Price']} Hotel: {hotel.name}, {hotel.address.city}")

            if not valid_room_numbers:
                print("No available rooms found for your criteria.")
            else:
                while True:
                    room_number = input("Enter room number: ")
                    if room_number in valid_room_numbers:
                        break
                    else:
                        print(
                            f"Invalid room number. Please choose from the available rooms: {', '.join(valid_room_numbers)}")

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
                    print("To manage yor bookings go to InventoryManager! Thank you!")


    elif choice == "3":
        # Code zum Einloggen in ein bestehendes Konto
        print("Log in to an existing account")
        input_username = input("Enter username: ")
        input_password = input("Enter password: ")
        user_manager = UserManager(reservation_manager.session)
        login_result = user_manager.login(input_username, input_password)
        if login_result:
            print("Login successful!")
            guest_id = user_manager.get_current_login().id
            city = input("Enter city for hotel: ")
            max_guest = int(input("Enter max guests: "))

            while True:
                start_date = input("Enter the start date of your stay (YYYY-MM-DD): ")
                if reservation_manager.validate_date(start_date):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    break
                else:
                    print("Invalid date format. Please enter again.")

            while True:
                end_date = input("Enter the end date of your stay (YYYY-MM-DD): ")
                if reservation_manager.validate_date(end_date):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    break
                else:
                    print("Invalid date format. Please enter again.")

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
                    print(
                        f"Hotel ID: {hotel.id}, name: {hotel.name}, {hotel.stars} stars, address: {hotel.address.street}, {hotel.address.city}")
                room_hotel_id = int(input("Enter hotel ID: "))

                matching_rooms = search_manager.get_rooms_by_hotel(room_hotel_id, max_guest)

                valid_room_numbers = []

                for room in matching_rooms:
                    if reservation_manager.is_room_available(room['Room Number'], room_hotel_id, start_date, end_date):
                        valid_room_numbers.append(room['Room Number'])
                        print(
                            f"Room No.: {room['Room Number']}, up to {room['Max Guests']} people, description: {room['Description']}, price per night: {room['Price']} Hotel: {hotel.name}, {hotel.address.city}")

                if not valid_room_numbers:
                    print("No available rooms found for your criteria.")
                else:
                    while True:
                        room_number = input("Enter room number: ")
                        if room_number in valid_room_numbers:
                            break
                        else:
                            print(
                                f"Invalid room number. Please choose from the available rooms: {', '.join(valid_room_numbers)}")

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
                        print("To manage yor bookings go to InventoryManager! Thank you!")
        else:
            print("Login failed! Please check your username and password.")

    else:
        print("Invalid option. Please restart the programme and select a valid option.")
