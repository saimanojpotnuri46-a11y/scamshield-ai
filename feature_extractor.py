"""
ScamShield Feature Extractor
Combines TF-IDF n-grams (word & character level) with engineered behavioral,
linguistic, and URL heuristic feature vectors.
"""

import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any, Tuple

from src.preprocessor import (
    normalize_text,
    extract_urls,
    analyze_url,
    detect_pattern_triggers,
    compute_linguistic_features
)

class ScamShieldFeatureExtractor:
    def __init__(self, max_features_word: int = 2500, max_features_char: int = 2500):
        # Word-level n-grams capture semantic phrases and key vocabulary
        self.word_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=max_features_word,
            strip_accents="unicode",
            lowercase=True,
            sublinear_tf=True
        )
        # Char-level n-grams capture typo-squatting, leetspeak, and subdomain patterns
        self.char_vectorizer = TfidfVectorizer(
            ngram_range=(3, 5),
            analyzer="char",
            max_features=max_features_char,
            sublinear_tf=True
        )
        self.is_fitted = False

    def extract_dense_features(self, texts: List[str]) -> np.ndarray:
        """Extracts engineered heuristic feature matrix for a list of texts."""
        rows = []
        for text in texts:
            clean_text = normalize_text(text)
            ling = compute_linguistic_features(clean_text)
            patterns = detect_pattern_triggers(clean_text)
            urls = extract_urls(clean_text)
            
            max_url_risk = 0.0
            for u in urls:
                info = analyze_url(u)
                if info["url_risk_score"] > max_url_risk:
                    max_url_risk = float(info["url_risk_score"])
            
            features = [
                float(len(patterns["urgency_triggers"])),
                float(len(patterns["bait_triggers"])),
                float(len(patterns["credential_triggers"])),
                ling["uppercase_ratio"],
                ling["digit_ratio"],
                ling["exclamation_count"],
                ling["url_count"],
                ling["phone_count"],
                max_url_risk / 100.0,
                float(1.0 if "otp" in clean_text.lower() else 0.0),
                float(1.0 if any(b in clean_text.lower() for b in ["police", "warrant", "subpoena", "court"]) else 0.0),
                float(1.0 if any(b in clean_text.lower() for b in ["crypto", "bitcoin", "roi", "invest"]) else 0.0)
            ]
            rows.append(features)
        return np.array(rows, dtype=np.float32)

    def fit(self, texts: List[str]):
        """Fits both word and char vectorizers on training corpus."""
        normalized = [normalize_text(t) for t in texts]
        self.word_vectorizer.fit(normalized)
        self.char_vectorizer.fit(normalized)
        self.is_fitted = True
        return self

    def transform(self, texts: List[str]) -> csr_matrix:
        """Transforms text corpus into concatenated sparse representation."""
        if not self.is_fitted:
            raise ValueError("ScamShieldFeatureExtractor must be fitted before transforming.")
        normalized = [normalize_text(t) for t in texts]
        word_feats = self.word_vectorizer.transform(normalized)
        char_feats = self.char_vectorizer.transform(normalized)
        dense_feats = self.extract_dense_features(texts)
        dense_sparse = csr_matrix(dense_feats)
        
        # Combine word n-grams + char n-grams + heuristic dense signals
        combined = hstack([word_feats, char_feats, dense_sparse], format="csr")
        return combined

    def fit_transform(self, texts: List[str]) -> csr_matrix:
        """Convenience fit and transform."""
        self.fit(texts)
        return self.transform(texts)
