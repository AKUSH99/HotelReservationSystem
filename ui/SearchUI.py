from business.SearchManager import SearchManager

class SearchUI():
    def __init__(self, session, back=None):
        self.search_manager = SearchManager(session)
        self.back = back

    def show_menu(self):
        print("1. Show all Hotels")
        print("2. Search by Name")
        print("3. Exit")

    def user_choice(self):
        choice = input("Choose Option (1-3): ")
        return choice

    def navigate(self, choice):
        match (choice):
            case "1":
                hotels = self.search_manager.get_all_hotels()
                for hotel in hotels:
                    print(hotel)
                return self
            case "2":
                searched_name = input("Enter hotel name: ")
                hotels = self.search_manager.get_hotels_by_name(searched_name)
                for hotel in hotels:
                    print(hotel)
                return self
            case "3":
                print("Thank you for visiting. Goodbye!")
                return self.back

            case _:
                print("Invalid")
                return self


if __name__ == "__main__":
    current_ui = SearchUI("../data/database.db")
    while current_ui is not None:
        current_ui.show_menu()
        choice = current_ui.user_choice()
        current_ui = current_ui.navigate(choice)