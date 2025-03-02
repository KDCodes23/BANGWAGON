document.addEventListener("DOMContentLoaded", function () {
    const apiKey = "pub_72580437a02dc7e453204306700799384ca8a"; // Replace with your NewsData.io API key
    const apiUrl = `https://newsdata.io/api/1/news?apikey=${apiKey}&country=ca&category=politics&q=Ontario`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById("news-container");
            newsContainer.innerHTML = ""; // Clear default loading text

            if (data.results.length === 0) {
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
});
