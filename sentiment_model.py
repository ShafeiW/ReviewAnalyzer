from transformers import BertTokenizer, BertForSequenceClassification
import torch
import re

class SentimentAnalyzer:
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name, num_labels=3
        )

    def preprocess_text(self, text):
        # Basic preprocessing
        text = re.sub(r"<.*?>", "", text)  # Remove HTML tags
        text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
        text = text.lower().strip()  # Convert to lowercase and strip spaces
        return text

    def predict(self, text):
        # Preprocess text
        text = self.preprocess_text(text)
        
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True, max_length=512
        )
        outputs = self.model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1).detach().cpu().numpy()
        sentiment = probabilities.argmax(axis=-1)[0]
        return sentiment, probabilities
