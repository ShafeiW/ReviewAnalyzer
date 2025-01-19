from flask import Flask, render_template, request, jsonify
from app.scraper import scrape_newegg_reviews
from app.nlp_models import SentimentAnalyzer, ReviewSummarizer

app = Flask(__name__)

sentiment_analyzer = SentimentAnalyzer()
review_summarizer = ReviewSummarizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_reviews():
    product_url = request.form.get('product_url')
    reviews = scrape_newegg_reviews(product_url)

    for review in reviews:
        sentiment = sentiment_analyzer.analyze(review['text'])
        review['sentiment'] = sentiment[0]['label']
        review['summary'] = review_summarizer.summarize(review['text'])

    return jsonify(reviews)

if __name__ == \"__main__\":
    app.run(debug=True)
