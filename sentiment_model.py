import torch
import torch.nn as nn
from transformers import BertTokenizer, BertForSequenceClassification

class SentimentAnalyzer:
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)  # Positive, Neutral, Negative
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        return torch.argmax(probs).item(), probs.detach().cpu().numpy()
