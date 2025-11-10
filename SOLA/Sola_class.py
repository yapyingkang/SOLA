import pandas as pd
from datetime import datetime, timedelta
import ast
import os


class Item:
    def __init__(self, data_dict):
        self.title = str(data_dict.get('title', '') or '')
        self.category = str(data_dict.get('category', '') or '')
        self.language = str(data_dict.get('language', '') or '')
        self.year_published = str(data_dict.get('year published', '') or '')
        self.std_no = str(data_dict.get('std_no', '') or '')
        self.author = str(data_dict.get('author', '') or '')
        self.type = str(data_dict.get('type', '') or '')
        self.audio_format = str(data_dict.get('audio format', '') or '')
        self.status = str(data_dict.get('status', 'available')).strip().lower()

    def display(self):
        print("\n" + "="*60)
        print(f"Title: {self.title}")
        print(f"Category: {self.category}")
        print(f"Language: {self.language}")
        print(f"Year Published: {self.year_published}")
        print(f"STD No: {str(self.std_no)}")
        print(f"Author: {self.author}")
        print(f"Type: {self.type}")
        print(f"Audio Format: {self.audio_format if self.audio_format else 'N/A'}")
        print(f"Status: {self.status.upper()}")
        print("="*60 + "\n")


class Borrower:
    def __init__(self, account_number, name='', fines=0.0, borrowed_items=None, max_borrowing_limit=8, username=''):
        self.account_number = str(account_number) if account_number is not None else ''
        self.name = str(name or '')
        try:
            self.fines = float(fines)
        except:
            self.fines = 0.0
        
        if borrowed_items is None:
            self.borrowed_items = []
        elif isinstance(borrowed_items, str):
            try:
                bi = ast.literal_eval(borrowed_items)
                self.borrowed_items = bi if isinstance(bi, list) else []
            except:
                self.borrowed_items = []
        elif isinstance(borrowed_items, list):
            self.borrowed_items = borrowed_items
        else:
            self.borrowed_items = []
        
        self.max_borrowing_limit = int(max_borrowing_limit)
        self.username = str(username)


class BorrowerNode:
    def __init__(self, borrower):
        self.borrower = borrower
        self.next = None
        self.prev = None


class BorrowerList:
    def __init__(self):
        self.head = None
        self.tail = None
    
    def add(self, borrower):
        node = BorrowerNode(borrower)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
    
    def find(self, account_number):
        account_number = str(account_number)
        current = self.head
        while current:
            if getattr(current.borrower, 'account_number', None) == account_number:
                return current.borrower
            current = current.next
        return None
    
    def remove(self, account_number):
        account_number = str(account_number)
        current = self.head
        while current:
            if getattr(current.borrower, 'account_number', None) == account_number:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                return True
            current = current.next
        return False


class LibraryBST:
    def __init__(self):
        self.root = None
    
    def insert(self, item):
        if not isinstance(item, Item):
            item = Item(item)
        if not self.root:
            self.root = TreeNode(item)
        else:
            self._insert(self.root, item)
    
    def _insert(self, node, item):
        if item.title.lower() < node.item.title.lower():
            if not node.left:
                node.left = TreeNode(item)
            else:
                self._insert(node.left, item)
        else:
            if not node.right:
                node.right = TreeNode(item)
            else:
                self._insert(node.right, item)
    
    def search(self, title):
        return self._search(self.root, (title or '').strip().lower())
    
    def _search(self, node, title):
        if not node:
            return None
        node_title = node.item.title.lower()
        if title == node_title:
            return node.item
        elif title < node_title:
            return self._search(node.left, title)
        else:
            return self._search(node.right, title)


class TreeNode:
    def __init__(self, item):
        self.item = item
        self.left = None
        self.right = None


