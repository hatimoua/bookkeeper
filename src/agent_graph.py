from pydantic import BaseModel
from typing import List, Optional
from models import AccountSuggestion
from query import suggest_accounts, grade_confidence, format_suggestions_for_user, format_needs_review
from langgraph.graph import StateGraph, END
from config import settings


class GraphState(BaseModel):
    description : str
    suggestions : Optional[List[AccountSuggestion]] = None
    confidence : Optional[str] = None # 'low' | 'medium' | 'high'
    final_answer : Optional[str] = None
    

def run_retriever(state: GraphState) -> dict:
    suggestions = suggest_accounts(state.description, settings.SEARCH_LIMIT_K)
    return {"suggestions": suggestions}

def run_confidence(state: GraphState) -> dict:
    confidence = grade_confidence(state.suggestions)
    return {"confidence": confidence}

def route_based_on_confidence(state: GraphState) -> str: 
    if state.confidence == "high":
        return "finalize"
    else: 
        return "needs_review"

def finalize(state: GraphState) -> dict: 
    message = format_suggestions_for_user(state.suggestions, state.confidence)
    return {"final_answer" : message}

def needs_review(state: GraphState) -> dict:
    message = format_needs_review(state.suggestions, state.confidence)
    return {"final_answer" : message}

def create_graph():

    workflow = StateGraph(GraphState)
    workflow.add_node("retriever", run_retriever)
    workflow.add_node("confidence", run_confidence)
    workflow.add_node("finalize", finalize)
    workflow.add_node("needs_review", needs_review)

    workflow.add_edge("retriever", "confidence")

    workflow.add_conditional_edges(
        "confidence",
        route_based_on_confidence,
        {
            "finalize": "finalize",
            "needs_review": "needs_review"
        }
    )
    
    workflow.set_entry_point("retriever")
    workflow.add_edge("finalize", END)
    workflow.add_edge("needs_review", END)

    app = workflow.compile()
    return app 




