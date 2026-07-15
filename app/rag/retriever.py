from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Global variables
model = None
ISSUES = []
SOLUTIONS = []
FAISS_INDEX = None

# Knowledge base path
KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base", "it_faqs.txt")

def load_model():
    """Load model lazily"""
    global model
    if model is None:
        print("Loading sentence transformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded!")
    return model

def load_knowledge_base():
    """Load and parse knowledge base file"""
    issues = []
    solutions = []
    
    with open(KB_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = content.strip().split("\n\n")
    
    for block in blocks:
        lines = block.strip().split("\n")
        issue = ""
        solution = ""
        
        for line in lines:
            if line.startswith("ISSUE:"):
                issue = line.replace("ISSUE:", "").strip()
            elif line.startswith("SOLUTION:"):
                solution = line.replace("SOLUTION:", "").strip()
        
        if issue and solution:
            issues.append(issue)
            solutions.append(solution)
    
    return issues, solutions

def initialize():
    """Initialize everything"""
    global ISSUES, SOLUTIONS, FAISS_INDEX
    
    if FAISS_INDEX is not None:
        return
    
    m = load_model()
    ISSUES, SOLUTIONS = load_knowledge_base()
    
    embeddings = m.encode(ISSUES)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    FAISS_INDEX = faiss.IndexFlatL2(dimension)
    FAISS_INDEX.add(embeddings)
    
    print(f"Knowledge base ready! {len(ISSUES)} issues indexed.")

def search_knowledge_base(query: str, top_k: int = 3) -> list:
    """Search knowledge base for similar issues.

    Returns an empty list on any failure (e.g. the embedding model can't be
    downloaded because of no internet access) instead of raising, so callers
    can treat "no results" and "search unavailable" the same way.
    """
    try:
        initialize()

        m = load_model()
        query_embedding = m.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        distances, indices = FAISS_INDEX.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(ISSUES):
                score = float(1 / (1 + distances[0][i]))
                results.append({
                    "issue": ISSUES[idx],
                    "solution": SOLUTIONS[idx],
                    "score": round(score, 3)
                })

        return results
    except Exception as e:
        print(f"search_knowledge_base failed: {e}")
        return []