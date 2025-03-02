require('dotenv').config();
const accessToken = process.env.TWITTER_ACCESS_TOKEN;
const accessSecret = process.env.TWITTER_ACCESS_SECRET;

const axios = require('axios');


const BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKmRzgEAAAAAON7cXweYSFbh3NW8%2FK7PpcHWKlA%3DhtmxdXiEnVXUEIKsqkEBl04iKisRg6wiKmaRpAGEFvofpx73wB";

const fetchTweets = async () => {
    try {
        const response = await axios.get('https://api.twitter.com/2/tweets/search/recent', {
            headers: {
                Authorization: `Bearer ${BEARER_TOKEN}`
            },
            params: {
                query: 'Ontario politics',
                'tweet.fields': 'created_at,text,author_id',
                max_results: 1
            }
        });

        console.log(response.data);
    } catch (error) {
        console.error("Error fetching tweets:", error.response ? error.response.data : error.message);
    }
};

fetchTweets();
