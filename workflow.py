
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents import (
    classification_agent,
    knowledge_agent,
    response_agent,
    review_agent,
)
class SupportState(TypedDict):
    complaint: str
    classification: str
    knowledge: str
    draft_response: str
    review: str

workflow = StateGraph(SupportState)

workflow.add_node("classification", classification_agent)
workflow.add_node("knowledge", knowledge_agent)
workflow.add_node("response", response_agent)
workflow.add_node("review", review_agent)

workflow.add_edge(START, "classification")
workflow.add_edge("classification", "knowledge")
workflow.add_edge("knowledge", "response")
workflow.add_edge("response", "review")
workflow.add_edge("review", END)

support_app = workflow.compile()

def run_support_workflow(complaint: str):
    return support_app.invoke({
        "complaint": complaint,
        "classification": "",
        "knowledge": "",
        "draft_response": "",
        "review": "",
    })
