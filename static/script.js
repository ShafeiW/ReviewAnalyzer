document.getElementById("review-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const url = document.getElementById("url").value;
    const numPages = document.getElementById("num_pages").value;

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Analyzing reviews...</p>";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, num_pages: numPages }),
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();
        const { sentiment_counts, reviews } = data;

        resultsDiv.innerHTML = `
            <h2>Sentiment Analysis Results</h2>
            <p>Positive: ${sentiment_counts.positive}</p>
            <p>Neutral: ${sentiment_counts.neutral}</p>
            <p>Negative: ${sentiment_counts.negative}</p>
            <h3>Reviews:</h3>
            <ul>${reviews.map(r => `<li>${r.review} (${['Negative', 'Neutral', 'Positive'][r.sentiment]})</li>`).join('')}</ul>
        `;
    } catch (error) {
        resultsDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});
