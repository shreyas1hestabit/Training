import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Enterprise Knowledge Intelligence", layout="wide")

st.title("Multimodal RAG System")
st.markdown("---")

# Sidebar for Navigation
option = st.sidebar.selectbox(
    "Choose Intelligence Mode",
    ("Document Chat (RAG)", "Image Analysis (Multimodal)", "Database Query (SQL)")
)

# 1. DOCUMENT CHAT (RAG)
if option == "Document Chat (RAG)":
    st.header("Documents Day1-2")
    query = st.text_input("Ask a question from PDFs/Markdown:")
    
    if st.button("Get Answer"):
        if query:
            with st.spinner("Searching knowledge base..."):
                response = requests.post(f"{BASE_URL}/ask", json={"question": query})
                if response.status_code == 200:
                    data = response.json()
                    st.success("Answer:")
                    st.write(data["answer"])
                    st.info(f"Confidence Score: {data.get('confidence', 'N/A')}")
                else:
                    st.error("API Error!")

# 2. IMAGE ANALYSIS (MULTIMODAL)
elif option == "Image Analysis (Multimodal)":
    st.header(" Multimodal Image RAG DAY3")
    uploaded_file = st.file_uploader("Upload an Image/Diagram", type=["png", "jpg", "jpeg"])
    image_query = st.text_input("What do you want to know about this image?")
    
    if uploaded_file and image_query:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        if st.button("Analyze Image"):
            with st.spinner("Performing OCR & Visual Search..."):
                files = {"file": uploaded_file.getvalue()}
                data_payload = {"question": image_query}
                # Note: Form data and Files handled together
                response = requests.post(f"{BASE_URL}/ask-image", files=files, data=data_payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis:")
                    st.write(result["answer"])
                    if "caption" in result:
                        st.caption(f"Visual Caption: {result['caption']}")
                else:
                    st.error("Failed to process image.")

# 3. DATABASE QUERY (SQL)
elif option == "Database Query (SQL)":
    st.header("SQL Day4")
    sql_query = st.text_input("Query your database (e.g., 'Show total sales by year'):")
    
    if st.button("Execute Query"):
        if sql_query:
            with st.spinner("Generating & Executing SQL..."):
                response = requests.post(f"{BASE_URL}/ask-sql", json={"question": sql_query})
                if response.status_code == 200:
                    data = response.json()
                    st.code(data["sql_query"], language="sql")
                    st.subheader("Result Table:")
                    if isinstance(data["result"], list):
                        st.table(data["result"])
                    else:
                        st.write(data["result"])
                else:
                    st.error("SQL Generation Failed.")