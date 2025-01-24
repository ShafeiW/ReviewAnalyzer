document.getElementById("review-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const url = document.getElementById("url").value;
    const numPages = document.getElementById("num_pages").value;

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Analyzing reviews... This may take a moment.</p>";

    try {
        // Send POST request to the backend
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, num_pages: numPages }),
        });

        // Handle non-200 responses
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();

        // Check if the backend returned an error
        if (data.error) {
            resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        const { sentiment_counts, reviews } = data;

        // Display the results
        resultsDiv.innerHTML = `
            <h2>Sentiment Analysis Results</h2>
            <p>Positive: ${sentiment_counts.positive}</p>
            <p>Neutral: ${sentiment_counts.neutral}</p>
            <p>Negative: ${sentiment_counts.negative}</p>
            <h3>Reviews:</h3>
            <ul>${reviews.map(r => `
                <li>
                    ${r.review} 
                    (${['Negative', 'Neutral', 'Positive'][r.sentiment]}) 
                    - Probabilities: ${r.probabilities.map(p => p.toFixed(2)).join(', ')}
                </li>
            `).join('')}</ul>
        `;


    } catch (error) {
        console.error("Error during fetch:", error);
        resultsDiv.innerHTML = `<p>An error occurred: ${error.message}</p>`;
    }
});
