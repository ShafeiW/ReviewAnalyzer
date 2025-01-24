from flask import Flask, request, jsonify, render_template
from sentiment_model import SentimentAnalyzer
from flask_cors import CORS
import re
from scrape import scrape_amazon_reviews

app = Flask(__name__)
CORS(app)

# Load sentiment analysis model
analyzer = SentimentAnalyzer()
sample_review = "This product is amazing! The quality exceeded my expectations."
sentiment, probabilities = analyzer.predict(sample_review)
print(f"Sample review sentiment: {sentiment}, probabilities: {probabilities}")


@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_reviews():
    print("Analyze endpoint hit.")  # Debugging log
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
            sentiment, probabilities = analyzer.predict(review)
            probabilities = [float(prob) for prob in probabilities[0]]  # Convert to Python-native floats
            sentiment_label = "positive" if sentiment == 2 else "neutral" if sentiment == 1 else "negative"
            sentiment_counts[sentiment_label] += 1
            analyzed_reviews.append({
                "review": review,
                "sentiment": int(sentiment),  # Convert to Python-native int
                "probabilities": probabilities  # JSON-serializable list of floats
            })

        # Return results
        return jsonify({
            "sentiment_counts": {k: int(v) for k, v in sentiment_counts.items()},  # Ensure counts are Python ints
            "reviews": analyzed_reviews
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500




if __name__ == "__main__":
    app.run(debug=True)
