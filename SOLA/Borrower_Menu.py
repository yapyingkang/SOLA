import pwinput
from Sola_class import SOLA
from AccountMgt_class import AccountManager, Borrower



def user_login():
    """User login entry point"""
    sola = SOLA('CatalogueItems.csv', 'BorrowedItems.csv', 'UserData.csv')
    sola.cleanup_borrowed_items() 
    user_mgr = AccountManager()  
    sola.account_manager = user_mgr

    while True:
        print("\n=== Singapore Online Library - User Portal ===")
        print("1. Register")
        print("2. Login")
        print("3. Password Reset")
        print("Q. Exit\n")
        
        choice = input("Choose: ").strip()

        if choice == '1':
            fn = input("\nFirst Name: ").strip()
            ln = input("Last Name: ").strip()
            username = input("Username: ").strip()
            pw = pwinput.pwinput("Password: ")
            
            success, message = user_mgr.register(username, fn, ln, pw)
            
            if success:
                print(f"\nRegistration complete! Your account number is: {message}")
            else:
                print(f"\nAccount registration failed. {message}")

        elif choice == '2':
            username = input("Username: ").strip()
            pw = pwinput.pwinput("Password: ")
            auth = user_mgr.authenticate(username, pw)
            if auth:
                user_mgr.load_users()
                sola.update_all_fines()
                
                borrower = sola.find_borrower(auth['account number'])
                if not borrower:
                    full_name = f"{auth.get('first name', '')} {auth.get('last name', '')}".strip()
                    borrower = Borrower(auth['account number'], full_name)
                    sola.borrowers[borrower.account_number] = borrower
                    sola.borrower_list.add(borrower)
                print(f"Welcome {auth.get('first name', '')}")
                borrower_menu(borrower, sola, user_mgr)
            else:
                print("Invalid credentials.")
                
        elif choice == '3':
            user_mgr.password_reset_flow()

        elif choice.upper() == 'Q':
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")

def borrower_login():
    
    sola = SOLA('CatalogueItems.csv', 'BorrowedItems.csv', 'UserData.csv')
    sola.cleanup_borrowed_items() 
    user_mgr = AccountManager()  
    sola.account_manager = user_mgr

    while True:
        print("\n=== Singapore Online Library - User Portal ===")
        print("1. Register")
        print("2. Login")
        print("3. Password Reset")
        print("Q. Exit\n")
        
        choice = input("Choose: ").strip()

        if choice == '1':
            fn = input("\nFirst Name: ").strip()
            ln = input("Last Name: ").strip()
            username = input("Username: ").strip()
            pw = pwinput.pwinput("Password: ")
            
            success, message = user_mgr.register(username, fn, ln, pw)
            
            if success:
                print(f"\nRegistration complete! Your account number is: {message}")
            else:
                print(f"\nAccount registration failed. {message}")

        elif choice == '2':
            username = input("Username: ").strip()
            pw = pwinput.pwinput("Password: ")
            auth = user_mgr.authenticate(username, pw)
            if auth:
                user_mgr.load_users()
                sola.update_all_fines()
                
                borrower = sola.find_borrower(auth['account number'])
                if not borrower:
                    full_name = f"{auth.get('first name', '')} {auth.get('last name', '')}".strip()
                    borrower = Borrower(auth['account number'], full_name)
                    sola.borrowers[borrower.account_number] = borrower
                    sola.borrower_list.add(borrower)
                print(f"Welcome {auth.get('first name', '')}")
                borrower_menu(borrower, sola, user_mgr)
            else:
                print("Invalid credentials.")
                
        elif choice == '3':
            user_mgr.password_reset_flow()

        elif choice.upper() == 'Q':
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")

