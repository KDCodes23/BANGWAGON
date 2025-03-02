import json
from datetime import datetime
from encrypt import CryptoHandler  # Import the encryption class

class DriverInfo:
    def __init__(self, id, first_last_full_string, dob, full_address):
        # Initialize default values
        self.id = None
        self.first_name = None
        self.last_name = None
        self.date_of_birth = None
        self.street_number = None
        self.street_name = None
        self.city = None
        self.province = None
        self.postal_code = None
        self.full_address = None

        # Parse the provided data
        self.parse_driver_info(id, first_last_full_string, dob, full_address)

    def parse_driver_info(self, id, first_last_full_string, dob, full_address):
        # Parse ID
        if isinstance(id, str) and id.strip():
            self.id = id.strip()

        # Parse first and last name
        if isinstance(first_last_full_string, str):
            names = first_last_full_string.strip().split(' ')
            if len(names) >= 2:
                self.first_name = names[0]
                self.last_name = ' '.join(names[1:])

        # Parse DOB
        if isinstance(dob, str) and dob.strip():
            try:
                self.date_of_birth = datetime.strptime(dob.strip(), "%Y-%m-%d")
            except ValueError:
                self.date_of_birth = None  # Handle invalid date format

        # Parse address
        if isinstance(full_address, str):
            address_parts = [part.strip() for part in full_address.split(',')]
            
            if len(address_parts) >= 3:
                street_parts = address_parts[0].split(' ')
                if len(street_parts) >= 2:
                    self.street_number = street_parts[0]
                    self.street_name = ' '.join(street_parts[1:])

                self.city = address_parts[1]
                self.province = address_parts[2]
                self.postal_code = address_parts[3] if len(address_parts) > 3 else None
                self.full_address = full_address.strip()

    def to_json(self):
        """Convert the object to JSON format."""
        return json.dumps({
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.strftime("%Y-%m-%d") if self.date_of_birth else None,
            "street_number": self.street_number,
            "street_name": self.street_name,
            "city": self.city,
            "province": self.province,
            "postal_code": self.postal_code,
            "full_address": self.full_address
        }, indent=4)

# Create a new crypto handler instance and generate a key
crypto_handler = CryptoHandler()
crypto_handler.generate_key()

# Create the driver info object
driver = DriverInfo(
    "D1234-56789",
    "John Smith",
    "1990-01-01",
    "206-320 KINGSWOOD DR, KITCHENER, ON, N2E 2K2"
)

# Get the JSON data and encrypt it
json_data = driver.to_json()
encrypted_data = crypto_handler.encrypt(json_data)

print("Encrypted data:", encrypted_data)
# To decrypt: decrypted_data = crypto_handler.decrypt(encrypted_data)

print(driver.to_json())

class TestDriverInfo:
    @staticmethod
    def run_test():
        try:
            # Test creating a driver
            test_driver = DriverInfo(
                "T9876-54321",
                "Jane Doe",
                "1985-06-15",
                "123 Main St, Toronto, ON, M5V 2K7"
            )
            
            # Test JSON conversion
            test_json = test_driver.to_json()
            print("\nTest Results:")
            print("Driver Info JSON:")
            print(test_json)
            
            # Test encryption
            test_encrypted = crypto_handler.encrypt(test_json)
            print("\nEncrypted Data:")
            print(test_encrypted)
            
            # Test decryption
            test_decrypted = crypto_handler.decrypt(test_encrypted)
            print("\nDecrypted Data:")
            print(test_decrypted)
            
            return True
            
        except Exception as e:
            print(f"Test failed: {str(e)}")
            return False

# Run the test
test = TestDriverInfo()
test.run_test()


