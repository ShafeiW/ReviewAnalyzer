document.getElementById("review-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const url = document.getElementById("url").value;
    const response = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
    });

    const data = await response.json();
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    if (data.error) {
        resultsDiv.innerHTML = `<p>${data.error}</p>`;
    } else {
        const { sentiments, keywords, reviews } = data;
        resultsDiv.innerHTML = `
            <h2>Analysis Results</h2>
            <p>Positive: ${sentiments.positive}</p>
            <p>Neutral: ${sentiments.neutral}</p>
            <p>Negative: ${sentiments.negative}</p>
            <h3>Top Keywords</h3>
            <ul>${keywords.map(k => `<li>${k[0]} (${k[1]} mentions)</li>`).join("")}</ul>
        `;
    }
});
