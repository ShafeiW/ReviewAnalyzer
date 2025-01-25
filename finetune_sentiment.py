import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    Trainer, 
    TrainingArguments,
    EarlyStoppingCallback
)
import pandas as pd
import numpy as np
from datasets import Dataset as HFDataset
from sklearn.metrics import accuracy_score, f1_score
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gpu():
    """Check GPU availability and print device information"""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.0f}MB")
        logger.info(f"CUDA Version: {torch.version.cuda}")
    else:
        device = torch.device("cpu")
        logger.warning("No GPU available, using CPU. This will be much slower!")
    return device

def tokenize_function(examples, tokenizer):
    """Tokenize the texts and prepare the targets"""
    tokenized = tokenizer(
        examples['review_text'],
        padding='max_length',
        truncation=True,
        max_length=512
    )
    
    tokenized['labels'] = [rating - 1 for rating in examples['rating']]
    return tokenized

def compute_metrics(eval_pred):
    """Compute metrics for evaluation"""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    return {
        'accuracy': accuracy_score(labels, predictions),
        'f1_macro': f1_score(labels, predictions, average='macro')
    }

def main():
    # Check GPU availability.
    device = check_gpu()
    
    # Configuration.
    MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
    TRAIN_DATA_PATH = "data/amazon_reviews_train.csv"
    TEST_DATA_PATH = "data/amazon_reviews_test.csv"
    OUTPUT_DIR = "./sentiment_model_finetuned"
    
    # Create necessary directories.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Initialize tokenizer and model.
    logger.info("Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=5,
        problem_type="single_label_classification"
    )
    
    # Move model to GPU if available.
    model = model.to(device)
    logger.info(f"Model moved to: {next(model.parameters()).device}")

    # Load and prepare data.
    logger.info("Loading data...")
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    val_df = pd.read_csv(TEST_DATA_PATH)
    
    # Convert to HuggingFace datasets.
    train_dataset = HFDataset.from_pandas(train_df)
    val_dataset = HFDataset.from_pandas(val_df)

    # Tokenize datasets.
    logger.info("Tokenizing datasets...")
    train_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=train_dataset.column_names
    )
    val_dataset = val_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=val_dataset.column_names
    )

    # Set format for pytorch.
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])
    val_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'labels'])

    # Training arguments optimized for GPU.
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=32,  # Increased for 8GB VRAM
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=50,
        eval_steps=200,
        save_steps=200,
        eval_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        learning_rate=2e-5,
        gradient_accumulation_steps=1,  # No need for accumulation with larger batch size.
        fp16=True,  # Enable mixed precision training.
        report_to="none",
        dataloader_num_workers=4,  # Increased for faster data loading.
        dataloader_pin_memory=True,
    )

    # Initialize trainer.
    logger.info("Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    # Train the model.
    logger.info("Starting training...")
    try:
        if torch.cuda.is_available():
            logger.info(f"Initial GPU memory: {torch.cuda.memory_allocated() / 1024**2:.2f}MB")
        trainer.train()
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise e

    # Save the final model.
    logger.info(f"Saving model to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Evaluate the model.
    logger.info("Evaluating model...")
    eval_results = trainer.evaluate()
    logger.info(f"Evaluation results: {eval_results}")
    
    # Save evaluation results.
    with open(os.path.join(OUTPUT_DIR, 'eval_results.txt'), 'w') as f:
        f.write(str(eval_results))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise e