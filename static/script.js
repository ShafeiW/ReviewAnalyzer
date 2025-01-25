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

        const data = await response.json();

        // Handle errors
        if (!response.ok || data.error) {
            throw new Error(data.error || data.message || 'An error occurred');
        }

        // Extract data from the response
        const { sentiment_summary, analyzed_reviews, total_reviews, processed_reviews } = data;

        // Create the results HTML
        const resultsHTML = `
            <h2>Sentiment Analysis Results</h2>
            <div class="summary-stats">
                <p>Total Reviews Analyzed: ${processed_reviews} of ${total_reviews}</p>
                <p>Average Rating: ${sentiment_summary.average_rating.toFixed(1)} / 5</p>
                <p>Average Confidence: ${(sentiment_summary.average_confidence * 100).toFixed(1)}%</p>
            </div>
            
            <div class="sentiment-breakdown">
                <h3>Rating Distribution:</h3>
                <p>★★★★★ Very Positive: ${sentiment_summary.very_positive}</p>
                <p>★★★★☆ Positive: ${sentiment_summary.positive}</p>
                <p>★★★☆☆ Neutral: ${sentiment_summary.neutral}</p>
                <p>★★☆☆☆ Negative: ${sentiment_summary.negative}</p>
                <p>★☆☆☆☆ Very Negative: ${sentiment_summary.very_negative}</p>
            </div>

            <div class="reviews-section">
                <h3>Analyzed Reviews:</h3>
                <ul>
                    ${analyzed_reviews.map(review => `
                        <li class="review-item">
                            <div class="review-text">${review.review_text}</div>
                            <div class="review-stats">
                                <span class="rating">Predicted Rating: ${review.predicted_rating}/5</span>
                                <span class="confidence">Confidence: ${(review.confidence * 100).toFixed(1)}%</span>
                            </div>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;

        resultsDiv.innerHTML = resultsHTML;

    } catch (error) {
        console.error("Error:", error);
        resultsDiv.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
});