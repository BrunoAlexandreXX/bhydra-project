import streamlit as st
from supabase import create_client
from zhipuai import ZhipuAI
from groq import Groq
from datetime import datetime

# 1. SETUP E MODELOS ATUALIZADOS (2026)
st.set_page_config(page_title="BHyDra IA", page_icon="🐍", layout="wide")
GROQ_MODEL = "llama-3.3-70b-versatile"
ZHIPU_MODEL = "glm-4-flash"
DATA_HOJE = datetime.now().strftime("%d/%m/%Y")

# 2. CONEXÕES
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client_glm = ZhipuAI(api_key=st.secrets["GLM_KEY"])
client_groq = Groq(api_key=st.secrets["GROQ_KEY"])

# 3. PERSONALIDADE E CONTEXTO TEMPORAL
SYSTEM_PROMPT = f"""Você é a BHyDra IA. Hoje é {DATA_HOJE}. 
- Responda de forma direta e técnica.
- Se for uma saudação, seja breve.
- Você tem acesso à internet para validar dados de 2026 via ZhipuAI."""

# --- SIDEBAR (HISTÓRICO E CONTROLES) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/BrunoAlexandreXX/bhydra-project/main/bhydra_logo.jpeg", width=80)
    st.title("Menu BHyDra")
    
    if st.button("➕ Nova Conversa", type="primary", use_container_width=True):
        if "chat_id" in st.session_state: del st.session_state.chat_id
        st.rerun()

    st.divider()
    
    # OPÇÃO DE ANEXAR (Ativa)
    arquivo_anexado = st.file_uploader("📂 Anexar Documento", type=['pdf', 'txt', 'csv'])
    
    st.divider()
    st.subheader("Conversas Recentes")
    
    # Carrega chats do Supabase
    chats = supabase.table("chats").select("*").order("created_at", desc=True).limit(10).execute().data
    
    for c in chats:
        col_btn, col_del = st.columns([0.85, 0.15])
        with col_btn:
            if st.button(f"💬 {c['title']}", key=f"chat_{c['id']}", use_container_width=True):
                st.session_state.chat_id = c['id']
                st.rerun()
        with col_del:
            if st.button("×", key=f"del_{c['id']}", help="Apagar esta conversa"):
                supabase.table("chat_history").delete().eq("chat_id", c['id']).execute()
                supabase.table("chats").delete().eq("id", c['id']).execute()
                if st.session_state.get("chat_id") == c['id']:
                    del st.session_state.chat_id
                st.rerun()

    # --- BOTÃO DISCRETO PARA APAGAR TUDO (CORREÇÃO UUID) ---
    st.write("<br>" * 10, unsafe_allow_html=True) 
    st.divider()
    
    if st.button("Limpar todo o histórico", help="Atenção: Isso apagará TODAS as conversas permanentemente", use_container_width=True):
        try:
            # Filtro UUID nulo compatível com PostgreSQL para deletar todos os registros
            null_uuid = "00000000-0000-0000-0000-000000000000"
            
            # Deleta mensagens e depois os chats
            supabase.table("chat_history").delete().neq("id", null_uuid).execute()
            supabase.table("chats").delete().neq("id", null_uuid).execute()
            
            if "chat_id" in st.session_state: del st.session_state.chat_id
            st.success("Histórico limpo!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao limpar: {str(e)}")

# --- ÁREA PRINCIPAL DO CHAT ---
historico_db = []

if "chat_id" in st.session_state:
    info_atual = supabase.table("chats").select("title").eq("id", st.session_state.chat_id).execute().data
    st.header(f"🐍 {info_atual[0]['title'] if info_atual else 'BHyDra'}")
    
    historico_db = supabase.table("chat_history").select("*").eq("chat_id", st.session_state.chat_id).order("created_at").execute().data
    for msg in historico_db:
        with st.chat_message(msg['role'], avatar="🐍" if msg['role'] == "assistant" else "👤"):
            st.markdown(msg['content'])

# --- ENTRADA E RESPOSTA ---
if prompt := st.chat_input("Dê um comando para a BHyDra..."):
    
    # 1. GERAÇÃO AUTOMÁTICA DE TEMA (Tema Instantâneo)
    if "chat_id" not in st.session_state:
        try:
            res_tema = client_groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}]
            ).choices[0].message.content.replace('"', '')[:20]
        except:
            res_tema = prompt[:15]
        
        novo_chat = supabase.table("chats").insert({"title": res_tema, "user_id": "bruno_ceo"}).execute()
        st.session_state.chat_id = novo_chat.data[0]['id']

    # 2. SALVAR COMANDO DO USUÁRIO
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    supabase.table("chat_history").insert({"chat_id": st.session_state.chat_id, "role": "user", "content": prompt}).execute()

    # 3. RESPOSTA DUAL-CORE COM ANEXO
    with st.chat_message("assistant", avatar="🐍"):
        with st.spinner("BHyDra processando..."):
            txt_contexto = ""
            if arquivo_anexado:
                txt_contexto = f"\n\n[DADOS DO ARQUIVO]: {arquivo_anexado.read().decode('utf-8', errors='ignore')}"

            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in historico_db[-3:]: msgs.append({"role": m['role'], "content": m['content']})
            msgs.append({"role": "user", "content": prompt + txt_contexto})

            try:
                # Decide se usa Groq (Geral) ou ZhipuAI (Internet/2026)
                if any(k in prompt.lower() for k in ["hoje", "notícia", "fii", "2026", "agora"]):
                    search_res = client_glm.chat.completions.create(
                        model=ZHIPU_MODEL,
                        messages=msgs,
                        tools=[{"type": "web_search", "web_search": {"search_query": f"{prompt} em 2026"}}]
                    )
                    res_final = search_res.choices[0].message.content
                else:
                    res_final = client_groq.chat.completions.create(model=GROQ_MODEL, messages=msgs).choices[0].message.content
            except:
                res_final = client_glm.chat.completions.create(model=ZHIPU_MODEL, messages=msgs).choices[0].message.content

            st.markdown(res_final)

    # 4. SALVAR RESPOSTA DA IA
    supabase.table("chat_history").insert({"chat_id": st.session_state.chat_id, "role": "assistant", "content": res_final}).execute()