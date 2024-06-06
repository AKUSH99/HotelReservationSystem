import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from data_models.models import *
from data_access.data_base import init_db
from sqlalchemy import select, func, and_, or_


class SearchManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def search_hotels_by_city_date_guests_stars(self, city=None, start_date=None, end_date=None, max_guest=1,
                                                stars=None):
        query = select(Hotel).join(Address).join(Room).outerjoin(Booking, Room.number == Booking.room_number).where(
            and_(
                Room.max_guests >= max_guest,
                or_(
                    Booking.id.is_(None),
                    and_(
                        Booking.end_date <= start_date if start_date else True,
                        Booking.start_date >= end_date if end_date else True
                    )
                )
            )
        ).distinct()

        if city:
            query = query.where(func.lower(Address.city) == city.lower())
        if stars is not None:
            query = query.where(Hotel.stars == stars)

        result = self.__session.execute(query).scalars().all()
        return result

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

    def get_hotels_by_name(self, name):
        query = select(Hotel).where(Hotel.name == name)
        hotels = self.__session.execute(query).scalars().all()
        return hotels


class HotelReservationApp(tk.Tk):
    def __init__(self, search_manager):
        super().__init__()
        self.search_manager = search_manager
        self.title("Hotelreservierungssystem")
        self.geometry("1200x800")
        self.configure(bg="#f5f5f5")

        # Hauptcontainer für das gesamte Layout
        main_container = tk.Frame(self, bg="#f5f5f5")
        main_container.pack(fill="both", expand=True)

        # Linker Frame für die Suchmaske
        left_frame = tk.Frame(main_container, bg="#e8f0fe", width=300)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Rechter Frame für die Suchergebnisse und Details
        right_frame = tk.Frame(main_container, bg="#f0f4ff")
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Suchmaske
        tk.Label(left_frame, text="Hotelsuche mit Enter bestätigen", font=("Arial", 18, "bold"), bg="#e8f0fe").pack(pady=10)

        self.city_entry = self.create_entry(left_frame, "Stadt (optional):")
        self.stars_entry = self.create_entry(left_frame, "Sterne (optional):")
        self.guests_entry = self.create_entry(left_frame, "Max Gäste (optional):")

        # Anpassung der Datumseingabe als Textfeld mit Validierung
        self.start_date_entry = self.create_date_entry(left_frame, "Startdatum (DD.MM.YYYY, optional):")
        self.end_date_entry = self.create_date_entry(left_frame, "Enddatum (DD.MM.YYYY, optional):")

        search_btn = tk.Button(left_frame, text="Suchen", command=self.search_hotels, font=("Arial", 14), bg="#4CAF50",
                               fg="white")
        search_btn.pack(pady=10)

        # Bind Enter key to search_hotels method
        self.bind('<Return>', lambda event: self.search_hotels())

        # Ergebnisse und Details
        instruction_label = tk.Label(right_frame,
                                     text="Klicken Sie auf ein Hotel, um die verfügbaren Räume anzuzeigen.",
                                     font=("Arial", 14), bg="#E4EC13")
        instruction_label.pack(pady=10)

        self.results_frame = tk.Frame(right_frame, bg="#f0f4ff")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.results_frame, columns=("Name", "Stadt", "Sterne"), show='headings', height=10)
        self.tree.heading("Name", text="Name")
        self.tree.heading("Stadt", text="Stadt")
        self.tree.heading("Sterne", text="Sterne")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.show_selected_hotel_details)

        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.details_frame = tk.Frame(right_frame, bg="#eef2ff", relief="groove", borderwidth=2)
        self.details_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_entry(self, parent, label_text):
        frame = tk.Frame(parent, bg="#e8f0fe")
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=label_text, font=("Arial", 12), bg="#e8f0fe").pack(side="left")
        entry = tk.Entry(frame, font=("Arial", 12))
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def create_date_entry(self, parent, label_text):
        frame = tk.Frame(parent, bg="#e8f0fe")
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=label_text, font=("Arial", 12), bg="#e8f0fe").pack(side="left")
        entry = tk.Entry(frame, font=("Arial", 12))
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def parse_date(self, date_str):
        if date_str:
            try:
                return datetime.strptime(date_str, "%d.%m.%Y").strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Ungültiges Datum", "Bitte geben Sie das Datum im Format DD.MM.YYYY ein.")
                return None
        return None

    def search_hotels(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.clear_details()

        city = self.city_entry.get()
        stars = self.stars_entry.get()
        max_guests = self.guests_entry.get()
        start_date = self.parse_date(self.start_date_entry.get())
        end_date = self.parse_date(self.end_date_entry.get())

        try:
            stars = int(stars) if stars else None
            max_guests = int(max_guests) if max_guests else 1
        except ValueError:
            messagebox.showerror("Ungültiger Wert",
                                 "Bitte geben Sie gültige numerische Werte für Sterne und max. Gäste ein.")
            return

        hotels = self.search_manager.search_hotels_by_city_date_guests_stars(
            city, start_date, end_date, max_guests, stars
        )

        if not hotels:
            messagebox.showinfo("Keine Hotels gefunden",
                                "Es wurden keine Hotels gefunden, die Ihren Kriterien entsprechen.")
        else:
            for hotel in hotels:
                self.tree.insert("", "end", values=(hotel.name, hotel.address.city, hotel.stars))

    def show_selected_hotel_details(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            hotel_name = item['values'][0]

            hotel = self.search_manager.get_hotels_by_name(hotel_name)[0]
            self.display_hotel_details(hotel)

    def display_hotel_details(self, hotel):
        self.clear_details()

        tk.Label(self.details_frame, text=f"Hotel: {hotel.name}", font=("Arial", 16, "bold"), bg="#eef2ff").pack(
            pady=10)
        tk.Label(self.details_frame, text=f"Adresse: {hotel.address.street}, {hotel.address.city}", font=("Arial", 14),
                 bg="#eef2ff").pack(pady=5)
        tk.Label(self.details_frame, text=f"Sterne: {hotel.stars}", font=("Arial", 14), bg="#eef2ff").pack(pady=5)

        rooms = self.search_manager.get_rooms_by_hotel(hotel.id, 1)
        if not rooms:
            tk.Label(self.details_frame, text="Keine verfügbaren Zimmer.", font=("Arial", 14), bg="#eef2ff").pack(
                pady=10)
        else:
            rooms_canvas = tk.Canvas(self.details_frame, bg="#eef2ff")
            rooms_canvas.pack(side="left", fill="both", expand=True)

            scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=rooms_canvas.yview)
            scrollbar.pack(side="right", fill="y")

            scrollable_frame = tk.Frame(rooms_canvas, bg="#eef2ff")
            scrollable_frame.bind(
                "<Configure>",
                lambda e: rooms_canvas.configure(
                    scrollregion=rooms_canvas.bbox("all")
                )
            )

            rooms_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            rooms_canvas.configure(yscrollcommand=scrollbar.set)

            for room in rooms:
                room_details = (f"Zimmernummer: {room['Room Number']}\n"
                                f"Typ: {room['Type']}\n"
                                f"Max Gäste: {room['Max Guests']}\n"
                                f"Beschreibung: {room['Description']}\n"
                                f"Ausstattung: {room['Amenities']}\n"
                                f"Preis: {room['Price']} €\n")
                tk.Label(scrollable_frame, text=room_details, font=("Arial", 12), bg="#eef2ff", justify="left",
                         anchor="nw").pack(fill="both", padx=10, pady=5)

    def clear_details(self):
        for widget in self.details_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    db_file = "../data/database.db"
    search_manager = SearchManager(db_file)

    app = HotelReservationApp(search_manager)
    app.mainloop()
