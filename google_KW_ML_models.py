import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from keybert import KeyBERT
from nltk.corpus import stopwords
import spacy
from transformers import pipeline
from collections import Counter
from pathlib import Path
import re

import nltk
nltk.download('stopwords')

# Load Data
input_file = "C:\google_scraping\Data\google-overviewai-2024-11-12.csv"
df = pd.read_csv(input_file)
merge_df = df.drop(columns=["urls"])

# Define Keywords for Classification
branded_keywords = [
        r"\benzymedica\b", r"\bdigest gold\b", r"\bacid soothe\b", r"\bglutenease\b", r"\brepair gold\b",
        r"\bbean assist\b", r"\blypo gold\b", r"\bdigest spectrum\b", r"\baqua biome\b", r"\baquabiome omega 3\b",
        r"\bmagnesium mind\b", r"\bheart burn soothe\b", r"\bkids digest\b", r"\blipo\b", r"\bmagnesium motion\b",
        r"\bberberine phytosome\b", r"\bcandidase\b", r"\bdigest basic\b", r"\bglutease\b", r"\bveggiegest\b", r"\bserra\b",
        r"\benzymedica\s\w+\b", r"\bdairy assist\b", r"\bdairy assit\b"
]

functionality_keywords = [
    r"gut health", r"gut-friendly", r"digestive health", r"stomach aid", 
    r"acid relief", r"digestive aid", r"probiotic", r"prebiotic", 
    r"natural remedy", r"gut microbiome", r"intestinal health", 
    r"natural digestive", r"digestive support", r"healthlinedigestive"
]

generic_keywords = [
    r"digestive enzyme", r"digestive enzymes", r"digestive supplement", 
    r"digestive supplements", r"enzyme supplement", r"enzyme supplements",
    r"taking digestive enzymes", r"taking enzyme supplements", 
    r"taking enzyme", r"enzymes digestive"
]

# Clean Summary Column
def clean_summary(text):
    text = text.lower()
    text = re.sub(r"^(yes|no),?\s+", "", text)
    filler_words = r"\b(in fact|however|furthermore|indeed|also|thus|therefore|generally|basically|help|use)\b"
    text = re.sub(filler_words, "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

merge_df["cleaned_summary"] = merge_df["summary"].apply(clean_summary)

# Preprocess Text for Phrase Extraction
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    custom_stopwords = set(stopwords.words("english")).union(ENGLISH_STOP_WORDS)
    custom_stopwords.update(["enzyme", "enzymes", "digestive", "product", "products"])
    text = " ".join(word for word in text.split() if word not in custom_stopwords)
    doc = nlp(text)
    phrases = " ".join(chunk.text for chunk in doc.noun_chunks)
    return phrases

preprocessed_texts = merge_df["cleaned_summary"].astype(str).apply(preprocess_text)

# Classification Function
def classify_text(text):
    text = text.lower().strip()
    
    # Check for Branded Keywords
    for brand in branded_keywords:
        if brand in text:
            return 0  # Branded
    
    # Check for Generic Keywords
    if any(keyword in text for keyword in generic_keywords):
        return 2  # Generic
    
    # Check for Functionality Keywords
    if any(keyword in text for keyword in functionality_keywords):
        return 1  # Functionality

    # Default to Generic if no matches
    return 2

# Update the DataFrame classifications
merge_df["cluster"] = merge_df["cleaned_summary"].apply(classify_text)

# Keyword Extraction with KeyBERT
keybert_model = KeyBERT("all-MiniLM-L6-v2")

def extract_keywords(texts, ngram_range=(1, 3), num_keywords=15):
    return [[kw[0] for kw in keybert_model.extract_keywords(text, keyphrase_ngram_range=ngram_range, stop_words="english", top_n=num_keywords)] for text in texts]

merge_df["keywords"] = extract_keywords(preprocessed_texts)

# Categorize Clusters
def categorize_cluster(cluster_number):
    cluster_to_category = {
        0: "Branded",
        1: "Functionality",
        2: "Generic"
    }
    return cluster_to_category.get(cluster_number, "Unknown")

merge_df["category"] = merge_df["cluster"].apply(categorize_cluster)

# Create Clustered Keywords for N-Grams
def extract_ngrams(texts, ngram_range, num_keywords=10):
    return [[kw[0] for kw in keybert_model.extract_keywords(text, keyphrase_ngram_range=ngram_range, stop_words="english", top_n=num_keywords)] for text in texts]

def generate_ngrams_dataframe(merge_df, ngram_range, num_clusters, top_n=15):
    ngrams_data = []
    for cluster_num in range(num_clusters):
        cluster_texts = merge_df[merge_df["cluster"] == cluster_num]["cleaned_summary"]
        ngrams = extract_ngrams(cluster_texts, ngram_range=ngram_range, num_keywords=top_n)
        flattened_ngrams = [ngram for sublist in ngrams for ngram in sublist]
        ngram_counts = Counter(flattened_ngrams)
        ngrams_data.extend({
            "Cluster": cluster_num, 
            "Category": categorize_cluster(cluster_num), 
            "Ngram": ngram, 
            "Count": count
        } for ngram, count in ngram_counts.most_common(top_n))
    return pd.DataFrame(ngrams_data)

# Generate DataFrames for Bigrams and Trigrams
num_clusters = 3
bigrams_df = generate_ngrams_dataframe(merge_df, ngram_range=(2, 2), num_clusters=num_clusters)
trigrams_df = generate_ngrams_dataframe(merge_df, ngram_range=(3, 3), num_clusters=num_clusters)

# Named Entity Recognition
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")

def extract_named_entities(texts):
    entities_list = []
    for text in texts:
        entities = ner_pipeline(text)
        unique_entities = list({entity["word"] for entity in entities if entity["entity"].startswith("B-") or entity["entity"].startswith("I-")})
        entities_list.append(unique_entities)
    return entities_list

merge_df["named_entities"] = extract_named_entities(merge_df["cleaned_summary"])

# Save Results
output_file = "google_analysis_results.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    merge_df.to_excel(writer, index=False, sheet_name="Cleaned Summaries")
    bigrams_df.to_excel(writer, index=False, sheet_name="Bigram Keywords")
    trigrams_df.to_excel(writer, index=False, sheet_name="Trigram Keywords")

print(f"Results saved to {output_file}")