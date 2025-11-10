import configparser
import pwinput
from argon2 import PasswordHasher
import re
import secrets
from datetime import datetime
from encryption_helper import FileEncryption

ph = PasswordHasher()
config = configparser.ConfigParser()
config_path = 'admin_config.ini'
log_file = 'admin_reset_log.txt'
encryptor = FileEncryption()

def log_event(event_type, token, message):
    """Write security events to audit log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, 'a') as log:
            log.write(f"{timestamp} | {event_type} | Token: {token} | {message}\n")
            log.flush()
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")

reset_token = secrets.token_hex(16)
log_event("RESET_INITIATED", reset_token, "Password reset process started")

print("=== Admin Password Reset ===")
print(f"Reset Token: {reset_token}")
print("\nPassword Requirements:")
print("  - 8-30 characters")
print("  - At least one uppercase letter")
print("  - At least one lowercase letter")
print("  - At least one digit")
print("  - At least one special character")
print()

confirm = input("Type 'YES' to continue: ")
if confirm != 'YES':
    log_event("RESET_CANCELLED", reset_token, "User cancelled reset operation")
    print("Password reset cancelled.")
    exit(0)

while True:
    pw1 = pwinput.pwinput(prompt="Enter new admin password: ")
    pw2 = pwinput.pwinput(prompt="Confirm new admin password: ")
    
    if pw1 != pw2:
        log_event("VALIDATION_FAILED", reset_token, "Password mismatch")
        print("Error: Passwords do not match. Try again.\n")
        continue
    
    if len(pw1) < 8 or len(pw1) > 30:
        log_event("VALIDATION_FAILED", reset_token, "Invalid length")
        print("Error: Password must be between 8 and 30 characters.\n")
        continue
    
    if not re.search('[a-z]', pw1):
        log_event("VALIDATION_FAILED", reset_token, "Missing lowercase")
        print("Error: Password must contain at least one lowercase letter.\n")
        continue
    
    if not re.search('[A-Z]', pw1):
        log_event("VALIDATION_FAILED", reset_token, "Missing uppercase")
        print("Error: Password must contain at least one uppercase letter.\n")
        continue
    
    if not re.search('[0-9]', pw1):
        log_event("VALIDATION_FAILED", reset_token, "Missing digit")
        print("Error: Password must contain at least one digit.\n")
        continue
    
    if not re.search(r'[!@#$%^&*()_+\-=\{\}\[\]:;"\'<>,.?/~`|]', pw1):
        log_event("VALIDATION_FAILED", reset_token, "Missing special character")
        print("Error: Password must contain at least one special character.\n")
        continue
    
    log_event("VALIDATION_PASSED", reset_token, "Password meets all requirements")
    break

hashed_pw = ph.hash(pw1)
log_event("PASSWORD_HASHED", reset_token, "Password hashed with Argon2")

if encryptor.is_encrypted(config_path):
    encryptor.decrypt_file(config_path)
    log_event("CONFIG_DECRYPTED", reset_token, "Config file decrypted for update")

config['admin'] = {
    'username': 'admin',
    'hashed_password': hashed_pw
}

with open(config_path, 'w') as configfile:
    config.write(configfile)

encryptor.encrypt_file(config_path)
log_event("CONFIG_ENCRYPTED", reset_token, "Config file encrypted")

log_event("RESET_COMPLETED", reset_token, "Password reset successful")

print("\nPassword reset successfully.")
print("Admin config file encrypted.")
print("You can now login with your new password.")
print(f"\nAll actions logged to: {log_file}")
