from data_models.models import Hotel
from data_access.data_base import init_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path


class InventoryManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{database_file}", echo=False)
        self.__Session = scoped_session(sessionmaker(bind=self.__engine))

    # Methode zum Hinzufügen eines neuen Hotels
    def add_hotel(self, name, stars, address_id):
        session = self.__Session()
        try:
            new_hotel = Hotel(name=name, stars=stars, address_id=address_id)
            session.add(new_hotel)
            session.commit()
            print(f"Hotel '{name}' erfolgreich hinzugefügt.")
        except Exception as e:
            session.rollback()
            print(f"Fehler beim Hinzufügen des Hotels: {e}")
        finally:
            session.close()


# Beispielaufruf der Methode außerhalb der Klasse
if __name__ == "__main__":
    inventory_manager = InventoryManager('/mnt/data/database.db')
    inventory_manager.add_hotel('Beispiel Hotel', 4, 1)
