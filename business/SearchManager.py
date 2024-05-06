from data_models.models import *
from data_access.data_base import init_db
from sqlalchemy import select, create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path



if __name__ == '__main__':
    db_file = "../data/test.db"
    db_file_path = Path(db_file)
    if not db_file_path.is_file():
        print("Database file not found.")
        init_db(db_file, generate_example_data=True)
    else:
        print("Database file found.")


    class SearchManagerTest:
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

        def get_hotels_by_city_and_stars(self, city, stars):
            query = select(Hotel).join(Address).where((Address.city.like(f"%{city}%") & (Hotel.stars == stars)))
            hotels = self.__session.execute(query).scalars().all()
            return hotels

        def get_hotels_by_city_room_guest_stars(self, city, max_guest, stars):
            query = select(Hotel).join(Address).join(Room).where(Address.city.like(f"%{city}%") & (Hotel.stars == stars) & (Room.max_guests == max_guest))
            hotels = self.__session.execute(query).scalars().all()
            return hotels


    if __name__ == "__main__":
        sm = SearchManagerTest("../data/database.db")
        hotels = sm.get_all_hotels()
        for hotel in hotels:
            print(hotel)


        # # User Story 1.1.1.
        # # Ich möchte alle Hotels in einer Stadt durchsuchen, damit ich
        # # das Hotel nach meinem bevorzugten Standort (Stadt) auswählen kann.
        # city = input("Enter city: ")
        # hotel_city = sm.get_hotels_by_city(city)
        # for hotel in hotel_city:
        #     print(hotel)
        #
        #
        # # User Story 1.1.2
        # # Ich möchte alle Hotels in einer Stadt nach der Anzahl der
        # # Sterne durchsuchen.
        # city = str(input("Enter city: "))
        # stars = int(input("Enter stars 1 to 5: "))
        # hotel_stars = sm.get_hotels_by_city_and_stars(city=city, stars=stars)
        # if not hotel_stars and stars == stars:
        #     print("No hotels found with given amount of stars.! ")
        # else:
        #     for hotel in hotel_stars:
        #         print(hotel)


        # 1.1.3. Ich möchte alle Hotels in einer Stadt durchsuchen, die Zimmer
        # haben, die meiner Gästezahl entsprechen (nur 1 Zimmer pro
        # Buchung), entweder mit oder ohne Anzahl der Sterne.
        city = str(input("Enter city: "))
        max_guest = int(input("Enter max guests: "))
        stars = int(input("Enter stars 1 to 5 (optional): "))
        hotel_city_max_guest_stars = sm.get_hotels_by_city_room_guest_stars(city=city, max_guest=max_guest, stars=stars)
        for hotel in hotel_city_max_guest_stars:
            print(hotel.rooms)

