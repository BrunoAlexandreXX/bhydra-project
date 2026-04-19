import streamlit as st
from supabase import create_client
from groq import Groq
import uuid

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BHyDra IA", 
    page_icon="🐍", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Melhora a experiência no telemóvel
)

# --- 2. UI/CSS (Ajustes de Responsividade e Estética) ---
st.markdown("""
    <style>
        /* Ajuste para ecrãs de telemóvel */
        @media (max-width: 640px) {
            .main .block-container { padding: 1rem !important; }
            [data-testid="stSidebar"] { width: 85vw !important; }
        }
        [data-testid="stSidebar"] { border-right: 2px solid #00ffa3; }
        footer {visibility: hidden;}
        .stChatInputContainer { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXÃO COM SERVIÇOS (Com tratamento de erro robusto) ---
@st.cache_resource
def init_connections():
    try:
        # Tenta aceder aos secrets do Streamlit Cloud
        sb_url = st.secrets.get("SUPABASE_URL")
        sb_key = st.secrets.get("SUPABASE_KEY")
        gq_key = st.secrets.get("GROQ_KEY")
        
        if not all([sb_url, sb_key, gq_key]):
            return None, None, False
            
        sb = create_client(sb_url, sb_key)
        gq = Groq(api_key=gq_key)
        return sb, gq, True
    except Exception:
        return None, None, False

supabase, groq, conectado = init_connections()

# --- 4. FUNÇÕES CRUD ---
def carregar_mensagens(chat_id):
    if conectado and chat_id:
        try:
            res = supabase.table("chat_history").select("*").eq("chat_id", chat_id).order("created_at").execute()
            return [{"role": m["role"], "content": m["content"]} for m in res.data]
        except: return []
    return []

def apagar_chat(chat_id):
    if conectado and chat_id:
        try:
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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Novo", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_id = None
            st.rerun()
    with col2:
        if st.session_state.chat_id:
            if st.button("🗑️", use_container_width=True, type="primary"):
                apagar_chat(st.session_state.chat_id)

    st.divider()
    uploaded_file = st.file_uploader("📂 Documento", type=['pdf', 'txt'])
    
    st.divider()
    st.subheader("🕒 Histórico")
    
    if conectado:
        try:
            chats = supabase.table("chats").select("id, title").order("created_at", desc=True).limit(10).execute()
            for c in chats.data:
                if st.button(f"💬 {c['title'][:15]}...", key=c['id'], use_container_width=True):
                    st.session_state.chat_id = c['id']
                    st.session_state.messages = carregar_mensagens(c['id'])
                    st.rerun()
        except:
            st.caption("Erro ao ligar ao banco.")

# --- 7. ÁREA DE CHAT ---
st.title("🐍 BHyDra IA")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escreve para a BHyDra..."):
    # Verifica se a IA está disponível antes de começar
    if not conectado or groq is None:
        st.error("Serviço temporariamente offline. Verifique as chaves de API.")
        st.stop()

    if st.session_state.chat_id is None:
        titulo = (prompt[:30] + '...') if len(prompt) > 30 else prompt
        res = supabase.table("chats").insert({"title": titulo}).execute()
        st.session_state.chat_id = res.data[0]["id"]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    supabase.table("chat_history").insert({
        "chat_id": st.session_state.chat_id, "role": "user", "content": prompt
    }).execute()

    with st.chat_message("assistant", avatar="🐍"):
        try:
            ctx = f"\n[Documento: {uploaded_file.name}]" if uploaded_file else ""
            completion = groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": f"És a BHyDra IA. {ctx}"}] + st.session_state.messages
            )
            resp = completion.choices[0].message.content
            st.markdown(resp)
            
            st.session_state.messages.append({"role": "assistant", "content": resp})
            supabase.table("chat_history").insert({
                "chat_id": st.session_state.chat_id, "role": "assistant", "content": resp
            }).execute()
        except Exception as e:
            st.error(f"Erro na resposta: {e}")