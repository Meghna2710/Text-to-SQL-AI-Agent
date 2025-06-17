import requests
import streamlit as st

API_URL = "http://localhost:8000/query"

st.title("🧠 Text-to-SQL Generator AI Agent")
query = st.text_input("Enter your question:")

if st.button("Submit") and query.strip():
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"question": query})
            result = response.json()
            st.subheader("Generated SQL")
            st.code(result["sql"], language="sql")
            st.subheader("Answer")
            st.success(result["answer"])
        except Exception as e:
            st.error(f"API call failed: {e}")