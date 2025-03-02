require('dotenv').config();

const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 5001;

// Allow frontend to access backend (CORS issue fix)
app.use(cors());

const BEARER_TOKEN = process.env.TWITTER_BEARER_TOKEN || "YOUR_BEARER_TOKEN_HERE";

// API route to get tweets
app.get('/getTweets', async (req, res) => {
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

        res.json(response.data);  // Send tweets to frontend
    } catch (error) {
        console.error("Error fetching tweets:", error.response ? error.response.data : error.message);
        res.status(500).json({ error: "Failed to fetch tweets" });
    }
});

// Start Express server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);

    app.get('/getTweets', async (req, res) => {
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
    
            res.json(response.data);  // Send tweets to frontend
        } catch (error) {
            console.error("Error fetching tweets:", error.response?.data || error.message);
            res.status(error.response?.status || 500).json({ 
                error: "Failed to fetch tweets",
                details: error.response?.data || error.message
            });
        }
    });
    
});
