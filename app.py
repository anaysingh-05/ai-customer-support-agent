import streamlit as st
from workflow import run_support_workflow

st.set_page_config(
    page_title="AI Customer Support System",
    layout="centered"
)

st.title("AI Customer Support Multi-Agent System")
st.write("Enter a customer complaint to get an AI-generated support response.")

complaint = st.text_area(
    "Customer Complaint",
    placeholder="Example: My payment was deducted twice.",
    height=150
)

if st.button("Process Complaint", type="primary"):
    if not complaint.strip():
        st.warning("Please enter a customer complaint.")
    else:
        with st.spinner("Agents are processing your complaint..."):
            try:
                result = run_support_workflow(complaint)

                st.subheader("Complaint Classification")
                st.write(result["classification"])

                st.subheader("Relevant Knowledge")
                st.write(result["knowledge"])

                st.subheader("Draft Response")
                st.write(result["draft_response"])

                st.subheader("Review Agent Result")
                st.write(result["review"])

            except Exception as e:
                st.error(f"An error occurred: {e}")