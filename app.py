import streamlit as st
from supabase import create_client
from groq import Groq
import uuid

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BHyDra IA", 
    page_icon="🐍", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. UI/CSS (Sidebar Neon e Ajustes) ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] { border-right: 2px solid #00ffa3; }
        .stChatInputContainer { padding-bottom: 20px; }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO COM SERVIÇOS ---
@st.cache_resource
def init_connections():
    try:
        sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        gq = Groq(api_key=st.secrets["GROQ_KEY"])
        return sb, gq, True
    except:
        return None, None, False

supabase, groq, conectado = init_connections()

# --- 4. FUNÇÕES DE OPERAÇÃO DO BANCO (CRUD) ---
def carregar_mensagens(chat_id):
    if conectado:
        res = supabase.table("chat_history").select("*").eq("chat_id", chat_id).order("created_at").execute()
        return [{"role": m["role"], "content": m["content"]} for m in res.data]
    return []

def apagar_chat(chat_id):
    if conectado and chat_id:
        try:
            # Exclusão em cascata manual (mensagens -> chat)
            supabase.table("chat_history").delete().eq("chat_id", chat_id).execute()
            supabase.table("chats").delete().eq("id", chat_id).execute()
            st.session_state.messages = []
            st.session_state.chat_id = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao apagar: {e}")

# --- 5. GESTÃO DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

# --- 6. BARRA LATERAL (MENU) ---
with st.sidebar:
    st.title("🐍 Menu BHyDra")
    
    # Botões de Ação Superior
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Novo Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_id = None
            st.rerun()
    with col2:
        if st.session_state.chat_id:
            if st.button("🗑️ Apagar", use_container_width=True, type="primary"):
                apagar_chat(st.session_state.chat_id)

    st.divider()
    
    # Gestão de Arquivos
    uploaded_file = st.file_uploader("📂 Anexar Documento", type=['pdf', 'txt'])
    
    st.divider()
    st.subheader("🕒 Histórico")
    
    if conectado:
        try:
            chats = supabase.table("chats").select("id, title").order("created_at", desc=True).limit(10).execute()
            for c in chats.data:
                label = f"💬 {c['title'][:20]}..."
                if st.button(label, key=c['id'], use_container_width=True):
                    st.session_state.chat_id = c['id']
                    st.session_state.messages = carregar_mensagens(c['id'])
                    st.rerun()
        except:
            st.caption("Erro ao carregar histórico.")
    else:
        st.error("Modo Offline")

# --- 7. ÁREA DE CHAT ---
st.title("🐍 BHyDra IA")

# Mostrar mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Processar entrada
if prompt := st.chat_input("Diga algo para a BHyDra..."):
    # Criar chat no banco se for o primeiro prompt
    if conectado and st.session_state.chat_id is None:
        titulo = (prompt[:30] + '...') if len(prompt) > 30 else prompt
        res = supabase.table("chats").insert({"title": titulo}).execute()
        st.session_state.chat_id = res.data[0]["id"]

    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if conectado:
        supabase.table("chat_history").insert({
            "chat_id": st.session_state.chat_id, "role": "user", "content": prompt
        }).execute()

    # Resposta da IA
    with st.chat_message("assistant", avatar="🐍"):
        try:
            ctx = f"\n[Arquivo: {uploaded_file.name}]" if uploaded_file else ""
            completion = groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": f"Você é a BHyDra IA.{ctx}"}] + st.session_state.messages
            )
            resp = completion.choices[0].message.content
            st.markdown(resp)
            
            st.session_state.messages.append({"role": "assistant", "content": resp})
            if conectado:
                supabase.table("chat_history").insert({
                    "chat_id": st.session_state.chat_id, "role": "assistant", "content": resp
                }).execute()
        except Exception as e:
            st.error(f"Erro na Groq: {e}")