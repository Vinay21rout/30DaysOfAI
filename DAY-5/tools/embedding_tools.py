from utils.mcp import mcp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@mcp.tool()
def text_similarity(text1: str, text2: str):
    """
    Compute cosine similarity.
    """

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([text1, text2])

    similarity = cosine_similarity(vectors)[0][1]

    return {
        "similarity": round(float(similarity), 4)
    }