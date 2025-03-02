import os
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

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
        
        # MongoDB connection attributes - initialized to None, will be set up later
        self.client = None
        self.db = None
        self.collection = None
        
        # Set up MongoDB connection
        self._setup_mongodb_connection()
    
    def _setup_mongodb_connection(self):
        """Set up the MongoDB connection using hardcoded values and environment variables"""
        try:
            # Load environment variables
            load_dotenv()
            db_password = os.getenv("DB_PASSWORD")
            
            if not db_password:
                print("Warning: DB_PASSWORD not found in .env file. MongoDB connection not established.")
                return
            
            # Hardcoded MongoDB connection details
            uri = f"mongodb+srv://muhammadelsoukkary:{db_password}@electionapp.sz7we.mongodb.net/?retryWrites=true&w=majority&appName=ElectionApp"
            db_name = "VoterInfo"
            collection_name = "ElectionApp"
            
            # Establish connection
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            self.client.admin.command('ping')  # Verify connection
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.collection = None  # Ensure collection is None if connection fails
    
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
    
    # New MongoDB specific methods
    def encrypt_and_store(self, document=None):
        """Encrypt a document and store it in MongoDB"""
        if self.collection is None:  # Fix: Explicitly check if collection is None
            raise ValueError("MongoDB collection not set up properly.")
        
        # Use provided document or the class's json_data
        if document:
            # Convert document to dictionary if it has a to_dict method
            if hasattr(document, 'to_dict'):
                self.json_data = document.to_dict()
            # Convert document to dictionary if it has a __dict__ attribute
            elif hasattr(document, '__dict__'):
                self.json_data = document.__dict__
            else:
                self.json_data = document
        
        if not self.json_data:
            raise ValueError("No data provided for encryption.")
        
        # Encrypt the data
        encrypted = self.encrypt()
        
        # Create a MongoDB document with encrypted data
        mongo_doc = {
            "encrypted_data": encrypted
        }
        
        # Store in MongoDB
        result = self.collection.insert_one(mongo_doc)
        print(f"Document stored in MongoDB with ID: {result.inserted_id}")
        return result.inserted_id
    
    def retrieve_and_decrypt(self, query):
        """Retrieve an encrypted document from MongoDB and decrypt it"""
        if self.collection is None:  # Fix: Explicitly check if collection is None
            raise ValueError("MongoDB collection not set up properly.")
        
        document = self.collection.find_one(query)
        if not document:
            raise ValueError(f"No document found matching query: {query}")
        
        if "encrypted_data" not in document:
            raise ValueError("Document found but contains no encrypted data")
        
        # Parse the encrypted data
        encrypted_data = json.loads(document["encrypted_data"])
        
        # Decrypt and return
        decrypted = self.decrypt(encrypted_data)
        return decrypted
    
    def update_encrypted_document(self, query, new_data):
        """Update an existing document with new encrypted data"""
        if self.collection is None:  # Fix: Explicitly check if collection is None
            raise ValueError("MongoDB collection not set up properly.")
        
        # Find the document first
        document = self.collection.find_one(query)
        if not document:
            raise ValueError(f"No document found matching query: {query}")
        
        # Encrypt the new data
        self.json_data = new_data
        encrypted = self.encrypt()
        
        # Update in MongoDB
        result = self.collection.update_one(
            query,
            {"$set": {"encrypted_data": encrypted}}
        )
        
        print(f"Updated {result.modified_count} document(s)")
        return result.modified_count