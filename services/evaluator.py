from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def similarity_score(original: str, optimized: str) -> float:
    """
    TF-IDF cosine similarity between the original and optimized prompt.
    A lightweight proxy for "did we keep the same meaning" — enough to
    flag a rewrite that drifted too far, without an embeddings API call.
    """
    if not original.strip() or not optimized.strip():
        return 0.0

    vectorizer = TfidfVectorizer().fit([original, optimized])
    vectors = vectorizer.transform([original, optimized])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(float(score), 3)