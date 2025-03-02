import json
from datetime import datetime
from encrypt import CryptoHandler  # Import the encryption class
from pymongo import MongoClient  # Import MongoDB client

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
        print("\n=== RUNNING DRIVER INFO TESTS ===")
        test_results = []

        try:
            # Test case 1: Standard input
            print("\nTest Case 1: Standard input")
            test_driver1 = DriverInfo(
                "T9876-54321",
                "Jane Doe",
                "1985-06-15",
                "123 Main St, Toronto, ON, M5V 2K7"
            )
            
            test_json1 = test_driver1.to_json()
            print("Driver Info JSON:")
            print(test_json1)
            
            # Test encryption and decryption
            test_encrypted1 = crypto_handler.encrypt(test_json1)
            print("\nEncrypted Data:")
            print(test_encrypted1)
            
            test_decrypted1 = crypto_handler.decrypt(json.loads(test_encrypted1))
            print("\nDecrypted Data:")
            print(json.dumps(test_decrypted1, indent=4))
            
            # Verify data consistency
            assert test_driver1.id == "T9876-54321"
            assert test_driver1.first_name == "Jane"
            assert test_driver1.last_name == "Doe"
            assert test_driver1.date_of_birth.strftime("%Y-%m-%d") == "1985-06-15"
            test_results.append("Test Case 1: PASSED")
            
            # Test case 2: Multi-word last name
            print("\nTest Case 2: Multi-word last name")
            test_driver2 = DriverInfo(
                "D5678-90123",
                "Robert Van Johnson",
                "1972-11-30",
                "456 Oak Avenue, Vancouver, BC, V6B 5T4"
            )
            
            test_json2 = test_driver2.to_json()
            print("Driver Info JSON:")
            print(test_json2)
            
            # Verify multi-word last name is handled correctly
            assert test_driver2.first_name == "Robert"
            assert test_driver2.last_name == "Van Johnson"
            test_results.append("Test Case 2: PASSED")
            
            # Test case 3: Complex address
            print("\nTest Case 3: Complex address")
            test_driver3 = DriverInfo(
                "L1234-56789",
                "Maria Garcia",
                "1990-03-25",
                "789 West 23rd Avenue, Montreal, QC, H3H 1E9"
            )
            
            test_json3 = test_driver3.to_json()
            print("Driver Info JSON:")
            print(test_json3)
            
            # Verify complex address is parsed correctly
            assert test_driver3.street_number == "789"
            assert test_driver3.street_name == "West 23rd Avenue"
            assert test_driver3.city == "Montreal"
            assert test_driver3.province == "QC"
            test_results.append("Test Case 3: PASSED")

            # Test case 4: MongoDB integration
            print("\nTest Case 4: MongoDB Integration")

            # Ensure that the crypto_handler has a valid collection attribute for MongoDB
            if crypto_handler.collection is not None:
                try:
                    # Store driver info in MongoDB
                    doc_id = crypto_handler.encrypt_and_store(json.loads(test_json1))
                    print(f"Stored document with ID: {doc_id}")

                    # Retrieve and decrypt the stored data
                    retrieved_data = crypto_handler.retrieve_and_decrypt({"_id": doc_id})
                    print("Retrieved and decrypted data:")
                    print(json.dumps(retrieved_data, indent=4))

                    # Verify that the retrieved data matches the expected values
                    assert retrieved_data["id"] == test_driver1.id, "ID mismatch"
                    assert retrieved_data["first_name"] == test_driver1.first_name, "First name mismatch"

                    test_results.append("Test Case 4: PASSED")
                except Exception as e:
                    # Handle any exceptions that occur during MongoDB interaction
                    print(f"Error during MongoDB operation: {e}")
                    test_results.append(f"Test Case 4: FAILED ({str(e)})")
            else:
                print("MongoDB connection not available. Skipping test.")
                test_results.append("Test Case 4: SKIPPED (No MongoDB connection)")

            # Test case 5: Invalid input handling
            print("\nTest Case 5: Invalid input handling")
            test_driver5 = DriverInfo(
                "",  # Empty ID
                "Only FirstName",  # Missing last name
                "invalid-date",  # Invalid date format
                "Incomplete Address"  # Incomplete address
            )
            
            test_json5 = test_driver5.to_json()
            print("Driver Info JSON (with invalid inputs):")
            print(test_json5)
            
            # Verify invalid inputs are handled gracefully
            assert test_driver5.id is None
            assert test_driver5.first_name == "Only"
            assert test_driver5.last_name == "FirstName"
            assert test_driver5.date_of_birth is None
            test_results.append("Test Case 5: PASSED")
            
            # Print summary
            print("\n=== TEST SUMMARY ===")
            for result in test_results:
                print(result)
            
            return all("PASSED" in result for result in test_results)
            
        except Exception as e:
            print(f"Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# Run the comprehensive tests
if __name__ == "__main__":
    test = TestDriverInfo()
    success = test.run_test()
    print(f"\nOverall test result: {'SUCCESS' if success else 'FAILURE'}")