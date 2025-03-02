class DriverInfo {
    constructor(id, firstLastFullString, dob, fullAddress) {
        // Initialize default values
        this.id = null;
        this.firstName = null;
        this.lastName = null;
        this.dateOfBirth = null;
        this.streetNumber = null;
        this.streetName = null;
        this.city = null;
        this.province = null;
        this.postalCode = null;
        this.fullAddress = null;

        // Parse the provided data
        this.parseDriverInfo(id, firstLastFullString, dob, fullAddress);
    }

    parseDriverInfo(id, firstLastFullString, dob, fullAddress) {
        // Parse ID
        if (id && typeof id === 'string' && id.trim() !== '') {
            this.id = id.trim();
        }

        // Parse first and last name
        if (firstLastFullString && typeof firstLastFullString === 'string') {
            const names = firstLastFullString.trim().split(' ');
            if (names.length >= 2) {
                this.firstName = names[0];
                this.lastName = names.slice(1).join(' ');
            }
        }

        // Parse DOB
        if (dob && typeof dob === 'string' && dob.trim() !== '') {
            this.dateOfBirth = new Date(dob);
        }

        // Parse address
        if (fullAddress && typeof fullAddress === 'string') {
            const addressParts = fullAddress.split(',').map(part => part.trim());
            
            if (addressParts.length >= 3) {
                const streetParts = addressParts[0].split(' ');
                if (streetParts.length >= 2) {
                    this.streetNumber = streetParts[0];
                    this.streetName = streetParts.slice(1).join(' ');
                }

                this.city = addressParts[0];
                this.province = addressParts[1];
                this.postalCode = addressParts[2];
                this.fullAddress = fullAddress.trim();
            }
        }
    }
}

// Example usage:
// const driver = new DriverInfo(
//     "D1234-56789",
//     "John Smith",
//     "1990-01-01",
//     "206-320 KINGSWOOD DR, KITCHENER, ON, N2E 2K2"
// );