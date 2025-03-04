# Voting App

This is a voting application that pulls the latest news, captures data from the camera for driver's licenses and other IDs, and allows you to vote while securing your data.

## Features

* **News Fetching:** Retrieves the latest news.
* **ID Verification:** Captures and processes driver's license/ID data using the device camera.
* **Secure Data Handling:** Encrypts and securely stores user data.
* **Voting:** Enables users to vote for candidates after successful ID verification.

## Project Structure


BANGWAGON/
├── Assets/
│   ├── 8c7dc827adf0f59f75be23feafe601f8b5010b9073d4d103c0f5f940f78abd47.jpg  # Image asset
│   ├── DougFord-scaled.jpeg                                                    # Image asset
│   ├── DougFord2.jpeg                                                          # Image asset
│   ├── gpo-mike-schreiner-headshot-2021-bricks-1.jpg                           # Image asset
│   ├── marit-stiles-ontario-ndp-leader.avif                                     # Image asset
├── Pages/
│   ├── Candidates.html                                                         # Candidates page
│   ├── Confirmation.html                                                       # Confirmation page
│   ├── HomePage.html                                                           # Homepage
│   ├── Verification.html                                                       # Verification page
│   ├── Voting.html                                                             # Voting page
├── Scripts/
│   ├── __pycache__/                                                            # Python bytecode cache
│   ├── .env                                                                    # Environment variables
│   ├── cadi.js                                                                 # JavaScript logic (likely related to candidates)
│   ├── connect.py                                                              # Python script for database connection
│   ├── encrypt.py                                                              # Python script for encryption
│   ├── gg.py                                                                   # Python script (purpose unclear, needs description)
│   ├── license_details.json                                                    # JSON file for license details
│   ├── license.py                                                              # Python script for license handling
│   ├── news.js                                                                 # JavaScript logic for news display
│   ├── sendEmail.js                                                            # JavaScript logic for sending emails
│   ├── server.js                                                               # JavaScript server-side logic
│   ├── server.py                                                               # Python server-side logic
│   ├── test.py                                                                 # Python testing script
├── Styles/
│   ├── home.css                                                                # Styles for homepage
│   ├── candi.css                                                               # Styles for candidates page
│   ├── Veri.css                                                                # Styles for verification page
│   ├── vote.css                                                                # Styles for voting page
├── Key&IV.enc                                                                  # Encrypted key and IV for encryption
├── license_details.json                                                        # JSON file for license details (duplicate, consider removing)
├── package.json                                                                # Node.js package configuration







## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/your-repo/voting-app.git](https://github.com/your-repo/voting-app.git)
    cd voting-app
    ```

2.  **Environment Variables:**

    * Create a `.env` file in the `Scripts/` directory.
    * Add the following environment variables to the `.env` file, replacing the placeholders with your actual values:

        ```
        TWITTER_BEARER_TOKEN=your_twitter_bearer_token
        TWITTER_ACCESS_TOKEN=your_twitter_access_token
        TWITTER_ACCESS_SECRET=your_twitter_access_secret
        MJ_APIKEY_PUBLIC=your_mailjet_public_key
        MJ_APIKEY_PRIVATE=your_mailjet_private_key
        DB_PASSWORD=your_mongodb_password
        ```

3.  **Install Dependencies:**
    * if using node.js for server.js run `npm install`
    * if using python for server.py make sure you have the required libraries installed. You can use pip. for example `pip install flask pymongo requests python-dotenv`

4.  **Run the Server:**

    * For the python server, navigate to the `Scripts` directory and run:

        ```bash
        python server.py
        ```
    * For the node.js server, navigate to the `Scripts` directory and run:
        ```bash
        node server.js
        ```

5.  **Access the Application:**

    * Open your web browser and navigate to `http://localhost:5000`.

## Notes

* Ensure that you have the necessary dependencies installed for both Python and JavaScript components.
* Replace the placeholder values in the `.env` file with your actual API keys and database credentials.
* The `Key&IV.enc` file is used for encryption. Ensure it is handled securely.
* The license_details.json file stores information extracted from the IDs. Ensure it is handled securely.
* The `__pycache__` folder is auto generated by python and can be ignored.
* The package.json file is used for node.js dependency management.
* The server.py and server.js files are the backend of the application.
