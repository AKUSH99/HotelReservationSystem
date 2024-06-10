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


# class HotelReservationApp(tk.Tk):
#     def __init__(self, search_manager):
#         super().__init__()
#         self.search_manager = search_manager
#         self.title("Hotelreservierungssystem")
#         self.geometry("1200x800")
#         self.configure(bg="#f5f5f5")
#
#         # Hauptcontainer für das gesamte Layout
#         main_container = tk.Frame(self, bg="#f5f5f5")
#         main_container.pack(fill="both", expand=True)
#
#         # Linker Frame für die Suchmaske
#         left_frame = tk.Frame(main_container, bg="#e8f0fe", width=300)
#         left_frame.pack(side="left", fill="y", padx=10, pady=10)
#
#         # Rechter Frame für die Suchergebnisse und Details
#         right_frame = tk.Frame(main_container, bg="#f0f4ff")
#         right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
#
#         # Suchmaske
#         tk.Label(left_frame, text="Hotelsuche mit 'Enter' bestätigen", font=("Arial", 18, "bold"), bg="#F0E68C").pack(
#             pady=10)
#
#         self.city_entry = self.create_entry(left_frame, "Stadt (optional):")
#         self.stars_entry = self.create_entry(left_frame, "Sterne (optional):")
#         self.guests_entry = self.create_entry(left_frame, "Max Gäste (optional):")
#         self.start_date_entry = self.create_date_entry(left_frame, "Startdatum (DD.MM.YYYY, optional):")
#         self.end_date_entry = self.create_date_entry(left_frame, "Enddatum (DD.MM.YYYY, optional):")
#
#         search_btn = tk.Button(left_frame, text="Suchen", command=self.search_hotels, font=("Arial", 14), bg="#4CAF50",
#                                fg="white")
#         search_btn.pack(pady=10)
#
#         # Bind Enter key to search_hotels method
#         self.bind('<Return>', lambda event: self.search_hotels())
#
#         # Suchmaske - Verfügbare Zimmer suchen
#         tk.Label(left_frame, text="Verfügbare Zimmer suchen", font=("Arial", 18, "bold"), bg="#F0E68C").pack(pady=10)
#
#         self.hotel_name_entry = self.create_entry(left_frame, "Hotel Name (optional):")
#         self.avail_start_date_entry = self.create_date_entry(left_frame, "Startdatum (DD.MM.YYYY):")
#         self.avail_end_date_entry = self.create_date_entry(left_frame, "Enddatum (DD.MM.YYYY):")
#
#         search_rooms_btn = tk.Button(left_frame, text="Verfügbare Zimmer suchen", command=self.search_available_rooms,
#                                      font=("Arial", 14), bg="#4CAF50", fg="white")
#         search_rooms_btn.pack(pady=10)
#
#         # Ergebnisse und Details
#         instruction_label = tk.Label(right_frame,
#                                      text="Klicken Sie auf ein Hotel, um die verfügbaren Räume anzuzeigen.",
#                                      font=("Arial", 14), bg="#DAF7A6")
#         instruction_label.pack(pady=10)
#
#         self.results_frame = tk.Frame(right_frame, bg="#f0f4ff")
#         self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
#
#         self.tree = ttk.Treeview(self.results_frame, columns=("Name", "Stadt", "Sterne"), show='headings', height=10)
#         self.tree.heading("Name", text="Name")
#         self.tree.heading("Stadt", text="Stadt")
#         self.tree.heading("Sterne", text="Sterne")
#         self.tree.pack(fill="both", expand=True)
#         self.tree.bind('<<TreeviewSelect>>', self.show_selected_hotel_details)
#
#         scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")
#
#         self.details_frame = tk.Frame(right_frame, bg="#eef2ff", relief="groove", borderwidth=2)
#         self.details_frame.pack(fill="both", expand=True, padx=10, pady=10)
#
#     def create_entry(self, parent, label_text):
#         frame = tk.Frame(parent, bg="#e8f0fe")
#         frame.pack(fill="x", pady=5)
#         tk.Label(frame, text=label_text, font=("Arial", 12), bg="#e8f0fe").pack(side="left")
#         entry = tk.Entry(frame, font=("Arial", 12))
#         entry.pack(side="left", fill="x", expand=True)
#         return entry
#
#     def create_date_entry(self, parent, label_text):
#         frame = tk.Frame(parent, bg="#e8f0fe")
#         frame.pack(fill="x", pady=5)
#         tk.Label(frame, text=label_text, font=("Arial", 12), bg="#e8f0fe").pack(side="left")
#         entry = tk.Entry(frame, font=("Arial", 12))
#         entry.pack(side="left", fill="x", expand=True)
#         return entry
#
#     def parse_date(self, date_str):
#         if date_str:
#             try:
#                 return datetime.strptime(date_str, "%d.%m.%Y").strftime('%Y-%m-%d')
#             except ValueError:
#                 messagebox.showerror("Ungültiges Datum", "Bitte geben Sie das Datum im Format DD.MM.YYYY ein.")
#                 return None
#         return None
#
#     def search_hotels(self):
#         for i in self.tree.get_children():
#             self.tree.delete(i)
#         self.clear_details()
#
#         city = self.city_entry.get()
#         stars = self.stars_entry.get()
#         max_guests = self.guests_entry.get()
#         start_date = self.parse_date(self.start_date_entry.get())
#         end_date = self.parse_date(self.end_date_entry.get())
#
#         try:
#             stars = int(stars) if stars else None
#             max_guests = int(max_guests) if max_guests else 1
#         except ValueError:
#             messagebox.showerror("Ungültiger Wert",
#                                  "Bitte geben Sie gültige numerische Werte für Sterne und max. Gäste ein.")
#             return
#
#         hotels = self.search_manager.search_hotels_by_city_date_guests_stars(
#             city, start_date, end_date, max_guests, stars
#         )
#
#         if not hotels:
#             messagebox.showinfo("Keine Hotels gefunden",
#                                 "Es wurden keine Hotels gefunden, die Ihren Kriterien entsprechen.")
#         else:
#             for hotel in hotels:
#                 self.tree.insert("", "end", values=(hotel.name, hotel.address.city, hotel.stars))
#
#             # Automatically select the first hotel in the list and show its details
#             if self.tree.get_children():
#                 first_item = self.tree.get_children()[0]
#                 self.tree.selection_set(first_item)
#                 self.show_selected_hotel_details(None)
#
#     def search_available_rooms(self):
#         self.clear_details()
#
#         hotel_name = self.hotel_name_entry.get()
#         avail_start_date = self.parse_date(self.avail_start_date_entry.get())
#         avail_end_date = self.parse_date(self.avail_end_date_entry.get())
#
#         if not avail_start_date or not avail_end_date:
#             messagebox.showerror("Fehlende Daten", "Bitte geben Sie sowohl das Start- als auch das Enddatum ein.")
#             return
#
#         hotel = None
#         if hotel_name:
#             hotels = self.search_manager.get_hotels_by_name(hotel_name)
#             if hotels:
#                 hotel = hotels[0]
#             else:
#                 messagebox.showinfo("Hotel nicht gefunden", "Es wurde kein Hotel mit diesem Namen gefunden.")
#                 return
#
#         available_rooms = self.search_manager.search_rooms_by_availability(
#             start_date=datetime.strptime(avail_start_date, "%Y-%m-%d"),
#             end_date=datetime.strptime(avail_end_date, "%Y-%m-%d"),
#             hotel=hotel
#         )
#
#         if not available_rooms:
#             messagebox.showinfo("Keine verfügbaren Zimmer",
#                                 "Es wurden keine verfügbaren Zimmer für die angegebenen Daten gefunden.")
#         else:
#             self.display_available_rooms(available_rooms)
#
#     def display_available_rooms(self, rooms):
#         self.clear_details()
#
#         rooms_canvas = tk.Canvas(self.details_frame, bg="#eef2ff")
#         rooms_canvas.pack(side="left", fill="both", expand=True)
#
#         scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=rooms_canvas.yview)
#         scrollbar.pack(side="right", fill="y")
#
#         scrollable_frame = tk.Frame(rooms_canvas, bg="#eef2ff")
#         scrollable_frame.bind(
#             "<Configure>",
#             lambda e: rooms_canvas.configure(
#                 scrollregion=rooms_canvas.bbox("all")
#             )
#         )
#
#         rooms_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
#         rooms_canvas.configure(yscrollcommand=scrollbar.set)
#
#         for room in rooms:
#             room_details = (f"Zimmernummer: {room.number}\n"
#                             f"Typ: {room.type}\n"
#                             f"Max Gäste: {room.max_guests}\n"
#                             f"Beschreibung: {room.description}\n"
#                             f"Ausstattung: {room.amenities}\n"
#                             f"Preis: {room.price} €\n")
#             tk.Label(scrollable_frame, text=room_details, font=("Arial", 12), bg="#eef2ff", justify="left",
#                      anchor="nw").pack(fill="both", padx=10, pady=5)
#
#     def show_selected_hotel_details(self, event):
#         selection = self.tree.selection()
#         if selection:
#             item = self.tree.item(selection[0])
#             hotel_name = item['values'][0]
#
#             hotel = self.search_manager.get_hotels_by_name(hotel_name)[0]
#             self.display_hotel_details(hotel)
#
#     def display_hotel_details(self, hotel):
#         self.clear_details()
#
#         tk.Label(self.details_frame, text=f"Hotel: {hotel.name}", font=("Arial", 16, "bold"), bg="#eef2ff").pack(
#             pady=10)
#         tk.Label(self.details_frame, text=f"Adresse: {hotel.address.street}, {hotel.address.city}", font=("Arial", 14),
#                  bg="#eef2ff").pack(pady=5)
#         tk.Label(self.details_frame, text=f"Sterne: {hotel.stars}", font=("Arial", 14), bg="#eef2ff").pack(pady=5)
#
#         try:
#             max_guests = self.guests_entry.get()
#             max_guests = int(max_guests) if max_guests else 1
#         except ValueError:
#             messagebox.showerror("Ungültiger Wert",
#                                  "Bitte geben Sie gültige numerische Werte für Sterne und max. Gäste ein.")
#             return
#
#         rooms = self.search_manager.get_rooms_by_hotel(hotel.id, max_guests)
#         if not rooms:
#             tk.Label(self.details_frame, text="Keine verfügbaren Zimmer.", font=("Arial", 14), bg="#eef2ff").pack(
#                 pady=10)
#         else:
#             rooms_canvas = tk.Canvas(self.details_frame, bg="#eef2ff")
#             rooms_canvas.pack(side="left", fill="both", expand=True)
#
#             scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=rooms_canvas.yview)
#             scrollbar.pack(side="right", fill="y")
#
#             scrollable_frame = tk.Frame(rooms_canvas, bg="#eef2ff")
#             scrollable_frame.bind(
#                 "<Configure>",
#                 lambda e: rooms_canvas.configure(
#                     scrollregion=rooms_canvas.bbox("all")
#                 )
#             )
#
#             rooms_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
#             rooms_canvas.configure(yscrollcommand=scrollbar.set)
#
#             # Bind mousewheel scrolling to the canvas
#             rooms_canvas.bind_all("<MouseWheel>", lambda event: self.on_mouse_wheel(event, rooms_canvas))
#
#             for room in rooms:
#                 room_details = (f"Zimmernummer: {room['Room Number']}\n"
#                                 f"Typ: {room['Type']}\n"
#                                 f"Max Gäste: {room['Max Guests']}\n"
#                                 f"Beschreibung: {room['Description']}\n"
#                                 f"Ausstattung: {room['Amenities']}\n"
#                                 f"Preis: {room['Price']} €\n")
#                 tk.Label(scrollable_frame, text=room_details, font=("Arial", 12), bg="#eef2ff", justify="left",
#                          anchor="nw").pack(fill="both", padx=10, pady=5)
#
#     def on_mouse_wheel(self, event, canvas):
#         # Scrolls the canvas on mouse wheel scroll
#         canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
#
#     def clear_details(self):
#         for widget in self.details_frame.winfo_children():
#             widget.destroy()


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


    print("Welcome to the hotel search!")
    print("Please enter the desired attributes:")
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