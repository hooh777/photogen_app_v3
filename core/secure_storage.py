# core/secure_storage.py
import os
import json
from cryptography.fernet import Fernet
import logging

class SecureStorage:
    """
    Handles secure, encrypted storage of API keys on the local filesystem.
    """
    def __init__(self, key_path='secret.key', data_path='api_keys.json.enc'):
        self.key_path = key_path
        self.data_path = data_path
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Loads the encryption key from a file, or generates a new one if not found."""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
            logging.info(f"Encryption key generated and saved to {self.key_path}")
            return key

    def _load_decrypted_data(self):
        """Loads and decrypts the API key data file."""
        if not os.path.exists(self.data_path):
            return {}
        try:
            with open(self.data_path, 'rb') as f:
                encrypted_data = f.read()
            if not encrypted_data:
                return {}
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logging.warning(f"Could not decrypt API key file. It might be corrupted. Starting fresh. Error: {e}")
            return {}

    def _save_encrypted_data(self, data):
        """Encrypts and saves the API key data."""
        json_data = json.dumps(data).encode('utf-8')
        encrypted_data = self.cipher.encrypt(json_data)
        with open(self.data_path, 'wb') as f:
            f.write(encrypted_data)

    def save_api_key(self, provider_name, api_key):
        """Saves or updates an API key for a specific provider."""
        data = self._load_decrypted_data()
        data[provider_name] = api_key
        self._save_encrypted_data(data)
        logging.info(f"API key for {provider_name} has been saved securely.")

    def load_api_key(self, provider_name):
        """Loads the API key for a specific provider."""
        if not provider_name: return ""
        data = self._load_decrypted_data()
        return data.get(provider_name, "") # Return empty string if not found

    def clear_api_key(self, provider_name):
        """Clears the API key for a specific provider."""
        data = self._load_decrypted_data()
        if provider_name in data:
            del data[provider_name]
            self._save_encrypted_data(data)
            logging.info(f"API key for {provider_name} has been cleared.")
            return ""
        return "" # Return empty string to clear the textbox