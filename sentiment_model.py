from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import numpy as np

class SentimentAnalyzer:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        # Using a BERT model specifically fine-tuned for sentiment analysis
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def preprocess_text(self, text):
        # Enhanced preprocessing
        text = re.sub(r"<.*?>", "", text)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Preserve important punctuation that carries sentiment
        text = re.sub(r'([!?.]){2,}', r'\1', text)  # Normalize repeated punctuation
        
        # Handle common emoticons
        text = re.sub(r':\)|:-\)', ' positive ', text)
        text = re.sub(r':\(|:-\(', ' negative ', text)
        
        # Handle negations
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"n't", " not", text)
        
        return text.strip()

    def predict(self, text):
        # Preprocess text
        text = self.preprocess_text(text)
        
        # Tokenize and prepare input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Move inputs to the same device as model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Add error handling
        try:
            with torch.no_grad():
                outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            probabilities = probabilities.detach().cpu().numpy()
            sentiment = probabilities.argmax(axis=-1)[0]
            confidence = probabilities.max()
            
            # Apply confidence threshold
            if confidence < 0.6:  # Adjust threshold as needed
                return None, probabilities  # Return None for uncertain predictions
                
            return sentiment, probabilities
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return None, None

    def predict_batch(self, texts, batch_size=16):
        """Add batch processing for better performance"""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Process batch similar to single prediction
            # ... implementation here ...
        return results