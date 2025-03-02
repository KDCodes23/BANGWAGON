require('dotenv').config();

const axios = require('axios');
const BEARER_TOKEN = process.env.TWITTER_BEARER_TOKEN;

const fetchTweets = async () => {
    try {
        const response = await axios.get('https://api.twitter.com/2/tweets/search/recent', {
            headers: {
                Authorization: `Bearer ${BEARER_TOKEN}`
            },
            params: {
                query: 'Ontario politics',
                'tweet.fields': 'created_at,text,author_id',
                max_results: 15
            }
        });

        console.log(response.data);
    } catch (error) {
        console.error("Error fetching tweets:", error.response ? error.response.data : error.message);
    }
};

fetchTweets();
