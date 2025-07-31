#Password manager and encryption script.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

def load_key():
    with open("key.key", "rb") as file:
        key = file.read()
    return key

'''
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
generate_key()
'''


master_password = input("Enter your master password: ").encode()
salt = b'some_salt_value'  # Use a secure, random salt and store it safely

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
)
key = base64.urlsafe_b64encode(kdf.derive(master_password))
fer = Fernet(key)

def add_pass():
    service = input("Enter the name of the website or service: ")
    new_pass = input("Enter the new password: ")
    confirm_pass = input("Confirm the new password: ")
    if new_pass == confirm_pass:
        print(f"Password for {service} has been added.")
        with open("passwords.txt", "a") as f:
            f.write(f"{service}: {fer.encrypt(new_pass.encode()).decode()}\n")
    else:
        print("Passwords do not match. Please try again.")


def find_pass():
    pass_name = input("Enter name of service to retrieve password: ")
    with open("passwords.txt", "r") as f:
        for line in f:
            if line.startswith(pass_name + ":"):
                user, encrypted = line.strip().split(": ", 1)
                decrypted = fer.decrypt(encrypted.encode()).decode()
                print(f"Service: {user}\nPassword: {decrypted}")
                return
        print("Service not found. Please try again.")
            
while True:
    print("Welcome to your password manager!")
    print("Select an option:")
    print("1. Add a new password")
    print("2. Retrieve a password")
    print("3. Exit")
    mode = int(input("Enter your choice (1-3): "))
    if mode == 3:
        break
    if mode!= 1 and mode != 2 and mode != 3:
        print("Invalid choice, please try again.")
        continue
    elif mode == 1:
        add_pass()
    elif mode == 2:
        find_pass()