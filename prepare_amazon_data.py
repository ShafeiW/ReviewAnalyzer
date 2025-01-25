import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split
import logging
import os
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_binary_to_five_scale(row):
    """Convert binary sentiment to 5-scale rating using content analysis"""
    # Base rating from sentiment (1 or 5).
    base_rating = 5 if row['label'] == 1 else 1
    
    # Analyze review content for rating refinement.
    text = row['content'].lower()
    
    if row['label'] == 1:  # Positive reviews.
        if any(phrase in text for phrase in ['amazing', 'excellent', 'perfect', 'best']):
            return 5
        elif any(phrase in text for phrase in ['good but', 'okay', 'decent']):
            return 4
        return 4
    else:  # Negative reviews.
        if any(phrase in text for phrase in ['terrible', 'worst', 'awful']):
            return 1
        elif any(phrase in text for phrase in ['disappointing', 'mediocre']):
            return 2
        return 2

def download_and_prepare_data(sample_size=None):
    """
    Download and prepare Amazon reviews dataset using amazon_polarity.
    
    """
    logger.info("Loading Amazon Polarity dataset...")
    dataset = load_dataset("amazon_polarity", trust_remote_code=True)
    
    # Convert to DataFrame.
    train_data = dataset['train'].to_pandas()
    test_data = dataset['test'].to_pandas()
    
    # Create new DataFrames with all needed columns.
    train_df = pd.DataFrame()
    test_df = pd.DataFrame()
    
    logger.info("Converting binary ratings to 5-scale ratings...")
    
    # Process training data.
    train_df['review_text'] = train_data['content'].fillna('').astype(str)
    train_df['rating'] = train_data.apply(convert_binary_to_five_scale, axis=1)
    
    # Process test data.
    test_df['review_text'] = test_data['content'].fillna('').astype(str)
    test_df['rating'] = test_data.apply(convert_binary_to_five_scale, axis=1)
    
    # Take a sample if specified (useful for testing).
    if sample_size:
        train_df = train_df.sample(min(sample_size, len(train_df)), random_state=42)
        test_df = test_df.sample(min(sample_size//5, len(test_df)), random_state=42)
    
    logger.info(f"Train set size: {len(train_df)}")
    logger.info(f"Test set size: {len(test_df)}")
    
    # Create data directory if it doesn't exist.
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV.
    train_df.to_csv('data/amazon_reviews_train.csv', index=False)
    test_df.to_csv('data/amazon_reviews_test.csv', index=False)
    
    logger.info("Data saved to data/amazon_reviews_train.csv and data/amazon_reviews_test.csv")
    
    # Print some statistics.
    logger.info("\nRating distribution in training set:")
    print(train_df['rating'].value_counts().sort_index())
    
    # Print sample reviews for each rating.
    logger.info("\nSample reviews for each rating:")
    for rating in sorted(train_df['rating'].unique()):
        sample_review = train_df[train_df['rating'] == rating]['review_text'].iloc[0][:100]
        print(f"\nRating {rating}:")
        print(sample_review + "...")
    
    return train_df, test_df

if __name__ == "__main__":
    # Download and prepare data.
    train_df, test_df = download_and_prepare_data(sample_size=10000)  # Remove sample_size for full dataset