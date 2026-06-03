# Installing Streamlit and local tunnel utility for Kaggle web preview
!pip install -q streamlit
!npm install -q -g localtunnel
print("✓ Streamlit and Localtunnel successfully installed!")
%%writefile app.py
import streamlit as st
import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_openai import ChatOpenAI

st.set_page_config(page_title='AI Assistant', page_icon='🤖', layout='wide')

try:
    @st.cache_resource
    def init_chromadb_with_dummy_data():
        """Initializes ChromaDB and inserts complete policy text directly to guarantee answers."""
        client = chromadb.PersistentClient(path='./chromadb')
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        
        collection = client.get_or_create_collection(
            name='company_docs',
            embedding_function=default_ef
        )
        
        # Injecting direct text data so the system is never empty
        if collection.count() == 0:
            policies = [
                "Remote Work Guidelines: Employees can work from home up to 3 days per week with manager approval. Core working hours for remote tracking are 10:00 AM to 4:00 PM. Permanent work from home requires HR executive escalation.",
                "Vacation and Time Off Policies: All full-time employees are entitled to 25 days of annual vacation leave per calendar year. Emergency time off must be logged via the HR portal at least 2 hours before shifts.",
                "Parental Leave Benefits: The company provides 16 weeks of fully paid maternity leave for birth mothers and 4 weeks of fully paid paternity leave for secondary caregivers. Benefits apply immediately after probation."
            ]
            collection.add(
                documents=policies,
                ids=[f"policy_{i}" for i in range(len(policies))],
                metadatas=[{"source": "hr_handbook"} for _ in policies]
            )
        return collection

    @st.cache_resource
    def init_llm():
        # Safeguard dummy key configuration to prevent API crashes
        if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "sk-proj-YOUR_OPENAI_KEY_HERE":
            os.environ["OPENAI_API_KEY"] = "dummy-key-for-local-retrieval"
        return ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

    collection = init_chromadb_with_dummy_data()
    llm = init_llm()

    def get_rag_response(query, n_results=1):
        try:
            results = collection.query(query_texts=[query], n_results=n_results)
            if not results['documents'] or not results['documents'][0]:
                return 'No relevant information found in documents.'
            
            context = '\n'.join(results['documents'][0])
            
            # Since OpenAI key is local/dummy, cleanly return the exact matched chunk
            return f"🤖 **[Context Retrieved From ChromaDB Successfully!]**\n\n{context}"
        except Exception as e:
            return f'Error: {str(e)}'

    # Application UI Configuration
    st.title('🏢 Company Knowledge Assistant')
    st.markdown('Ask me anything about company policies!')

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header('ℹ️ About')
        st.markdown("Powered by local ChromaDB Vector Search.")
        st.divider()
        st.metric('Documents Indexed', collection.count())
        st.metric('Messages in Chat', len(st.session_state.messages))
        st.divider()
        if st.button('Clear Chat History'):
            st.session_state.messages = []
            st.rerun()

    if len(st.session_state.messages) == 0:
        with st.chat_message('assistant'):
            st.write("Hi! I'm your company knowledge assistant. 👋 Ask me a question to get started.")

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.write(message['content'])

    if prompt := st.chat_input('Ask a question...'):
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.write(prompt)
            
        with st.chat_message('assistant'):
            with st.spinner('Searching database...'):
                response = get_rag_response(prompt)
                st.write(response)
        st.session_state.messages.append({'role': 'assistant', 'content': response})

except Exception as e:
    st.error(f'System Error: {str(e)}')
    st.stop()
  # Extract the public IP to use as the password tunnel gateway
!curl ipv4.icanhazip.com
import subprocess
import threading
import time

print("🧹 Cleaning older background processes...")
!pkill -f streamlit
!pkill -f localtunnel
!pkill -f ngrok
!pkill -f ssh

print("🚀 Starting Streamlit background server...")
def run_app():
    subprocess.Popen("streamlit run app.py --server.port=8501 --server.address=0.0.0.0", shell=True)

threading.Thread(target=run_app, daemon=True).start()
time.sleep(5)

print("\n🌐 Generating dynamic clean public link via Serveo...")
print("Click the link below when it appears. Ignore any 'warning' or click 'Continue' if asked.")
print("="*60)

# This exposes port 8501 globally without requiring any login/token/password
!ssh -o StrictHostKeyChecking=no -R 80:localhost:8501 serveo.net
