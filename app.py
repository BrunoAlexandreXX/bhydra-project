import streamlit as st
from groq import Groq

# Configurações de interface do Streamlit
st.set_page_config(page_title="BHyDra IA", page_icon="🐍", layout="centered")

st.title("🐍 BHyDra IA")
st.caption("Motor: Llama 3.1 (via Groq Cloud) | Status: Online")

# Chave da Groq atualizada
CHAVE_GROQ = "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"

# Inicializa o cliente da Groq
client = Groq(api_key=CHAVE_GROQ)

# Gerenciamento de histórico de conversação (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens do histórico no chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Campo de entrada do utilizador
if prompt := st.chat_input("Diga 'Oi BHyDra'"):
    # Adiciona e exibe a mensagem do utilizador
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Chamada da API Groq com o modelo Llama 3.1 (Versão estável e atualizada)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            model="llama-3.1-8b-instant", # Versão que substitui a llama3-8b-8192
        )
        
        # Resposta gerada pela IA
        full_response = chat_completion.choices[0].message.content
        
        # Exibe e guarda a resposta da BHyDra
        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        # Tratamento de erro detalhado para o teu log de QA
        st.error(f"Erro de QA (Groq): {e}")
        st.info("Dica: Se o erro for 'model_decommissioned', verifique se o nome do modelo está correto.")