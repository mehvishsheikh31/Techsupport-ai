from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Knowledge base path
KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base", "it_faqs.txt")

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

def build_faiss_index(issues):
    """Build FAISS index from issues"""
    embeddings = model.encode(issues)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    return index, embeddings

# Load knowledge base on startup
print("Loading knowledge base...")
ISSUES, SOLUTIONS = load_knowledge_base()
FAISS_INDEX, _ = build_faiss_index(ISSUES)
print(f"Knowledge base loaded! {len(ISSUES)} issues indexed.")

def search_knowledge_base(query: str, top_k: int = 3) -> list:
    """Search knowledge base for similar issues"""
    query_embedding = model.encode([query])
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