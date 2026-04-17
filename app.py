import streamlit as st
from groq import Groq

# Configurações de interface
st.set_page_config(page_title="BHyDra IA", page_icon="🐍", layout="centered")

st.title("🐍 BHyDra IA")
st.caption("Motor: Llama 3.1 (via Groq Cloud) | Status: Online")

# SEGURANÇA: Agora buscamos a chave nas configurações do servidor (Secrets)
# Se estiver rodando local, ele buscará em .streamlit/secrets.toml
try:
    CHAVE_GROQ = st.secrets["GROQ_API_KEY"]
except:
    st.error("Erro de Configuração: Chave GROQ_API_KEY não encontrada nas Secrets.")
    st.stop()

# Inicializa o cliente Groq
client = Groq(api_key=CHAVE_GROQ)

# Gerenciamento de histórico (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Lógica de Chat
if prompt := st.chat_input("Diga 'Oi BHyDra'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            model="llama-3.1-8b-instant", 
        )
        
        full_response = chat_completion.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Erro de QA (Groq): {e}")