class SOLA:
    def __init__(self, catalogue_csv, borrowed_csv, borrower_csv=None):
        self.catalogue_csv = catalogue_csv
        self.borrowed_csv = borrowed_csv
        self.borrower_csv = borrower_csv
        self.catalogue = pd.DataFrame()
        self.borrowed = pd.DataFrame()
        self.borrowers = {}
        self.borrower_list = BorrowerList()
        self.load_catalogue()
        self.load_borrowed()
        if self.borrower_csv:
            self.load_borrowers()
    
    def load_catalogue(self):
        try:
            if not os.path.exists(self.catalogue_csv):
                self.catalogue = pd.DataFrame(columns=['title', 'category', 'language', 'year published', 'std_no', 'author', 'type', 'audio format', 'status'])
                return
            
            df = pd.read_csv(self.catalogue_csv, dtype={'std_no': str})
            
            if df.empty:
                self.catalogue = pd.DataFrame(columns=['title', 'category', 'language', 'year published', 'std_no', 'author', 'type', 'audio format', 'status'])
                return
            
            df.columns = [col.strip().lower() for col in df.columns]
            
            for col in ['title', 'category', 'language', 'year published', 'std_no', 'author', 'type', 'audio format', 'status']:
                if col not in df.columns:
                    df[col] = ''
            
            df['status'] = df['status'].fillna('available').str.lower()
            
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].dtype == 'string':
                    df[col] = df[col].fillna('')
                else:
                    df[col] = df[col].fillna(0)
            
            df['std_no'] = df['std_no'].astype(str).str.replace('.0', '', regex=False).str.strip()
            self.catalogue = df.copy()
            
        except Exception as e:
            print(f"Error loading catalogue: {e}")
            self.catalogue = pd.DataFrame(columns=['title', 'category', 'language', 'year published', 'std_no', 'author', 'type', 'audio format', 'status'])
    
    def save_catalogue(self):
        """Centralized method to save catalogue with proper quoting"""
        try:
            self.catalogue.to_csv(self.catalogue_csv, index=False, quoting=1)
        except Exception as e:
            print(f"Error saving catalogue: {e}")
    
    def load_borrowers(self):
        if not self.borrower_csv:
            return
        self.borrower_list = BorrowerList()
        self.borrowers = {}
        try:
            if not os.path.exists(self.borrower_csv):
                return
            
            df = pd.read_csv(self.borrower_csv, dtype={'account number': str})
            
            if df.empty:
                return
            
            df.columns = [col.strip().lower() for col in df.columns]
            
            for col in ['account number', 'first name', 'last name', 'username', 'rented items', 'fines', 'hashedpassword']:
                if col not in df.columns:
                    df[col] = ''
            
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].dtype == 'string':
                    df[col] = df[col].fillna('')
                else:
                    df[col] = df[col].fillna(0)
            
            df['account number'] = df['account number'].astype(str).str.strip()
            
            for _, row in df.iterrows():
                borrower = Borrower(
                    account_number=row.get('account number', '').strip(),
                    name=f"{row.get('first name', '')} {row.get('last name', '')}".strip(),
                    username=row.get('username', ''),
                    fines=row.get('fines', 0.0),
                    borrowed_items=row.get('rented items', [])
                )
                borrower.hashedpassword = row.get('hashedpassword', '')
                borrower.first_name = row.get('first name', '')
                borrower.last_name = row.get('last name', '')
                
                self.borrower_list.add(borrower)
                self.borrowers[borrower.account_number] = borrower
                
        except Exception as e:
            print(f"Error loading borrowers: {e}")
            self.borrowers = {}
            self.borrower_list = BorrowerList()
    
    def find_borrower(self, account_number):
        account_number = str(account_number).strip()
        borrower = self.borrowers.get(account_number)
        if borrower:
            return borrower
        return self.borrower_list.find(account_number)
    
    def remove_borrower(self, account_number):
        account_number = str(account_number).strip()
        if account_number not in self.borrowers:
            return False
        self.borrowers.pop(account_number)
        self.borrower_list.remove(account_number)
        self.save_borrowers()
        return True
    
    def load_borrowed(self):
        try:
            if not os.path.exists(self.borrowed_csv):
                self.borrowed = pd.DataFrame(columns=['title', 'account number', 'date borrowed', 'date due', 'stdno', 'type'])
                return
            
            df = pd.read_csv(self.borrowed_csv, dtype={'account number': str, 'stdno': str})
            
            if df.empty:
                self.borrowed = pd.DataFrame(columns=['title', 'account number', 'date borrowed', 'date due', 'stdno', 'type'])
                return
            
            df.columns = [col.strip().lower() for col in df.columns]
            
            for col in ['title', 'account number', 'date borrowed', 'date due', 'stdno', 'type']:
                if col not in df.columns:
                    df[col] = ''
            
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].dtype == 'string':
                    df[col] = df[col].fillna('')
                else:
                    df[col] = df[col].fillna(0)
            
            df['account number'] = df['account number'].apply(
                lambda x: '{:.0f}'.format(float(x)) if 'e' in str(x).lower() else str(x)
            )
            df['stdno'] = df['stdno'].apply(
                lambda x: '{:.0f}'.format(float(x)) if 'e' in str(x).lower() else str(x)
            )
            self.borrowed = df.copy()
        except:
            self.borrowed = pd.DataFrame(columns=['title', 'account number', 'date borrowed', 'date due', 'stdno', 'type'])
    
    def update_all_fines(self):
        if not hasattr(self, 'account_manager') or not self.account_manager:
            return
        now = datetime.now()
        self.account_manager.load_users()
        overdue_fines = {}
        
        for _, row in self.borrowed.iterrows():
            acc_num = str(row.get('account number', '')).strip()
            due_str = row.get('date due', '')
            try:
                try:
                    due_date = datetime.strptime(due_str, '%Y-%m-%d')
                except:
                    due_date = datetime.strptime(due_str, '%d/%m/%Y')
                if due_date < now:
                    days_over = (now - due_date).days
                    overdue_fine = min(days_over * 0.15, 25)
                    if acc_num not in overdue_fines:
                        overdue_fines[acc_num] = 0.0
                    overdue_fines[acc_num] += overdue_fine
            except:
                pass
        
        for acc_num, calculated_fine in overdue_fines.items():
            user_data = self.account_manager.find_user(acc_num)
            if user_data:
                manual_fine = float(user_data.get('fines', 0.0))
                final_fine = max(manual_fine, calculated_fine)
                if abs(final_fine - manual_fine) > 0.01:
                    self.account_manager.update_fines(acc_num, final_fine)
                borrower = self.find_borrower(acc_num)
                if borrower:
                    borrower.fines = final_fine
    
    def list_borrowed_items(self, account_number):
        acc_str = str(account_number).strip()
        if self.borrowed.empty:
            return []
        mask = self.borrowed['account number'].astype(str).str.strip() == acc_str
        borrowed_by_user = self.borrowed[mask]
        seen = set()
        titles = []
        for title in borrowed_by_user['title'].values:
            title_str = str(title).strip()
            if title_str and title_str != 'nan' and title_str.lower() not in seen:
                seen.add(title_str.lower())
                titles.append(title_str)
        return titles
    
    def save_borrowers(self):
        try:
            if not self.borrower_csv:
                return
            df = pd.read_csv(self.borrower_csv, dtype={'account number': str})
            df.columns = [col.strip().lower() for col in df.columns]
            current = self.borrower_list.head
            while current:
                b = current.borrower
                account_num = str(b.account_number).strip()
                mask = df['account number'].astype(str).str.strip() == account_num
                if mask.any():
                    df.loc[mask, 'rented items'] = str(b.borrowed_items)
                    df.loc[mask, 'fines'] = float(b.fines)
                    if hasattr(b, 'first_name'):
                        df.loc[mask, 'first name'] = b.first_name
                    if hasattr(b, 'last_name'):
                        df.loc[mask, 'last name'] = b.last_name
                current = current.next
            temp_file = self.borrower_csv + ".tmp"
            df.to_csv(temp_file, index=False, quoting=1)
            if os.path.exists(self.borrower_csv):
                os.remove(self.borrower_csv)
            os.rename(temp_file, self.borrower_csv)
        except Exception as e:
            print(f"Error saving borrowers: {e}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def borrow_item(self, account_number, title_fragment):
        acc_str = str(account_number).strip()
        if self.catalogue.empty:
            return "No catalogue data."
        
        current_borrowed = self.borrowed[self.borrowed['account number'].astype(str).str.strip() == acc_str]
        if len(current_borrowed) >= 8:
            return "You have reached your borrowing limit."
        
        matches = self.catalogue[
            self.catalogue['title'].str.contains(str(title_fragment), case=False, na=False, regex=False) &
            (self.catalogue['status'].str.lower() == 'available')
        ]
        
        if matches.empty:
            return "No available item matches that title."
        
        selected = None
        if len(matches) > 1:
            print("Multiple items found:")
            for idx, row in enumerate(matches.itertuples(), 1):
                print(f"{idx}. {row.title}")
            try:
                choice = int(input(f"Select item number (1-{len(matches)}): "))
                if not 1 <= choice <= len(matches):
                    return "Invalid selection."
                selected = matches.iloc[choice - 1]
            except:
                return "Invalid input."
        else:
            selected = matches.iloc[0]
        
        item_title = selected['title']
        
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=21)
        
        record = {
            'title': item_title,
            'account number': acc_str,
            'date borrowed': borrow_date.strftime('%d/%m/%Y'),
            'date due': due_date.strftime('%d/%m/%Y'),
            'std_no': selected.get('std_no', ''),
            'type': selected.get('type', ''),
            'stdno': selected.get('std_no', '')
        }
        
        new_df = pd.DataFrame([record])
        self.borrowed = pd.concat([self.borrowed, new_df], ignore_index=True)
        self.save_borrowed()
        
        catalogue_idx = self.catalogue[self.catalogue['title'] == item_title].index
        if not catalogue_idx.empty:
            self.catalogue.at[catalogue_idx[0], 'status'] = 'unavailable'
            self.save_catalogue()
        
        if hasattr(self, 'account_manager') and self.account_manager:
            user_idx = self.account_manager.users_df[
                self.account_manager.users_df['account number'].astype(str) == acc_str
            ].index
            if not user_idx.empty:
                try:
                    rented_items_str = self.account_manager.users_df.at[user_idx[0], 'rented items']
                    rented_items = ast.literal_eval(rented_items_str) if rented_items_str else []
                    if not isinstance(rented_items, list):
                        rented_items = []
                    if item_title not in rented_items:
                        rented_items.append(item_title)
                    self.account_manager.users_df.at[user_idx[0], 'rented items'] = str(rented_items)
                    self.account_manager.save_users()
                except:
                    pass
        
        return f"Borrowed '{item_title}'."
    
    def return_item(self, account_number, title):
        acc_str = str(account_number).strip()
        if not isinstance(title, str) or not title:
            return False
        title_clean = title.strip()
        
        if self.borrowed.empty:
            return False
        
        account_mask = self.borrowed['account number'].astype(str).str.strip() == acc_str
        title_mask = self.borrowed['title'].astype(str).str.strip().str.lower() == title_clean.lower()
        combined_mask = account_mask & title_mask
        
        if not combined_mask.any():
            return False
        
        self.borrowed = self.borrowed[~combined_mask].copy()
        self.borrowed.reset_index(drop=True, inplace=True)
        self.save_borrowed()
        
        catalogue_items = self.catalogue[self.catalogue['title'].astype(str).str.strip().str.lower() == title_clean.lower()]
        if not catalogue_items.empty:
            for idx in catalogue_items.index:
                self.catalogue.at[idx, 'status'] = 'available'
            self.save_catalogue()
        
        if hasattr(self, 'account_manager') and self.account_manager:
            user_idx = self.account_manager.users_df[
                self.account_manager.users_df['account number'].astype(str) == acc_str
            ].index
            if not user_idx.empty:
                try:
                    rented_items_str = self.account_manager.users_df.at[user_idx[0], 'rented items']
                    rented_items = ast.literal_eval(rented_items_str) if rented_items_str else []
                    rented_items = [t for t in rented_items if str(t).strip().lower() != title_clean.lower()]
                    self.account_manager.users_df.at[user_idx[0], 'rented items'] = str(rented_items)
                    self.account_manager.save_users()
                except:
                    pass
        
        return True
    
    def add_item(self, item_dict):
        try:
            new_item = pd.DataFrame([item_dict])
            self.catalogue = pd.concat([self.catalogue, new_item], ignore_index=True)
            self.save_catalogue()
            return f"Added '{item_dict.get('title', 'item')}' to catalogue."
        except Exception as e:
            return f"Error adding item: {e}"
    
    def update_item(self, title, **updates):
        try:
            mask = self.catalogue['title'].str.strip().str.lower() == title.strip().lower()
            if not mask.any():
                return f"Item '{title}' not found."
            
            for key, value in updates.items():
                col = key.lower().replace('_', ' ')
                if col in self.catalogue.columns:
                    self.catalogue.loc[mask, col] = value
            
            self.save_catalogue()
            return f"Updated '{title}' successfully."
        except Exception as e:
            return f"Error updating item: {e}"
    
    def remove_item(self, title):
        try:
            mask = self.catalogue['title'].str.contains(title, case=False, na=False, regex=False)
            if not mask.any():
                return f"Item '{title}' not found."
            
            borrowed_mask = self.borrowed['title'].str.contains(title, case=False, na=False, regex=False)
            if borrowed_mask.any():
                return f"Cannot remove '{title}' - currently borrowed."
            
            self.catalogue = self.catalogue[~mask].copy()
            self.catalogue.reset_index(drop=True, inplace=True)
            self.save_catalogue()
            return f"Removed '{title}' from catalogue."
        except Exception as e:
            return f"Error removing item: {e}"

    def save_borrowed(self):
        try:
            self.borrowed.to_csv(self.borrowed_csv, index=False, quoting=1)
        except Exception as e:
            print(f"Error saving borrowed items: {e}")
    
    def search_catalogue(self, keyword=None, **criteria):
        """
        Search catalogue by keyword (searches title, author, category) or specific criteria.
        """
        df = self.catalogue.copy()
        
        if df.empty:
            return []
        
        if keyword:
            keyword = str(keyword).strip().lower()
            if keyword:
                mask = (
                    df['title'].astype(str).str.lower().str.contains(keyword, na=False, regex=False) |
                    df['author'].astype(str).str.lower().str.contains(keyword, na=False, regex=False) |
                    df['category'].astype(str).str.lower().str.contains(keyword, na=False, regex=False)
                )
                df = df[mask].copy()
        
        for k, v in criteria.items():
            col = k.lower().replace('_', ' ')
            if col in df.columns:
                df = df[df[col].astype(str).str.contains(str(v), case=False, na=False, regex=False)].copy()
        
        return [Item(row) for _, row in df.iterrows()]
    
    def cleanup_borrowed_items(self):
        if self.borrowed.empty:
            return
        self.borrowed = self.borrowed.drop_duplicates(subset=['account number', 'title'], keep='first').copy()
        self.borrowed.reset_index(drop=True, inplace=True)
        self.save_borrowed()

    def generate_fine_report(self):
        self.update_all_fines()
        if self.borrower_csv:
            self.load_borrowers()
        users_with_fines = []
        current = self.borrower_list.head
        while current:
            borrower = current.borrower
            if borrower.fines > 0:
                users_with_fines.append({
                    'account_number': borrower.account_number,
                    'username': borrower.username,
                    'first_name': getattr(borrower, 'first_name', ''),
                    'last_name': getattr(borrower, 'last_name', ''),
                    'name': borrower.name,
                    'fines': borrower.fines
                })
            current = current.next
        
        if not users_with_fines:
            print("\n" + "="*70)
            print("FINE REPORT - NO OUTSTANDING FINES")
            print("="*70)
            print("No users currently have outstanding fines.")
            print("="*70)
            return

        users_with_fines.sort(key=lambda x: x['fines'], reverse=True)
        total_users = len(users_with_fines)
        total_fines = sum(user['fines'] for user in users_with_fines)
        avg_fine = total_fines / total_users
        max_fine = max(user['fines'] for user in users_with_fines)
        min_fine = min(user['fines'] for user in users_with_fines)
        
        print("\n" + "="*70)
        print("FINE REPORT - USERS WITH OUTSTANDING FINES")
        print("="*70)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Users with Fines: {total_users}")
        print(f"Total Outstanding Fines: ${total_fines:.2f}")
        print("="*70)
        print("\n")
        print(f"{'Account Number':<15} | {'Username':<15} | {'Name':<25} | {'Fine':<10}")
        print("-" * 70)

        for user in users_with_fines:
            account_num = str(user['account_number'])
            username = str(user['username'])[:14]
            full_name = user['name'][:24] if user['name'] else f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()[:24]
            fine_amount = f"${user['fines']:.2f}"
            
            print(f"{account_num:<15} | {username:<15} | {full_name:<25} | {fine_amount:<10}")
    
        print("="*70)
        print("FINE STATISTICS:")
        print(f"  Average Fine: ${avg_fine:.2f}")
        print(f"  Highest Fine: ${max_fine:.2f}")
        print(f"  Lowest Fine: ${min_fine:.2f}")
        print("="*70)
        
        save_option = input("\nSave report to CSV file? (y/n): ").strip().lower()
        if save_option == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Fine_Report_{timestamp}.csv"
            
            export_data = []
            for user in users_with_fines:
                export_data.append({
                    'Account Number': user['account_number'],
                    'Username': user['username'],
                    'First Name': user.get('first_name', ''),
                    'Last Name': user.get('last_name', ''),
                    'Fine Amount': user['fines']
                })
            
            export_df = pd.DataFrame(export_data)
            export_df.to_csv(filename, index=False, quoting=1)
            print(f"Report saved to: {filename}")
        
        print()
