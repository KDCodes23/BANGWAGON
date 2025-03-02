document.addEventListener("DOMContentLoaded", function () {
    fetchNews();
    fetchTweets();
});

// Fetch Ontario Political News from NewsData.io
function fetchNews() {
    const apiKey = "pub_72674e189bc593de82af34ffffa362e2a1bca"; // Replace with your actual API key
    const apiUrl = `https://newsdata.io/api/1/news?apikey=${apiKey}&country=ca&category=politics&q=Ontario`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById("news-container");
            newsContainer.innerHTML = ""; // Clear previous content

            if (!data.results || data.results.length === 0) {
                newsContainer.innerHTML = "<p>No latest news available.</p>";
                return;
            }

            data.results.forEach(article => {
                const newsItem = document.createElement("div");
                newsItem.classList.add("news-article");

                const title = document.createElement("h3");
                title.textContent = article.title;

                const description = document.createElement("p");
                description.textContent = article.description || "No description available.";

                const link = document.createElement("a");
                link.href = article.link;
                link.textContent = "Read more";
                link.target = "_blank";

                newsItem.appendChild(title);
                newsItem.appendChild(description);
                newsItem.appendChild(link);
                newsContainer.appendChild(newsItem);
            });
        })
        .catch(error => {
            console.error("Error fetching news:", error);
            document.getElementById("news-container").innerHTML = "<p>Failed to load news.</p>";
        });
}

// Fetch Ontario Political Tweets from Node.js Backend
function fetchTweets() {
    fetch("http://localhost:5000/getTweets")
        .then(response => response.json())
        .then(data => {
            const tweetContainer = document.getElementById("tweets-container");
            tweetContainer.innerHTML = ""; // Clear previous content

            if (!data.data || data.data.length === 0) {
                tweetContainer.innerHTML = "<p>No recent tweets found.</p>";
                return;
            }

            data.data.forEach(tweet => {
                const tweetItem = document.createElement("div");
                tweetItem.classList.add("tweet");

                const content = document.createElement("p");
                content.textContent = tweet.text;

                tweetItem.appendChild(content);
                tweetContainer.appendChild(tweetItem);
            });
        })
        .catch(error => {
            console.error("Error loading tweets:", error);
            document.getElementById("tweets-container").innerHTML = "<p>Failed to load tweets.</p>";
        });
}
