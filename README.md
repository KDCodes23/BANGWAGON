Voting App
This is a voting application that pulls the latest news, captures data from the camera for driver's licenses and other IDs, and allows you to vote while securing your data.

Features
News Fetching: Pulls the latest news.
ID Verification: Captures and processes driver's license data using the camera.
Secure Data Handling: Encrypts and stores user data securely.
Voting: Allows users to vote for candidates after successful ID verification.
Project Structure
BANGWAGON/
├── Assets/
│   ├── 8c7dc827adf0f59f75be23feafe601f8b5010b9073d4d103c0f5f940f78abd47.jpg
│   ├── DougFord-scaled.jpeg
│   ├── DougFord2.jpeg
│   ├── gpo-mike-schreiner-headshot-2021-bricks-1.jpg
│   ├── marit-stiles-ontario-ndp-leader.avif
├── Pages/
│   ├── Candidates.html
│   ├── Confirmation.html
│   ├── HomePage.html
│   ├── Verification.html
│   ├── Voting.html
├── Scripts/
│   ├── __pycache__/
│   ├── .env
│   ├── cadi.js
│   ├── connect.py
│   ├── encrypt.py
│   ├── gg.py
│   ├── license_details.json
│   ├── license.py
│   ├── news.js
│   ├── sendEmail.js
│   ├── server.js
│   ├── server.py
│   ├── test.py
├── Styles/
│   ├── home.css
│   ├── candi.css
│   ├── Veri.css
│   ├── vote.css
├── Key&IV.enc
├── license_details.json
├── package.json

git clone https://github.com/your-repo/voting-app.git
cd voting-app

TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
MJ_APIKEY_PUBLIC=your_mailjet_public_key
MJ_APIKEY_PRIVATE=your_mailjet_private_key
DB_PASSWORD=your_mongodb_password

python [server.py](http://_vscodecontentref_/0)
http://localhost:5000
