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
            query = select(Hotel).join(Address).where(func.lower(Address.city) == city.lower())
            hotels = self.__session.execute(query).scalars().all()
            return hotels


    if __name__ == "__main__":
        sm = SearchManagerTest("../data/database.db")
        hotels = sm.get_all_hotels()
        for hotel in hotels:
            print(hotel)

        # name = input("Enter name hotel name: ")
        # hotel_name = sm.get_hotels_by_name(name)
        # for hotel in hotel_name:
        #     print(hotel)

        city = input("Enter city name: ")
        hotel_city = sm.get_hotels_by_city(city)
        for hotel in hotel_city:
            print(hotel)

