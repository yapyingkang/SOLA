
from AccountMgt_class import AccountManager
from Sola_class import SOLA
from Admin_Menu import admin_login
from Borrower_Menu import borrower_login

def main():
    account_manager = AccountManager()
    sola = SOLA('CatalogueItems.csv', 'BorrowedItems.csv', 'UserData.csv')
    sola.account_manager = account_manager
    
    while True:
        print("\n=== SOLA Library System ===")
        print("1. Borrower Login")
        print("2. Admin Login")
        print("Q. Exit\n")
        
        choice = input("Select login type: ").strip()
        
        if choice == '1':
            borrower_login()
        elif choice == '2':
            admin_login()
        elif choice.upper() == 'Q':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()