def borrower_menu(borrower, sola, user_mgr):
    account_number = borrower.account_number  

    while True:
        user_mgr.load_users()
        user_data = user_mgr.find_user(account_number)
        
        sola.update_all_fines()
        
        if user_data:
            borrower.fines = float(user_data.get('fines', 0.0))
            try:
                rented_items = user_data.get('rented items', [])
                if isinstance(rented_items, list):
                    borrower.borrowed_items = rented_items
            except:
                pass
        
        print("\n--- User Menu ---")
        print("1. Borrow an item")
        print("2. Return an item")
        print("3. Search the catalogue")
        print("4. View details of an item") 
        print("5. Search books by author's name")  
        print("6. Check due dates of borrowed items")
        print("7. Pay a fine")
        print("Q. Logout \n")

        choice = input(" What would you like to do?: ").strip()
        if not choice:
            continue
        if choice == '1':
            if getattr(borrower, 'fines', 0) > 0:
                print("You have outstanding fines. Please pay fines before borrowing.")
                continue
            if len(getattr(borrower, 'borrowed_items', [])) >= getattr(borrower, 'max_borrowing_limit', 8):
                print("You are allowed to borrow a maximum of 8 items.")
                continue
            title = input("Enter title to borrow: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue
            print(sola.borrow_item(account_number, title))
            
        elif choice == '2':
            titles = sola.list_borrowed_items(account_number)
            if not titles:
                print("No borrowed items to return.")
                continue
            print("Your borrowed items:")
            for i, title in enumerate(titles, 1):
                print(f"{i}. {title}")
            try:
                idx = int(input(f"Select item to return (1-{len(titles)}) or 0 to return all: "))
                if idx == 0:
                    success_count = 0
                    for t in titles:
                        result = sola.return_item(account_number, t)
                        if result:
                            success_count += 1
                            print(f"Returned '{t}'")
                    print(f"\nTotal: Returned {success_count}/{len(titles)} item(s) successfully.")
                    borrower.borrowed_items = sola.list_borrowed_items(account_number)
                elif 1 <= idx <= len(titles):
                    selected_title = titles[idx - 1]
                    result = sola.return_item(account_number, selected_title)
                    if result:
                        print(f"Returned '{selected_title}' successfully.")
                        borrower.borrowed_items = sola.list_borrowed_items(account_number)
                    else:
                        print(f"Failed to return '{selected_title}'.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

        elif choice == '3':
            keyword = input("Search keyword (title/category/language/year/author): ").strip()
            if not keyword:
                print("Keyword cannot be empty.")
                continue
            results = (
                sola.search_catalogue(title=keyword)
                + sola.search_catalogue(category=keyword)
                + sola.search_catalogue(language=keyword)
                + sola.search_catalogue(year_published=keyword)
                + sola.search_catalogue(author=keyword)
            )
            unique_results = {item.title: item for item in results}.values()
            if not list(unique_results):
                print("No items found matching the keyword.")
                continue
            print(f"{'Title':40} | {'Category':15} | {'Status':10}")
            print('-' * 70)
            for item in unique_results:
                print(f"{item.title:40} | {item.category:15} | {item.status:10}")

        elif choice == '4': 
            search_str = input("Enter part of title to view details: ").strip()
            if not search_str:
                print("Search string cannot be empty.")
                continue
            results = sola.search_catalogue(title=search_str)
            if not results:
                print("No items found.")
                continue
            elif len(results) == 1:
                results[0].display()
            else:
                print("Multiple matches:")
                for i, item in enumerate(results, 1):
                    print(f"{i}. {item.title}")
                try:
                    idx = int(input(f"Select item number (1-{len(results)}): "))
                    if 1 <= idx <= len(results):
                        results[idx - 1].display()
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input.")

        elif choice == '5':  
            author = input("Enter author name: ").strip()
            if not author:
                print("Author name cannot be empty.")
                continue
            results = sola.search_catalogue(author=author)
            if results:
                print(f"Items by {author}:")
                for item in results:
                    print(f"- {item.title}")
            else:
                print("No items found by this author.")

        elif choice == '6':
            borrowed = sola.list_borrowed_items(account_number)
            if not borrowed: 
                print("No borrowed items.")
            else:
                print(f"\n{'Title':<50} | {'Due Date':<12}")
                print("-" * 65)
                borrowed_df = sola.borrowed[sola.borrowed['account number'].astype(str).str.strip() == str(account_number).strip()]
                for _, row in borrowed_df.iterrows():
                    title = row['title'][:47] + '...' if len(row['title']) > 50 else row['title']
                    print(f"{title:<50} | {row['date due']:<12}")

        elif choice == '7':
            print("\n--- Pay Fine ---")
            
            user_mgr.load_users()
            user_data = user_mgr.find_user(account_number)
            if user_data:
                borrower.fines = float(user_data.get('fines', 0.0))
            
            if getattr(borrower, 'fines', 0) <= 0:
                print("You have no outstanding fines.")
            else:
                print(f"Your outstanding fines: ${borrower.fines:.2f}")
                try:
                    amount = float(input("Enter amount to pay: $"))
                    if amount <= 0:
                        print("Amount must be positive.")
                    elif amount > borrower.fines + 0.01:
                        print("You cannot pay more than your outstanding fines.")
                    else:
                        new_fine_amount = max(0.0, borrower.fines - amount)
                        
                        if user_mgr.update_fines(account_number, new_fine_amount):
                            borrower.fines = new_fine_amount
                            print(f"Payment of ${amount:.2f} successful.")
                            print(f"Remaining fines: ${borrower.fines:.2f}")
                        else:
                            print("Error: Unable to save fine payment.")
                        
                except ValueError:
                    print("Invalid amount entered.")

        elif choice.upper() == 'Q':
            print("Logging out...")
            break

        else:
            print("Invalid option.")


if __name__ == '__main__':
    user_login()
