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


    engine = create_engine(f'sqlite:///{db_file}')

    session = scoped_session(sessionmaker(bind=engine))
    query = select(Hotel)
    print(query)
    hotels = session.execute(query).scalars().all()

    for hotel in hotels:
        print(hotel.address)
    city = input("Enter city: ")

    query_1 = select(Hotel).join(Address).where(func.lower(Address.city) == city.lower())

    hotels = session.execute(query_1).scalars().all()

    for hotel in hotels:
        print(hotel)

    query_2 = select(Hotel).where(Hotel.stars > 3)

    hotels = session.execute(query_2).scalars().all()

    for hotel in hotels:
        print(hotel)

    # name = input("Enter name: ")
    #
    # query_3 = select(Hotel).where(Hotel.name.like(f"%{name}%"))
    # print(query_3)
    # hotels = session.execute(query_3).scalars().all()
    #
    # for hotel in hotels:
    #     print(hotel)


#  Sujani is the best