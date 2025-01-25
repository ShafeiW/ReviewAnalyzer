from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_path="./sentiment_model_finetuned"):
        """Initialize the sentiment analyzer with the fine-tuned model"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def preprocess_text(self, text):
        """Preprocess the input text"""
        text = str(text)  # Ensure text is string
        text = re.sub(r"<.*?>", "", text)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'([!?.]){2,}', r'\1', text)  # Normalize repeated punctuation
        text = re.sub(r':\)|:-\)', ' positive ', text)
        text = re.sub(r':\(|:-\(', ' negative ', text)
        text = re.sub(r"n't", " not", text)
        return text.strip()

    def predict(self, text, confidence_threshold=0.6):
        """
        Predict sentiment for a single text
        Returns:
        - rating: 1-5 star rating
        - confidence: prediction confidence
        - probabilities: raw probability distribution
        """
        text = self.preprocess_text(text)
        
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                probabilities = probabilities.cpu().numpy()[0]
                
                rating = probabilities.argmax() + 1  # Convert to 1-5 scale
                confidence = probabilities.max()
                
                if confidence < confidence_threshold:
                    return None, confidence, probabilities
                    
                return rating, confidence, probabilities
                
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            return None, 0.0, None

    def predict_batch(self, texts, batch_size=32):
        """
        Predict sentiment for a batch of texts
        Returns list of (rating, confidence, probabilities) tuples
        """
        results = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                processed_batch = [self.preprocess_text(text) for text in batch]
                
                inputs = self.tokenizer(
                    processed_batch,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    probabilities = probabilities.cpu().numpy()
                    
                    for probs in probabilities:
                        rating = probs.argmax() + 1  # Convert to 1-5 scale
                        confidence = probs.max()
                        results.append((rating, confidence, probs))
                        
        except Exception as e:
            logger.error(f"Error in batch prediction: {str(e)}")
            
        return results

    def get_sentiment_explanation(self, rating, confidence):
        """Provide a human-readable explanation of the sentiment"""
        sentiment_map = {
            1: "very negative",
            2: "negative",
            3: "neutral",
            4: "positive",
            5: "very positive"
        }
        
        if rating is None:
            return "Unable to determine sentiment with sufficient confidence"
            
        confidence_percent = f"{confidence * 100:.1f}%"
        sentiment = sentiment_map.get(rating, "unknown")
        
        return f"Sentiment is {sentiment} ({rating} stars) with {confidence_percent} confidence"

def test_model():
    """Test the model with some example reviews"""
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "This product is amazing! Works perfectly.",
        "Terrible quality, broke after first use.",
        "It's okay, nothing special but does the job.",
        "Highly recommend this product, excellent value!",
        "Don't waste your money on this."
    ]
    
    for text in test_texts:
        rating, confidence, _ = analyzer.predict(text)
        explanation = analyzer.get_sentiment_explanation(rating, confidence)
        print(f"\nText: {text}")
        print(f"Analysis: {explanation}")

if __name__ == "__main__":
    test_model()