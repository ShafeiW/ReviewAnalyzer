from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, T5ForConditionalGeneration, T5Tokenizer

# Load Sentiment Analysis Model
class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(\"distilbert-base-uncased\")
        self.model = AutoModelForSequenceClassification.from_pretrained(\"distilbert-base-uncased-finetuned-sst-2-english\")
        self.pipeline = pipeline(\"sentiment-analysis\", model=self.model, tokenizer=self.tokenizer)

    def analyze(self, text):
        return self.pipeline(text)

# Load Summarization Model
class ReviewSummarizer:
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained(\"t5-small\")
        self.model = T5ForConditionalGeneration.from_pretrained(\"t5-small\")

    def summarize(self, text):
        inputs = self.tokenizer.encode(\"summarize: \" + text, return_tensors=\"pt\", max_length=512, truncation=True)
        outputs = self.model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
