import pwinput
from AccountMgt_class import validate_password_policy, Admin , AccountManager
from Sola_class import SOLA

def admin_login():
    """Admin login entry point"""
    sola = SOLA('CatalogueItems.csv', 'BorrowedItems.csv', 'UserData.csv')
    sola.cleanup_borrowed_items() 
    user_mgr = AccountManager()  
    sola.account_manager = user_mgr
    admin_obj = Admin(sola, account_manager=user_mgr)

    print("\n=== Singapore Online Library - Admin Portal ===")
    pw = pwinput.pwinput("Admin password: ")
    
    if admin_obj.authenticate(pw):
        print("\nWelcome Admin!")
        admin_menu(admin_obj, sola, user_mgr)
        return True
    else:
        print("\nInvalid admin password. Access denied.")
        return False

def admin_menu(admin, sola, user_mgr):
  
    while True:
        print("\n=== Admin Menu ===")
        print("1. Create Borrower Account")
        print("2. Search Borrower")
        print("3. Update Borrower Information")
        print("4. Delete Borrower Account")
        print("5. Add Item to Catalogue")
        print("6. Update Catalogue Item")
        print("7. Remove Item from Catalogue")
        print("8. Search Catalogue")
        print("9. View Borrower's Borrowed Items")
        print("10. View All Borrowed Items Report")
        print("11. Process Fine Payment")
        print("12. View Fines and Generate Report")
        print("Q. Logout\n")
        
        choice = input("Select option: ").strip()
        
        if not choice:
            continue
        
        if choice == '1':
            print("\n--- Create Borrower Account ---")
            
            first_name = input("Enter first name: ").strip()
            if not first_name:
                print("First name cannot be empty.")
                continue
            
            last_name = input("Enter last name: ").strip()
            if not last_name:
                print("Last name cannot be empty.")
                continue

            username = input("Enter username: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            
            password = pwinput.pwinput("Enter password: ")
            if not password:
                print("Password cannot be empty.")
                continue
            
            success, result = user_mgr.register(username, first_name, last_name, password)
            if success:
                print(f"Account created successfully! Account number: {result}")
                admin.refresh_borrowers()
            else:
                print(f"Error: {result}")

        elif choice == '2':
            print("\n--- Search Borrower ---")
            account_num = input("Enter account number: ").strip()
            if not account_num:
                print("Account number cannot be empty.")
                continue
            
            user_mgr.load_users()
            borrower = sola.find_borrower(account_num)
            if borrower:
                print(f"\nAccount Number: {borrower.account_number}")
                print(f"Username: {borrower.username}")
                print(f"Borrowed Items: {len(borrower.borrowed_items)}/{borrower.max_borrowing_limit}")
                print(f"Fines: ${borrower.fines:.2f}")
            else:
                print(f"No borrower found with account number {account_num}.")
        
        elif choice == '3':
            print("\n--- Update Borrower Information ---")
            account_num = input("Enter account number: ").strip()
            if not account_num:
                print("Account number cannot be empty.")
                continue
            
            user_mgr.load_users()
            borrower = sola.find_borrower(account_num)
            if not borrower:
                print(f"No borrower found with account number {account_num}.")
                continue
            
            print(f"\nCurrent First Name: {borrower.first_name}")
            new_first_name = input("Enter new first name (or press Enter to skip): ").strip()
            if new_first_name:
                if user_mgr.update_first_name(account_num, new_first_name):
                    borrower.first_name = new_first_name
                else:
                    print("Failed to update first name.")
            
            print(f"Current Last Name: {borrower.last_name}")
            new_last_name = input("Enter new last name (or press Enter to skip): ").strip()
            if new_last_name:
                if user_mgr.update_last_name(account_num, new_last_name):
                    borrower.last_name = new_last_name
                else:
                    print("Failed to update last name.")
            
            print(f"Current Username: {borrower.username}")
            new_username = input("Enter new username (or press Enter to skip): ").strip()
            if new_username:
                if user_mgr.update_username(account_num, new_username):
                    borrower.username = new_username
                else:
                    print("Failed to update username.")
            
            update_pw = input("Update password? (y/n): ").strip().lower()
            if update_pw == 'y':
                new_password = pwinput.pwinput("Enter new password: ")
                confirm_password = pwinput.pwinput("Confirm new password: ")
                
                if new_password != confirm_password:
                    print("Passwords do not match.")
                else:
                    is_valid, error_msg = validate_password_policy(new_password, borrower.username)
                    if not is_valid:
                        print(error_msg)
                    else:
                        if user_mgr.update_password(account_num, new_password):
                            print("Password updated successfully.")
                        else:
                            print("Failed to update password.")
            
            print(f"Current Fines: ${borrower.fines:.2f}")
            adjust_fine = input("Adjust fine? (y/n): ").strip().lower()
            if adjust_fine == 'y':
                try:
                    new_fine = float(input("Enter new fine amount: "))
                    if new_fine >= 0:
                        if user_mgr.update_fines(account_num, new_fine):
                            borrower.fines = new_fine
                            print(f"Fine updated to ${new_fine:.2f}.")
                        else:
                            print("Error: Failed to update fine.")
                    else:
                        print("Fine must be non-negative.")
                except ValueError:
                    print("Invalid amount.")

        elif choice == '4':
            print("\n--- Delete Borrower Account ---")
            account_num = input("Enter account number to delete: ").strip()
            if not account_num:
                print("Account number cannot be empty.")
                continue
            
            admin.remove_borrower(account_num)
        
        elif choice == '5':
            print("\n--- Add Item to Catalogue ---")
            title = input("Title: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue
            
            std_no = input("Standard Number (ISBN/ISSN): ").strip()
            author = input("Author/Creator: ").strip()
            year = input("Year Published: ").strip()
            publisher = input("Publisher: ").strip()
            category = input("Category: ").strip()
            language = input("Language: ").strip()
            item_type = input("Type (book/magazine/audio): ").strip()
            
            item_dict = {
                'title': title,
                'std_no': std_no,
                'author': author,
                'year_published': year,
                'publisher': publisher,
                'category': category,
                'language': language,
                'type': item_type,
                'status': 'available'
            }
            
            result = sola.add_item(item_dict)
            print(result)
        
        elif choice == '6':
            print("\n--- Update Catalogue Item ---")
            title = input("Enter title of item to update: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue
            
            matches = sola.catalogue[sola.catalogue['title'].str.contains(title, case=False, na=False, regex=False)]
            if matches.empty:
                print("No item found with that title.")
                continue
            
            if len(matches) > 1:
                print("Multiple items found:")
                for idx, row in enumerate(matches.itertuples(), 1):
                    print(f"{idx}. {row.title}")
                try:
                    selection = int(input("Select item number: "))
                    if 1 <= selection <= len(matches):
                        title = matches.iloc[selection - 1]['title']
                    else:
                        print("Invalid selection.")
                        continue
                except ValueError:
                    print("Invalid input.")
                    continue
            else:
                title = matches.iloc[0]['title']
            
            print("\nLeave field blank to skip update.")
            updates = {}
            
            new_author = input("New author (current: " + str(matches[matches['title'] == title].iloc[0]['author']) + "): ").strip()
            if new_author:
                updates['author'] = new_author
            
            new_status = input("New status (available/unavailable): ").strip().lower()
            if new_status in ['available', 'unavailable']:
                updates['status'] = new_status
            
            if updates:
                result = sola.update_item(title, **updates)
                print(result)
            else:
                print("No updates made.")
        
        elif choice == '7':
            print("\n--- Remove Item from Catalogue ---")
            title = input("Enter title of item to remove: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue
            
            confirm = input(f"Are you sure you want to remove '{title}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                result = sola.remove_item(title)
                print(result)
            else:
                print("Removal cancelled.")
        
        elif choice == '8':
            print("\n--- Search Catalogue ---")
            keyword = input("Search keyword (title/author/category): ").strip()
            if not keyword:
                print("Keyword cannot be empty.")
                continue
            
            results = (
                sola.search_catalogue(title=keyword)
                + sola.search_catalogue(author=keyword)
                + sola.search_catalogue(category=keyword)
            )
            
            unique_results = {item.title: item for item in results}.values()
            if not list(unique_results):
                print("No items found.")
                continue
            
            print(f"\n{'Title':40} | {'Author':20} | {'Status':10}")
            print('-' * 75)
            for item in unique_results:
                print(f"{item.title[:40]:40} | {item.author[:20]:20} | {item.status:10}")
        
        elif choice == '9':
            print("\n--- View Borrower's Borrowed Items ---")
            account_num = input("Enter borrower account number: ").strip()
            if not account_num:
                print("Account number cannot be empty.")
                continue
            
            borrowed_items = sola.list_borrowed_items(account_num)
            if not borrowed_items:
                print(f"No borrowed items for account {account_num}.")
                continue
            
            borrowed_df = sola.borrowed[
                sola.borrowed['account number'].astype(str).str.strip() == account_num
            ]
            
            print(f"\nBorrowed items for account {account_num}:")
            print(f"{'Title':<50} | {'Due Date':<12}")
            print("-" * 65)
            for _, row in borrowed_df.iterrows():
                title_display = row['title'][:47] + '...' if len(row['title']) > 50 else row['title']
                print(f"{title_display:<50} | {row['date due']:<12}")
        
        elif choice == '10':
            print("\n--- All Borrowed Items Report ---")
            if sola.borrowed.empty:
                print("No items currently borrowed.")
                continue
            
            print(f"{'Account':<15} | {'Title':<40} | {'Due Date':<12}")
            print("-" * 70)
            for _, row in sola.borrowed.iterrows():
                title_display = row['title'][:37] + '...' if len(row['title']) > 40 else row['title']
                print(f"{row['account number']:<15} | {title_display:<40} | {row['date due']:<12}")
            
            print(f"\nTotal borrowed items: {len(sola.borrowed)}")
        
        elif choice == '11':
            print("\n--- Process Fine Payment ---")
            account_num = input("Enter borrower account number: ").strip()
            if not account_num:
                print("Account number cannot be empty.")
                continue
            
            user_mgr.load_users()
            borrower = sola.find_borrower(account_num)
            if not borrower:
                print(f"No borrower found with account number {account_num}.")
                continue
            
            if borrower.fines <= 0:
                print(f"Account {account_num} has no outstanding fines.")
                continue
            
            print(f"Outstanding fines: ${borrower.fines:.2f}")
            try:
                amount = float(input("Enter payment amount: "))
                if amount <= 0:
                    print("Amount must be positive.")
                elif amount > borrower.fines + 0.01:
                    print("Payment amount exceeds outstanding fines.")
                else:
                    new_fine_amount = max(0.0, borrower.fines - amount)
                    if user_mgr.update_fines(account_num, new_fine_amount):
                        borrower.fines = new_fine_amount
                        print(f"Payment of ${amount:.2f} processed.")
                        print(f"Remaining fines: ${borrower.fines:.2f}")
                    else:
                        print("Error: Failed to process payment.")
            except ValueError:
                print("Invalid amount.")
                
        elif choice == '12':
             sola.generate_fine_report()

        elif choice.upper() == 'Q':
            print("Logging out...")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    admin_login()
