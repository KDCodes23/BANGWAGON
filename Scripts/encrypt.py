import os
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class CryptoHandler:
    def __init__(self, key_file="Key&IV.enc", json_data=None):
        """Initialize the CryptoHandler with optional custom key file and JSON data."""
        self.key_file = key_file
        if isinstance(key_file, dict):
            self.json_data = key_file
            self.key_file = "Key&IV.enc"
        else:
            self.json_data = json_data
        self.key = None
        self.backend = default_backend()
    
    def generate_key(self, key_size=32):
        """Generate a new AES key (default: 256 bits)."""
        self.key = os.urandom(key_size)  # 256 bits by default
        print(f"Key generated successfully ({key_size*8} bits)")
        return self.key
    
    def save_key_and_iv(self, iv):
        """Save the IV and key to the key file."""
        if not self.key:
            raise ValueError("No key available. Generate or import a key first.")
        
        # Combine IV and key and encode as base64
        file_data = base64.b64encode(iv + self.key).decode('utf-8')
        
        try:
            with open(self.key_file, 'a') as file:
                file.write(file_data + '\n')  # Append new line for separation
            print(f'Key and IV saved to {self.key_file}.')
        except Exception as err:
            print(f"Error writing file: {err}")
        
        self._read_key_file()
    
    def _read_key_file(self):
        """Helper method to read the key file contents."""
        try:
            with open(self.key_file, 'r') as file:
                data = file.read()
            print(f"File Contents:\n{data}")
        except Exception as err:
            print(f"Error reading file: {err}")
    
    def encrypt(self, data=None):
        """Encrypt data using AES-CBC with the current key."""
        if not self.key:
            raise ValueError("No key available. Generate or import a key first.")
        
        # Use the JSON data if no data is provided
        if data is None:
            if self.json_data is None:
                raise ValueError("No data provided for encryption.")
            data = self.json_data
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Convert input to string if it's not already
        if not isinstance(data, str):
            data_str = json.dumps(data)
        else:
            data_str = data
        
        data_bytes = data_str.encode('utf-8')
        
        # Create cipher and encryptor
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # Pad the data (AES requires data length to be a multiple of 16 bytes)
        padded_data = self._pad_data(data_bytes)
        
        # Encrypt the data
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        encrypted_base64 = base64.b64encode(encrypted).decode('utf-8')
        
        # Save IV and key
        self.save_key_and_iv(iv)
        
        # Return formatted encrypted data as JSON
        result = {
            'iv': base64.b64encode(iv).decode('utf-8'),
            'data': encrypted_base64
        }
        
        print(f"Data encrypted successfully")
        return json.dumps(result)
    
    def decrypt(self, encrypted_data):
        """Decrypt data using AES-CBC with the current key."""
        if not self.key:
            raise ValueError("No key available. Generate or import a key first.")
        
        # Split the encrypted data to get IV and data
        if isinstance(encrypted_data, dict) and 'iv' in encrypted_data and 'data' in encrypted_data:
            # If provided as a dictionary with iv and data keys
            iv = base64.b64decode(encrypted_data['iv'])
            data = base64.b64decode(encrypted_data['data'])
        else:
            # If provided as a string in the format "iv.data"
            iv_b64, data_b64 = encrypted_data.split('.')
            iv = base64.b64decode(iv_b64)
            data = base64.b64decode(data_b64)
        
        # Create cipher and decryptor
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        decrypted = decryptor.update(data) + decryptor.finalize()
        
        # Remove padding
        unpadded_data = self._unpad_data(decrypted)
        
        try:
            # Try to parse as JSON if it was a JSON object
            result = json.loads(unpadded_data)
        except json.JSONDecodeError:
            # Otherwise, return as string
            result = unpadded_data
        
        print(f"Data decrypted successfully")
        return result
    
    def _pad_data(self, data):
        """Pad data to be a multiple of 16 bytes (AES block size)."""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length]) * padding_length
        return data + padding
    
    def _unpad_data(self, data):
        """Remove PKCS#7 padding."""
        padding_length = data[-1]
        if padding_length > 16:
            # Invalid padding, return as is
            return data.decode('utf-8', errors='replace')
        
        # Check for valid PKCS#7 padding
        if all(x == padding_length for x in data[-padding_length:]):
            unpadded = data[:-padding_length]
        else:
            # Invalid padding, return as is
            unpadded = data
            
        return unpadded.decode('utf-8', errors='replace')
    
    def import_key(self, key):
        """Import an existing key."""
        if isinstance(key, str):
            # Assume base64 encoded
            self.key = base64.b64decode(key)
        else:
            # Assume bytes
            self.key = key
        print("Key imported successfully")
        return self.key
    
    def export_key(self):
        """Export the current key as base64."""
        if not self.key:
            raise ValueError("No key available to export")
        return base64.b64encode(self.key).decode('utf-8')
    
    def read_encrypted_file(self):
        """Read all encrypted data entries from the key file."""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'r') as file:
                    lines = file.readlines()
                return [line.strip() for line in lines if line.strip()]
            else:
                print(f"File {self.key_file} not found.")
                return []
        except Exception as err:
            print(f"Error reading file: {err}")
            return []
    
    def decrypt_file_entries(self):
        """Decrypt all entries in the key file."""
        entries = self.read_encrypted_file()
        results = []
        
        for entry in entries:
            try:
                # The first 16 bytes (after base64 decoding) are the IV,
                # The rest is the key we used for encryption
                raw_data = base64.b64decode(entry)
                iv = raw_data[:16]
                key = raw_data[16:]
                
                # Save the current key to restore it later
                current_key = self.key
                
                # Use the key from the file
                self.key = key
                
                # We need to create a properly formatted string for decryption
                # Since we don't have the actual encrypted data here, this is a placeholder
                print(f"Found key entry with IV: {base64.b64encode(iv).decode('utf-8')}")
                
                # Restore the original key
                self.key = current_key
                
            except Exception as e:
                print(f"Error processing entry: {e}")
        
        return results
    
    def encrypt_file(self, file_path, output_path=None):
        """Encrypt an entire file."""
        if not output_path:
            output_path = file_path + '.enc'
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Generate a random IV
            iv = os.urandom(16)
            
            # Create cipher and encryptor
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            # Pad the data
            padded_data = self._pad_data(file_data)
            
            # Encrypt the data
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            
            # Write IV and encrypted data to output file
            with open(output_path, 'wb') as f:
                f.write(iv)
                f.write(encrypted)
            
            print(f"File encrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path, output_path=None):
        """Decrypt an encrypted file."""
        if not output_path:
            # Remove .enc extension if present
            if encrypted_file_path.endswith('.enc'):
                output_path = encrypted_file_path[:-4]
            else:
                output_path = encrypted_file_path + '.dec'
        
        try:
            with open(encrypted_file_path, 'rb') as f:
                # Read the IV (first 16 bytes)
                iv = f.read(16)
                # Read the rest as encrypted data
                encrypted_data = f.read()
            
            # Create cipher and decryptor
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            # Decrypt the data
            decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            unpadded_data = self._unpad_data(decrypted).encode('utf-8')
            
            # Write decrypted data to output file
            with open(output_path, 'wb') as f:
                f.write(unpadded_data)
            
            print(f"File decrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error decrypting file: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create a crypto handler instance with JSON data
    sensitive_data = {
        "first_name": "John",
        "last_name": "Doe",
        "dob": "1990-01-01",
        "id_license": "ABC123456",
        "address": "123 Main St, Anytown, US"
    }
    
    crypto = CryptoHandler(json_data=sensitive_data)
    
    # Generate a new key
    key = crypto.generate_key()
    
    # Encrypt the JSON data
    encrypted = crypto.encrypt()
    print(f"Encrypted: {encrypted}")
    
    # Decrypt the data
    decrypted = crypto.decrypt(json.loads(encrypted))
    print(f"Decrypted: {decrypted}")
    
    # Export the key for storage
    key_b64 = crypto.export_key()
    print(f"Exported key: {key_b64}")
    
    # Import a key (in a new instance)
    crypto2 = CryptoHandler()
    crypto2.import_key(key_b64)
    
    # Encrypt a file
    # crypto.encrypt_file("example.txt")
    
    # Decrypt a file
    # crypto.decrypt_file("example.txt.enc")