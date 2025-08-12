import streamlit as st
import requests
import os

# ===== Backend API URL =====
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Smart RAG", page_icon="📄", layout="wide")

st.title("📄 Smart RAG – Document Q&A")

# Sidebar for file upload
st.sidebar.header("📂 Upload a Document")
uploaded_file = st.sidebar.file_uploader(
    "Choose a file",
    type=["pdf", "docx", "txt", "csv", "jpg", "jpeg", "png", "db"]
)

if uploaded_file:
    st.sidebar.success(f"Uploaded: {uploaded_file.name}")
    if st.sidebar.button("📤 Process Document"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        res = requests.post(f"{API_BASE_URL}/upload", files=files)
        if res.status_code == 200:
            st.sidebar.success("✅ Document processed and stored in vector DB!")
        else:
            st.sidebar.error(f"❌ Upload failed: {res.text}")

# Main Q&A interface
st.subheader("💬 Ask a Question")
question = st.text_input("Type your question here...")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        res = requests.post(
            f"{API_BASE_URL}/ask",
            json={"question": question}
        )
        if res.status_code == 200:
            answer = res.json().get("answer", "No answer returned.")
            st.markdown(f"**Answer:** {answer}")
        else:
            st.error(f"❌ Error: {res.text}")

# Optional: Display server health
if st.sidebar.button("🔍 Check Server Health"):
    try:
        r = requests.get(f"{API_BASE_URL}/health")
        st.sidebar.info(f"Server says: {r.json()}")
    except:
        st.sidebar.error("Server not reachable.")
