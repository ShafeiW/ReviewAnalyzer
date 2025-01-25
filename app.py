from flask import Flask, request, jsonify, render_template
from sentiment_model import SentimentAnalyzer
from flask_cors import CORS
import logging
from scrape import scrape_amazon_reviews

# Set up logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load sentiment analysis model.
try:
    analyzer = SentimentAnalyzer()
    # Test the model.
    sample_review = "This product is amazing! The quality exceeded my expectations."
    rating, confidence, probabilities = analyzer.predict(sample_review)
    logger.info(f"Model test - Rating: {rating}/5, Confidence: {confidence:.2f}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_reviews():
    """Analyze reviews from an Amazon product URL."""
    logger.info("Analyze endpoint hit")
    
    # Initialize variables.
    sentiment_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    analyzed_reviews = []
    total_confidence = 0
    processed_reviews = 0
    
    try:
        data = request.json
        logger.info(f"Received request data: {data}")

        product_url = data.get("url")
        num_pages = int(data.get("num_pages", 1))
        
        if not product_url:
            return jsonify({"error": "Product URL is required"}), 400

        # Scrape reviews.
        logger.info(f"Scraping {num_pages} pages of reviews from {product_url}")
        reviews_data = scrape_amazon_reviews(product_url, num_pages)
        
        if not reviews_data:
            logger.warning("No reviews found or scraping failed")
            return jsonify({"error": "No reviews found or scraping failed"}), 400

        logger.info(f"Processing {len(reviews_data)} reviews")

        # Process each review.
        for review_text in reviews_data:
            if not review_text or not isinstance(review_text, str):
                continue

            # Analyze sentiment.
            try:
                rating, confidence, probabilities = analyzer.predict(review_text)
                
                if rating is not None:  # Only count confident predictions.
                    sentiment_counts[rating] += 1
                    total_confidence += confidence
                    processed_reviews += 1
                    
                    analyzed_reviews.append({
                        "review_text": review_text[:500],  # Limit review text length in response.
                        "predicted_rating": int(rating),
                        "confidence": float(confidence),
                        "probabilities": [float(p) for p in probabilities] if probabilities is not None else None
                    })
            except Exception as e:
                logger.error(f"Error analyzing review: {str(e)}")
                continue

        # Calculate statistics.
        if processed_reviews > 0:
            avg_confidence = total_confidence / processed_reviews
            avg_rating = sum(k * v for k, v in sentiment_counts.items()) / processed_reviews
        else:
            avg_confidence = 0
            avg_rating = 0

        # Prepare response..
        response = {
            "sentiment_summary": {
                "very_negative": sentiment_counts[1],
                "negative": sentiment_counts[2],
                "neutral": sentiment_counts[3],
                "positive": sentiment_counts[4],
                "very_positive": sentiment_counts[5],
                "average_rating": float(avg_rating),
                "average_confidence": float(avg_confidence)
            },
            "analyzed_reviews": analyzed_reviews,
            "total_reviews": len(reviews_data),
            "processed_reviews": processed_reviews
        }

        logger.info(f"Successfully analyzed {processed_reviews} reviews")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "sentiment_counts": sentiment_counts,  # Include for debugging.
            "processed_reviews": processed_reviews
        }), 500

if __name__ == "__main__":
    app.run(debug=True)