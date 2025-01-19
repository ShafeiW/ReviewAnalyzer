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
    data = request.json
    url = data.get("url")
    
    # Scrape reviews
    reviews = scrape_amazon_reviews(url)
    if not reviews:
        return jsonify({"error": "No reviews found or invalid URL."}), 400

    # Analyze sentiment
    sentiment_results = {"positive": 0, "neutral": 0, "negative": 0}
    keyword_counter = Counter()

    for review in reviews:
        sentiment, _ = analyzer.predict(review)
        if sentiment == 0:
            sentiment_results["negative"] += 1
        elif sentiment == 1:
            sentiment_results["neutral"] += 1
        else:
            sentiment_results["positive"] += 1
        
        # Extract keywords
        keywords = extract_keywords(review)
        keyword_counter.update(keywords)

    # Format results
    top_keywords = keyword_counter.most_common(10)
    return jsonify({
        "sentiments": sentiment_results,
        "keywords": top_keywords,
        "reviews": reviews
    })


def extract_keywords(text):
    words = re.findall(r"\b\w+\b", text.lower())
    common_words = set(["the", "is", "and", "it", "to", "of", "a", "in", "for", "on", "with", "as", "this", "that"])
    keywords = [word for word in words if word not in common_words]
    return keywords

if __name__ == "__main__":
    app.run(debug=True)
