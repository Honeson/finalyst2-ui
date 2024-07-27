import streamlit as st
import requests
import uuid
from datetime import datetime

import re

# Page configuration
st.set_page_config(page_title="Equitech Financial Analyst", page_icon="📊", layout="wide")

# Custom CSS for a professional financial theme
st.markdown("""
<style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    .main {
        background-color: #2B2B2B;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stTextInput > div > div > input {
        background-color: #3C3C3C;
        color: #E0E0E0;
        border: 1px solid #555;
        border-radius: 5px;
        padding: 10px 15px;
        font-size: 16px;
    }
    .stButton > button {
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
        background-color: #007bff;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        width: 80%;
        word-wrap: break-word;
    }
    .chat-message.user {
        background-color: #1C3B4C;
        color: #E0E0E0;
        margin-left: auto;
    }
    .chat-message.bot {
        background-color: #3C3C3C;
        color: #E0E0E0;
        margin-right: auto;
    }
    .chat-message p {
        margin: 0;
        line-height: 1.4;
    }
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: #f8f9fa;
    }
    .sidebar .sidebar-content .stButton > button {
        background-color: #28a745;
        color: white;
    }
    .sidebar .sidebar-content .stButton > button:hover {
        background-color: #218838;
    }
    .stMetric {
        background-color: #3C3C3C;
        padding: 10px;
        border-radius: 5px;
        color: #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())
if 'chat_histories' not in st.session_state:
    st.session_state['chat_histories'] = [{'id': st.session_state['session_id'], 'history': [], 'timestamp': datetime.now()}]
if 'current_document' not in st.session_state:
    st.session_state['current_document'] = None
if 'document_processed' not in st.session_state:
    st.session_state['document_processed'] = False
if 'total_anchors' not in st.session_state:
    st.session_state['total_anchors'] = 0

# Backend URL
backend_url = "https://finalyst2.onrender.com//ask"
#backend_url = "http://127.0.0.1:8000/ask"

def process_markdown_file(input_file, output_file):
    with open(input_file, 'r') as file:
        content = file.read()

    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    anchor_id = 1
    
    def header_replacement(match):
        nonlocal anchor_id
        level, title = match.groups()
        anchor = f'<a name="{anchor_id}"></a>\n{level} {title}'
        anchor_id += 1
        return anchor

    processed_content = header_pattern.sub(header_replacement, content)

    with open(output_file, 'w') as file:
        file.write(processed_content)

    return anchor_id - 1

def ask_question(question, document):
    response = requests.post(backend_url, json={
        "question": question,
        "session_id": st.session_state['session_id'],
        "document": document
    })
    return response.json()['answer']

def get_current_chat_history():
    for chat in st.session_state['chat_histories']:
        if chat['id'] == st.session_state['session_id']:
            return chat['history']
    return []

def update_current_chat_history(history):
    for chat in st.session_state['chat_histories']:
        if chat['id'] == st.session_state['session_id']:
            chat['history'] = history
            chat['timestamp'] = datetime.now()
            return
    st.session_state['chat_histories'].append({'id': st.session_state['session_id'], 'history': history, 'timestamp': datetime.now()})

def display_full_document():
    with open("data/processed_output.md", "r") as file:
        content = file.read()
    
    st.markdown("""
    <script>
    function searchAndHighlight(text) {
        const content = document.querySelector('.stMarkdown');
        const regex = new RegExp(text, 'gi');
        content.innerHTML = content.innerHTML.replace(regex, match => `<mark>${match}</mark>`);
        const firstMatch = document.querySelector('mark');
        if (firstMatch) {
            firstMatch.scrollIntoView({behavior: 'smooth', block: 'center'});
        }
    }
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown(content, unsafe_allow_html=True)

# Process the markdown file if not already done
if not st.session_state['document_processed']:
    input_file = "data/output.md"
    output_file = "data/processed_output.md"
    total_anchors = process_markdown_file(input_file, output_file)
    st.session_state['document_processed'] = True
    st.session_state['total_anchors'] = total_anchors

# Sidebar for document selection and new conversation
with st.sidebar:
    st.image("static/logo.svg", width=150)
    st.title("Document Analysis")
    
    document_options = ["Nvidia", "Apple", "Tesla", "Amazon"]
    selected_document = st.selectbox("Select a Company:", document_options)
    
    if selected_document != st.session_state.get('current_document'):
        st.session_state['current_document'] = selected_document
        st.session_state['session_id'] = str(uuid.uuid4())
        st.session_state['chat_histories'].append({'id': st.session_state['session_id'], 'history': [], 'timestamp': datetime.now()})
        st.experimental_rerun()
    
    if st.button("Start New Analysis"):
        st.session_state['session_id'] = str(uuid.uuid4())
        st.session_state['chat_histories'].append({'id': st.session_state['session_id'], 'history': [], 'timestamp': datetime.now()})
        st.experimental_rerun()

    st.subheader("Recent Analyses")
    for i, chat in enumerate(reversed(st.session_state['chat_histories'][-5:])):
        with st.expander(f"{chat['timestamp'].strftime('%Y-%m-%d %H:%M')} - {len(chat['history'])} queries"):
            st.write(f"Document: {chat.get('document', 'Unknown')}")
            st.write(f"Queries: {len(chat['history'])}")
            if chat['id'] == st.session_state['session_id']:
                st.info("Current Analysis")

# Main chat interface
st.title(f"📊 Financial Analysis: {st.session_state['current_document']}")

# Tab layout
tab1, tab2 = st.tabs(["Analyze", "Full Document"])

with tab1:
    # Display current chat history
    current_history = get_current_chat_history()
    for chat in current_history:
        st.markdown(f'<div class="chat-message user"><p>👤 {chat["question"]}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-message bot"><p>🤖 {chat["answer"]}</p></div>', unsafe_allow_html=True)
        
        if "source_documents" in chat:
            st.subheader("Source Documents:")
            for i, doc in enumerate(chat["source_documents"]):
                page_content = doc['page_content'][:30]  # First 30 characters
                st.markdown(f"""
                <a href="#" onclick="switchToDocumentTab(); searchAndHighlight('{page_content}'); return false;">
                Source {i+1}: {page_content}...
                </a>
                """, unsafe_allow_html=True)
                

    # Input for new question
    question = st.text_input("Ask about the financial document...", key="question_input")

    # Handle question submission
    if st.button("Analyze") and question:
        with st.spinner("Analyzing..."):
            response = ask_question(question, st.session_state['current_document'])
        current_history.append({
            "question": question,
            "answer": response['answer'],
            "source_documents": response['source_documents']
        })
        update_current_chat_history(current_history)
        st.experimental_rerun()
  

with tab2:
    display_full_document()

st.markdown("""
<script>
function switchToDocumentTab() {
    const tabs = window.parent.document.querySelectorAll('.stTabs button[role="tab"]');
    tabs[1].click();
}
</script>
""", unsafe_allow_html=True)

# Key financial metrics
st.subheader("Key Financial Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenue", "$16.68B", "+41%")
with col2:
    st.metric("Net Income", "$4.02B", "+768%")
with col3:
    st.metric("EPS", "$1.62", "+765%")

# Footer
st.markdown("---")
st.write("🌐 Connected to: Equitech Ventures Financial Analysis Engine")
st.write("ℹ️ Pro Tips:")
st.write("- Select a document from the sidebar to start a new analysis.")
st.write("- Ask specific questions about financial metrics, trends, or comparisons.")
st.caption("Powered by Equitech Ventures | © 2024")
