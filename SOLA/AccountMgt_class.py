import os
import re
import pwinput
import configparser
import pandas as pd
from datetime import datetime
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import random
import ast
import time



def normalize_username(username):
    return username.strip().lower() if isinstance(username, str) else ''



def validate_password_policy(password, username=None):
    if username and 'admin' in normalize_username(username):
        return (True, "")
    
    if not isinstance(password, str):
        return (False, "Password must be a string.")
    
    if len(password) < 8 or len(password) > 30:
        return (False, "Password must be between 8 and 30 characters.")
    
    if not re.search('[a-z]', password):
        return (False, "Password must contain at least one lowercase letter.")
    
    if not re.search('[A-Z]', password):
        return (False, "Password must contain at least one uppercase letter.")
    
    if not re.search('[0-9]', password):
        return (False, "Password must contain at least one digit.")
    
    if not re.search(r'[!@#$%^&*()_+\-=\{\}\[\]:;"\'<>,.?/~`|]', password):
        return (False, "Password must contain at least one special character.")
    
    if username and normalize_username(username) in password.lower():
        return (False, "Password cannot contain your username.")
    
    return (True, "")



class AccountManager:
    def __init__(self):
        self.user_file = "UserData.csv"
        self.ph = PasswordHasher()
        self.users_df = pd.DataFrame(columns=[
            'account number', 'first name', 'last name',
            'username', 'rented items', 'fines', 'hashedpassword'
        ])
        self.load_users()



    def load_users(self):
        try:
            if not os.path.exists(self.user_file) or os.path.getsize(self.user_file) == 0:
                self.users_df = pd.DataFrame(columns=[
                    'account number', 'first name', 'last name', 'username', 
                    'rented items', 'fines', 'hashedpassword'])
                return



            df = pd.read_csv(self.user_file, dtype={'account number': str})
            df.columns = [col.strip().lower() for col in df.columns]



            for col in ['account number', 'first name', 'last name', 'username',
                        'rented items', 'fines', 'hashedpassword']:
                if col not in df.columns:
                    if col == 'fines':
                        df[col] = 0.0
                    elif col == 'rented items':
                        df[col] = '[]'
                    else:
                        df[col] = ''
            
            df['account number'] = df['account number'].astype(str).str.strip()
            df['fines'] = pd.to_numeric(df['fines'], errors='coerce').fillna(0.0)
            
            for col in df.columns:
                if col not in ['fines', 'account number'] and df[col].dtype == 'object':
                    df[col] = df[col].fillna('').astype(str).str.strip()
            
            self.users_df = df
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users_df = pd.DataFrame(columns=[
                'account number', 'first name', 'last name',
                'username', 'rented items', 'fines', 'hashedpassword'
            ])



    def save_users(self):
        try:
            import os
            temp_file = self.user_file + ".tmp"
            
            with open(temp_file, 'w', newline='') as f:
                self.users_df.to_csv(f, index=False)
                f.flush()
                os.fsync(f.fileno())
            
            if os.path.exists(self.user_file):
                os.remove(self.user_file)
            os.rename(temp_file, self.user_file)
            
        except Exception as e:
            print(f"Error saving users: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass



    def register(self, username, first_name, last_name, password):
        username = username.lower().strip()
        
        if not username:
            return (False, "Username cannot be empty.")
        
        if username in self.users_df['username'].astype(str).str.lower().values:
            return (False, "Username already exists.")
        
        is_valid, error_msg = validate_password_policy(password, username)
        if not is_valid:
            return (False, error_msg)
        
        hashed_pw = self.ph.hash(password)
        account_number = self.generate_account_number()



        new_user = {
            'account number': str(account_number),
            'first name': first_name.strip() if first_name else '',
            'last name': last_name.strip() if last_name else '',
            'username': username,
            'rented items': '[]',
            'fines': 0.0,
            'hashedpassword': hashed_pw
        }
        
        new_df = pd.DataFrame([new_user])
        self.users_df = pd.concat([self.users_df, new_df], ignore_index=True)
        self.save_users()
        
        self.load_users()
        
        return (True, account_number)



    def generate_account_number(self):
        date_str = datetime.now().strftime('%Y%m%d')
        random_number = f"{random.randint(0, 9999):04d}"
        return f"{date_str}{random_number}"



    def authenticate(self, username, password):
        username = username.lower().strip()
        user_row = self.users_df[self.users_df['username'].str.lower() == username]
        
        if user_row.empty:
            return None
        
        try:
            hashed_pw = user_row.iloc[0]['hashedpassword']
            if self.ph.verify(hashed_pw, password):
                return user_row.iloc[0].to_dict()
        except argon2_exceptions.VerifyMismatchError:
            return None
        except Exception:
            return None
        
        return None



    def find_user(self, account_number):
        if not account_number:
            return None
        
        self.load_users()
        
        account_str = str(account_number).strip()
        df = self.users_df[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if df.empty:
            return None
        
        row = df.iloc[0].to_dict()
        
        try:
            row['rented items'] = ast.literal_eval(row.get('rented items', '[]'))
            if not isinstance(row['rented items'], list):
                row['rented items'] = []
        except Exception:
            row['rented items'] = []
        
        return row



    def update_rented_items(self, account_number, rented_items):
        self.load_users()
        
        account_str = str(account_number).strip()
        idxs = self.users_df.index[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if len(idxs) == 0:
            return False
        
        idx = idxs[0]
        self.users_df.at[idx, 'rented items'] = str(rented_items)
        self.save_users()
        return True
    
    
    def update_fines(self, account_number, new_fines):
        account_str = str(account_number).strip()
        
        self.load_users()
        
        idxs = self.users_df.index[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if len(idxs) == 0:
            return False
        
        try:
            idx = idxs[0]
            self.users_df.at[idx, 'fines'] = float(new_fines)
            self.save_users()
            
            time.sleep(0.2)
            
            verify_df = pd.read_csv(self.user_file, dtype={'account number': str})
            verify_df['account number'] = verify_df['account number'].astype(str).str.strip()
            verify_row = verify_df[verify_df['account number'] == account_str]
            if not verify_row.empty:
                actual_fine = float(verify_row.iloc[0]['fines'])
                if abs(actual_fine - float(new_fines)) > 0.001:
                    print(f"Warning: Expected ${new_fines:.2f} but file shows ${actual_fine:.2f}")
                    return False
            return True
        except Exception as e:
            print(f"Error updating fines: {e}")
            return False


    def update_username(self, account_number, new_username):
        account_str = str(account_number).strip()
        new_username = new_username.strip().lower()
        
        self.load_users()
        
        existing = self.users_df[
            (self.users_df['username'].str.lower() == new_username) & 
            (self.users_df['account number'].astype(str).str.strip() != account_str)
        ]
        
        if not existing.empty:
            print(f"Username '{new_username}' is already taken.")
            return False
        
        idxs = self.users_df.index[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if len(idxs) == 0:
            print(f"Account {account_number} not found.")
            return False
        
        idx = idxs[0]
        self.users_df.at[idx, 'username'] = new_username
        self.save_users()
        
        time.sleep(0.2)
        self.load_users()
        
        verify_row = self.users_df[self.users_df['account number'].astype(str).str.strip() == account_str]
        if not verify_row.empty:
            actual_username = str(verify_row.iloc[0]['username']).strip().lower()
            if actual_username == new_username:
                print("Username updated.")
                return True
            else:
                print(f"Warning: Expected '{new_username}' but file shows '{actual_username}'")
                return False
        
        return False


    def update_first_name(self, account_number, new_first_name):
        account_str = str(account_number).strip()
        new_first_name = new_first_name.strip()
        
        self.load_users()
        
        idxs = self.users_df.index[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if len(idxs) == 0:
            print(f"Account {account_number} not found.")
            return False
        
        idx = idxs[0]
        self.users_df.at[idx, 'first name'] = new_first_name
        self.save_users()
        
        print("First name updated.")
        return True


    def update_last_name(self, account_number, new_last_name):
        account_str = str(account_number).strip()
        new_last_name = new_last_name.strip()
        
        self.load_users()
        
        idxs = self.users_df.index[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if len(idxs) == 0:
            print(f"Account {account_number} not found.")
            return False
        
        idx = idxs[0]
        self.users_df.at[idx, 'last name'] = new_last_name
        self.save_users()
        
        print("Last name updated.")
        return True


    def update_password(self, account_number, new_password):
        account_str = str(account_number).strip()
        
        self.load_users()
        
        idxs = self.users_df.index[self.users_df['account number'].astype(str).str.strip() == account_str]
        
        if len(idxs) == 0:
            print(f"Account {account_number} not found.")
            return False
        
        try:
            new_hashed = self.ph.hash(new_password)
            idx = idxs[0]
            self.users_df.at[idx, 'hashedpassword'] = new_hashed
            self.save_users()
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False



    def password_reset_flow(self):
        print("=== Password Reset ===")
        username = input("Enter your username: ").strip().lower()
        
        if not username:
            print("Username cannot be empty.")
            return False

        user_row = self.users_df[self.users_df['username'].str.lower() == username]
        if user_row.empty:
            print("Username not found.")
            return False

        first_name_input = input("Enter your first name: ").strip()
        if not first_name_input:
            print("First name cannot be empty.")
            return False

        if first_name_input.lower() != user_row.iloc[0]['first name'].strip().lower():
            print("Identity verification failed.")
            return False

        new_password = pwinput.pwinput("Enter your new password: ")
        
        is_valid, error_msg = validate_password_policy(new_password, username)
        if not is_valid:
            print(error_msg)
            return False

        try:
            new_hash = self.ph.hash(new_password)
        except Exception as e:
            print(f"Error hashing password: {e}")
            return False

        idx = user_row.index[0]
        self.users_df.at[idx, 'hashedpassword'] = new_hash
        self.save_users()
        print("Password reset successfully.")
        return True



class Borrower:
    def __init__(self, account_number, name, username='', fines=0.0, borrowed_items=None, max_borrowing_limit=8):
        self.account_number = str(account_number)
        self.name = str(name)
        self.username = str(username)
        try:
            self.fines = float(fines)
        except Exception:
            self.fines = 0.0
        self.borrowed_items = borrowed_items if isinstance(borrowed_items, list) else []
        self.max_borrowing_limit = max_borrowing_limit



class Admin:
    CONFIG_PATH = "admin_config.ini"

    def __init__(self, sola, account_manager=None, config_path=CONFIG_PATH):
        self.sola = sola
        self.account_manager = account_manager
        
        # Initialize encryption
        try:
            from encryption_helper import FileEncryption
            self.encryptor = FileEncryption()
            self.encryption_enabled = True
        except ImportError:
            self.encryptor = None
            self.encryption_enabled = False
        
        if account_manager:
            self.load_borrowers_from_csv(account_manager)
        else:
            self.borrowers = sola.borrowers

        self.ph = PasswordHasher()
        self.config_path = config_path
        self.config = configparser.ConfigParser()

        if not os.path.exists(self.config_path):
            self._setup_password()
        else:
            self._load_config()
            
    def _load_config(self):
        """Load admin config with decryption"""

        if self.encryption_enabled and os.path.exists(self.config_path):
            if self.encryptor.is_encrypted(self.config_path):
                self.encryptor.decrypt_file(self.config_path)
        
        self.config.read(self.config_path)
        self.hashed_password = self.config.get('admin', 'hashed_password', fallback=None)
  
        if self.encryption_enabled and os.path.exists(self.config_path):
            self.encryptor.encrypt_file(self.config_path)
        
        if not self.hashed_password:
            self._setup_password()

    def _save_config(self):
        """Save admin config with encryption"""
        if self.encryption_enabled and os.path.exists(self.config_path):
            if self.encryptor.is_encrypted(self.config_path):
                self.encryptor.decrypt_file(self.config_path)
        
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
        if self.encryption_enabled:
            self.encryptor.encrypt_file(self.config_path)

    def _setup_password(self):
        print("=== Setup Admin Password ===")
        while True:
            p1 = pwinput.pwinput("Enter new admin password: ")
            p2 = pwinput.pwinput("Confirm new admin password: ")
            
            if p1 != p2:
                print("Passwords do not match.")
                continue
            
            if len(p1) < 8:
                print("Password must be at least 8 characters.")
                continue
            
            self.hashed_password = self.ph.hash(p1)
            self.config['admin'] = {'hashed_password': self.hashed_password}
            self._save_config()
            
            if self.encryption_enabled:
                print("Admin password set and encrypted.")
            else:
                print("Admin password set.")
            break

    def refresh_borrowers(self):
        if self.account_manager:
            self.load_borrowers_from_csv(self.account_manager)

    def load_borrowers_from_csv(self, account_manager):
        self.borrowers = {}
        
        account_manager.load_users()
        
        for idx, row in account_manager.users_df.iterrows():
            acc = str(row['account number']).strip()
            first_name = row.get('first name', '')
            last_name = row.get('last name', '')
            name = f"{first_name} {last_name}".strip()
            username = row.get('username', '')
            fines = row.get('fines', 0.0)
            
            try:
                rented = ast.literal_eval(str(row.get('rented items', '[]')))
                if not isinstance(rented, list):
                    rented = []
            except:
                rented = []
            
            borrower = Borrower(acc, name, username=username, fines=fines, borrowed_items=rented)
            borrower.first_name = first_name
            borrower.last_name = last_name
            borrower.hashedpassword = row.get('hashedpassword', '')
            self.borrowers[acc] = borrower

    def authenticate(self, pw):
        try:
            if self.ph.verify(self.hashed_password, pw):
                return {'username': 'admin', 'first_name': 'Admin'}
        except Exception:
            pass
        return None

    def change_password(self):
        print("=== Change Admin Password ===")
        while True:
            old_pw = pwinput.pwinput("Current password: ")
            if not self.authenticate(old_pw):
                print("Incorrect password.")
                continue
            
            new_pw = pwinput.pwinput("New password: ")
            confirm_pw = pwinput.pwinput("Confirm new admin password: ")
            
            if new_pw != confirm_pw:
                print("Passwords do not match.")
                continue
            
            if len(new_pw) < 8:
                print("Password must be at least 8 characters.")
                continue
            
            self.hashed_password = self.ph.hash(new_pw)
            self.config['admin']['hashed_password'] = self.hashed_password
            self._save_config()
            
            if self.encryption_enabled:
                print("Password changed and encrypted.")
            else:
                print("Password changed.")
            break

    def add_borrower(self, borrower):
        if not hasattr(borrower, 'username'):
            borrower.username = ""
        if not hasattr(borrower, 'hashedpassword'):
            borrower.hashedpassword = ""
        
        acc_str = str(borrower.account_number).strip()
        
        if acc_str in self.borrowers:
            return False
        
        self.borrowers[acc_str] = borrower
        
        if hasattr(self.sola, 'borrower_list'):
            self.sola.borrower_list.add(borrower)
        if hasattr(self.sola, 'save_borrowers'):
            self.sola.save_borrowers()
        
        time.sleep(0.2)
        self.refresh_borrowers()
        
        return True

    def remove_borrower(self, account_number):
        acc_str = str(account_number).strip()
        
        if not self.account_manager:
            return False
        
        time.sleep(0.2)
        self.refresh_borrowers()
        
        idx = self.account_manager.users_df[
            self.account_manager.users_df['account number'].astype(str).str.strip() == acc_str
        ].index
        
        if idx.empty:
            print(f"No borrower found with account '{acc_str}'")
            return False
        
        user_data = self.account_manager.users_df.iloc[idx[0]]
        
        print("\nAccount Details:")
        print(f"  Username: {user_data['username']}")
        
        try:
            rented = ast.literal_eval(str(user_data.get('rented items', '[]')))
            rented_count = len(rented) if isinstance(rented, list) else 0
        except:
            rented_count = 0
        
        print(f"  Name: {user_data['first name']} {user_data['last name']}")
        print(f"  Books Currently Borrowed: {rented_count}")
        print(f"  Outstanding Fines: ${float(user_data.get('fines', 0.0)):.2f}")
        
        confirm = input("\nAre you sure you want to delete this account? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("Account deletion cancelled.")
            return False
        
        self.account_manager.users_df = self.account_manager.users_df.drop(idx)
        self.account_manager.save_users()
        
        if acc_str in self.borrowers:
            self.borrowers.pop(acc_str)
        
        print(f"Account {acc_str} deleted successfully.")
        return True
    
    def add_item(self, title, category, language, year, std_no='', author='', type_='', audio_format=''):
        if not title.strip():
            return "Title is required."
        if any(self.sola.catalogue['title'].str.lower() == title.lower()):
            return f"Item '{title}' already exists."
        
        new_item = {
            'title': title,
            'category': category,
            'language': language,
            'year published': year,
            'std_no': std_no,
            'author': author,
            'type': type_,
            'audio_format': audio_format,
            'status': 'available'
        }
        
        new_df = pd.DataFrame([new_item])
        self.sola.catalogue = pd.concat([self.sola.catalogue, new_df], ignore_index=True)
        self.sola.save()
        return f"Item '{title}' added successfully."

    def remove_item(self, title_fragment):
        matches = self.sola.catalogue[
            self.sola.catalogue['title'].str.contains(str(title_fragment), case=False, na=False)
        ]
        
        if matches.empty:
            return f"No items found matching '{title_fragment}'."
        
        if len(matches) > 1:
            print(f"\nMultiple items found matching '{title_fragment}':")
            for idx, row in enumerate(matches.itertuples(), 1):
                print(f"{idx}. {row.title}")
            try:
                choice = int(input(f"Select item to remove (1-{len(matches)}): "))
                if not 1 <= choice <= len(matches):
                    return "Invalid selection."
                selected = matches.iloc[choice - 1]
            except:
                return "Invalid input."
        else:
            selected = matches.iloc[0]
        
        title = selected['title']
        
        if not self.sola.borrowed.empty and 'title' in self.sola.borrowed.columns:
            if title in self.sola.borrowed['title'].values:
                return f"Cannot remove '{title}' - item is currently borrowed."
        
        self.sola.catalogue = self.sola.catalogue[
            self.sola.catalogue['title'].str.lower() != title.lower()
        ]
        self.sola.save()
        return f"Item '{title}' removed successfully."

    def list_all_borrowers(self):
        self.refresh_borrowers()
        
        print("\n=== Borrowers ===")
        print(f"{'Account Number':<18} | {'Username':<15} | {'First Name':<15} | {'Last Name':<15}")
        print('-' * 72)
        
        seen_accounts = set()
        
        for borrower in self.borrowers.values():  
            acc = str(getattr(borrower, 'account_number', '')).strip()
            
            if acc in seen_accounts:
                continue
            seen_accounts.add(acc)
            
            username = str(getattr(borrower, 'username', ''))
            
            if hasattr(borrower, 'first_name'):
                first_name = str(getattr(borrower, 'first_name', ''))
            else:
                name = str(getattr(borrower, 'name', ''))
                first_name = name.split()[0] if name else ''
            
            if hasattr(borrower, 'last_name'):
                last_name = str(getattr(borrower, 'last_name', ''))
            else:
                name = str(getattr(borrower, 'name', ''))
                last_name = ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else ''
            
            print(f"{acc:<18} | {username:<15} | {first_name:<15} | {last_name:<15}")
        
        return [b for b in self.borrowers.values()]

    def list_borrowers_with_unpaid_fines(self):
        self.refresh_borrowers()
        
        print("\n=== Borrowers with Unpaid Fines ===")
        print(f"{'Account Number':<18} | {'Username':<15} | {'Name':<25} | {'Fines':<10}")
        print('-' * 75)
        
        found_any = False
        seen_accounts = set()
        
        for borrower in self.borrowers.values():
            acc = str(getattr(borrower, 'account_number', '')).strip()
            
            if acc in seen_accounts:
                continue
            
            if hasattr(borrower, 'fines') and float(borrower.fines) > 0:
                found_any = True
                seen_accounts.add(acc)
                
                username = str(getattr(borrower, 'username', ''))
                
                if hasattr(borrower, 'first_name') and hasattr(borrower, 'last_name'):
                    full_name = f"{borrower.first_name} {borrower.last_name}"
                else:
                    full_name = str(getattr(borrower, 'name', ''))
                
                fines = float(borrower.fines)
                print(f"{acc:<18} | {username:<15} | {full_name:<25} | ${fines:<9.2f}")
        
        if not found_any:
            print("No borrowers with unpaid fines.")
        
        print()

    def list_borrowed_items(self, account_number):
        return self.sola.list_borrowed_items(account_number)
