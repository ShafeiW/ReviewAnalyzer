from flask import Flask, request, jsonify, render_template
from sentiment_model import SentimentAnalyzer
from flask_cors import CORS
import re
from scrape import scrape_amazon_reviews
from collections import Counter

app = Flask(__name__)
CORS(app)

# Load sentiment analysis model
# Verify the sentiment analysis model
analyzer = SentimentAnalyzer()
sample_review = "This product is amazing! The quality exceeded my expectations."
sentiment, probabilities = analyzer.predict(sample_review)
print(f"Sample review sentiment: {sentiment}, probabilities: {probabilities}")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_reviews():
    print("Analyze route hit")  # Debugging log
    data = request.json
    print(f"Received data: {data}")  # Debugging log
    """Scrape and analyze reviews."""
    try:
        data = request.json
        print(f"Received data: {data}")  # Debugging log

        product_url = data.get("url")
        num_pages = int(data.get("num_pages", 1))
        if not product_url:
            return jsonify({"error": "Product URL is required"}), 400

        # Scrape reviews
        reviews = scrape_amazon_reviews(product_url, num_pages)
        if not reviews:
            return jsonify({"error": "No reviews found or scraping failed."}), 400

        # Analyze sentiment
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        analyzed_reviews = []

        for review in reviews:
            sentiment, _ = analyzer.predict(review)
            if sentiment == 0:
                sentiment_counts["negative"] += 1
            elif sentiment == 1:
                sentiment_counts["neutral"] += 1
            else:
                sentiment_counts["positive"] += 1
            analyzed_reviews.append({"review": review, "sentiment": sentiment})

        # Return results
        return jsonify({
            "sentiment_counts": sentiment_counts,
            "reviews": analyzed_reviews
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500



def extract_keywords(text):
    words = re.findall(r"\b\w+\b", text.lower())
    common_words = set(["the", "is", "and", "it", "to", "of", "a", "in", "for", "on", "with", "as", "this", "that"])
    keywords = [word for word in words if word not in common_words]
    return keywords

if __name__ == "__main__":
    app.run(debug=True)
