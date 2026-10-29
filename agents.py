
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_pdf_chunks():
    chunks = []

    pdf_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pdfs"
    )

    if not os.path.isdir(pdf_folder):
        os.makedirs(pdf_folder, exist_ok=True)
        return chunks

    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(os.path.join(pdf_folder, filename))

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text()

                if text:
                    chunks.append({
                        "text": text,
                        "source": filename,
                        "page": page_number
                    })

    return chunks

documents = load_pdf_chunks()

if documents:
    embeddings = embedding_model.encode(
        [document["text"] for document in documents]
    )

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
else:
    index = None

def classification_agent(state):
    prompt = f"""
    Classify this customer complaint.

    Category: Billing, Technical, Account, Delivery, or Other.
    Urgency: Low, Medium, or High.

    Complaint: {state["complaint"]}

    Return the category and urgency briefly.
    """

    response = llm.invoke(prompt)
    return {"classification": response.content}

def knowledge_agent(state):
    if index is None or not documents:
        return {
            "knowledge": "No relevant information was found in the policy PDFs."
        }

    question_embedding = embedding_model.encode(
        [state["complaint"]]
    ).astype("float32")

    distances, indices = index.search(
        question_embedding,
        k=min(3, len(documents))
    )

    retrieved = []

    for i in indices[0]:
        if i >= 0:
            document = documents[i]
            retrieved.append(
                f"Source: {document['source']}, "
                f"Page: {document['page']}\n"
                f"{document['text']}"
            )

    context = "\n\n".join(retrieved)

    prompt = f"""
    You are a customer support knowledge agent.

    Use the retrieved policy text below to identify relevant information.
    The policy may use different wording from the complaint.
    Summarize any relevant information found.
    If the policy does not contain relevant information, say so.
    Never invent company policies.

    Retrieved policy text:
    {context}

    Customer complaint:
    {state["complaint"]}
    """

    response = llm.invoke(prompt)

    return {"knowledge": response.content}


def response_agent(state):
    prompt = f"""
    You are a professional customer support agent.

    Write a polite, clear, and concise response to the customer.

    Use the complaint and retrieved knowledge to answer.
    Follow these rules:
    1. Never invent company policies or claim that a feature exists
       unless the provided knowledge supports it.
    2. If the retrieved knowledge does not contain the answer,
       clearly say that the information is not available in the
       current policy documents.
    3. Do not make promises about refunds, approvals, or outcomes.
    4. If more information or investigation is needed, explain this
       politely.
    5. Do not add unrelated advice or ask for unnecessary details.

    Customer complaint:
    {state["complaint"]}

    Retrieved knowledge:
    {state["knowledge"]}

    Classification:
    {state["classification"]}

    Write only the customer-facing response.
    """

    response = llm.invoke(prompt)

    return {"draft_response": response.content}

def review_agent(state):
    prompt = f"""
    Review the proposed response for unsupported claims.

    Use only the available information.
    Do not invent facts.

    Complaint: {state["complaint"]}
    Available information: {state["knowledge"]}
    Proposed response: {state["draft_response"]}

    Return the final response and whether human review is recommended.
    """

    response = llm.invoke(prompt)
    return {"review": response.content}