
import os
import getpass
import json
import eth_account

account = None

def get_account():
    global account
    if account is None:
        load_key(None)
    return account

def load_key(args):
    global account
    filename = args.file
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return None, None

    print(f"Loading master key from {filename}...")
    password = getpass.getpass(f"Enter password to decrypt {filename}: ")

    try:
        with open(filename, "r") as f:
            key_json = json.load(f)

        # Decrypt the private key
        private_key_bytes = eth_account.Account.decrypt(key_json, password)
        account = eth_account.Account.from_key(private_key_bytes)
        
        print(f"Success! Private key loaded for address: {account.address}")
        return account, password
    except Exception as e:
        print(f"Error: Failed to decrypt key. Incorrect password? ({e})")
        return None, None
