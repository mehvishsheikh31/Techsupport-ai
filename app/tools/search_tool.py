from app.rag.retriever import search_knowledge_base

def search_it_solution(query: str) -> dict:
    """Search knowledge base for IT solutions"""
    results = search_knowledge_base(query)
    
    if not results:
        return {
            "found": False,
            "message": "No solution found in knowledge base.",
            "solution": None
        }
    
    best_match = results[0]
    
    return {
        "found": True,
        "issue": best_match["issue"],
        "solution": best_match["solution"],
        "confidence": best_match["score"]
    }