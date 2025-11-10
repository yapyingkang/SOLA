from cryptography.fernet import Fernet
import os

class FileEncryption:
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
        
    def _load_or_generate_key(self):
        """Load existing key or generate new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            print(f"Encryption key generated: {self.key_file}")
            print("KEEP THIS FILE SECURE!")
            return key
    
    def encrypt_file(self, filename):
        """Encrypt a file"""
        if not os.path.exists(filename):
            print(f"File {filename} not found.")
            return False
        
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.cipher.encrypt(data)
            
            with open(filename, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"File {filename} encrypted successfully.")
            return True
        except Exception as e:
            print(f"Encryption error for {filename}: {e}")
            return False
    
    def decrypt_file(self, filename):
        """Decrypt a file"""
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(filename, 'wb') as f:
                f.write(decrypted_data)
            
            return True
        except Exception as e:
            print(f"Decryption error for {filename}: {e}")
            return False
    
    def is_encrypted(self, filename):
        """Check if file is encrypted"""
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            if not data:
                return False
            
            self.cipher.decrypt(data)
            return True
        except:
            return False

if __name__ == "__main__":
    fe = FileEncryption()
    fe.encrypt_file('UserData.csv')
