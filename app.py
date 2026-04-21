import streamlit as st
from supabase import create_client
from zhipuai import ZhipuAI
from groq import Groq
from datetime import datetime
import PyPDF2
import io
import urllib.parse
import requests

# ─────────────────────────────────────────────
# 1. CONFIGURAÇÃO E DESIGN (CSS)
# ─────────────────────────────────────────────
st.set_page_config(page_title="BHyDra IA", page_icon="🐍", layout="wide")

# CSS para visual Futurista e Limpo
st.markdown("""
<style>
    /* Fundo escuro e texto claro */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar escura */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #262730;
    }

    /* Inputs e Selectboxes */
    .stTextInput > div > div > input, .stChatInput textarea {
        background-color: #1A1C24;
        color: #FAFAFA;
        border: 1px solid #262730;
        border-radius: 10px;
    }

    /* Botões principais */
    .stButton > button[kind="primary"] {
        background-color: #00C3FF;
        color: #0E1117;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #00A3CC;
        color: white;
    }

    /* Botões secundários */
    .stButton > button:not([kind="primary"]) {
        background-color: #1A1C24;
        color: #FAFAFA;
        border: 1px solid #262730;
        border-radius: 10px;
    }
    .stButton > button:not([kind="primary"]):hover {
        border: 1px solid #00C3FF;
        color: #00C3FF;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #00C3FF;
    }

    /* Mensagens do Chat */
    .stChatMessage {
        background-color: #1A1C24;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid #262730;
    }
    
    /* Remover bordas padrão do streamlit */
    .stDivider {
        background-color: #262730;
    }
    
    /* Logo arredondada e sombreada */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .logo-img {
        border-radius: 50%; 
        box-shadow: 0 4px 15px rgba(0, 195, 255, 0.3);
        width: 90px;
        height: 90px;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

GROQ_MODEL    = "llama-3.3-70b-versatile"
ZHIPU_MODEL   = "glm-4-flash"
DATA_HOJE     = datetime.now().strftime("%d/%m/%Y")
MAX_HISTORICO = 8

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&nologo=true&enhance=true"

# ─────────────────────────────────────────────
# 2. CONEXÕES
# ─────────────────────────────────────────────
@st.cache_resource
def init_connections():
    supabase    = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client_glm  = ZhipuAI(api_key=st.secrets["GLM_KEY"])
    client_groq = Groq(api_key=st.secrets["GROQ_KEY"])
    return supabase, client_glm, client_groq

try:
    supabase, client_glm, client_groq = init_connections()
except Exception as e:
    st.error(f"Erro ao conectar servicos: {e}")
    st.stop()

# ─────────────────────────────────────────────
# 3. AUTENTICAÇÃO
# ─────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None

if "supabase_session" not in st.session_state:
    st.session_state.supabase_session = None

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False

def restore_session():
    if st.session_state.supabase_session:
        try:
            supabase.auth.set_session(
                st.session_state.supabase_session.access_token,
                st.session_state.supabase_session.refresh_token
            )
            st.session_state.user = supabase.auth.get_user().user
        except Exception:
            st.session_state.user = None
            st.session_state.supabase_session = None

restore_session()

if not st.session_state.user:
    # Tela de Login/Cadastro com estilo centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.signup_success:
            st.title("📧 Confirme seu E-mail")
            st.success("✅ Cadastro realizado!")
            st.info("Enviamos um link de confirmação para o seu e-mail.")
            st.warning("⚠️ Verifique sua caixa de entrada (e spam).")
            if st.button("Já confirmei, voltar para o Login", type="primary", use_container_width=True):
                st.session_state.signup_success = False
                st.rerun()
        else:
            st.title("🔒 BHyDra IA")
            st.write("Acesse sua conta para continuar")
            
            tab_login, tab_signup = st.tabs(["Entrar", "Criar Conta"])
            
            with tab_login:
                with st.form("login_form"):
                    email = st.text_input("Email")
                    senha = st.text_input("Senha", type="password")
                    submit = st.form_submit_button("Entrar", type="primary", use_container_width=True)
                    
                    if submit:
                        try:
                            res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                            st.session_state.user = res.user
                            st.session_state.supabase_session = res.session
                            st.rerun()
                        except Exception as e:
                            st.error(f"Credenciais inválidas ou e-mail não confirmado.")

            with tab_signup:
                with st.form("signup_form"):
                    novo_email = st.text_input("Novo Email")
                    nova_senha = st.text_input("Criar Senha", type="password")
                    submit_cad = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)
                    
                    if submit_cad:
                        try:
                            res = supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                            st.session_state.signup_success = True
                            st.session_state.email_registered = novo_email
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao criar conta: {e}")

    st.stop()

# --- USUÁRIO LOGADO ---
user_id_real = st.session_state.user.id
user_email = st.session_state.user.email
# Pega o nome salvo nos metadados do usuário (ou vazio se não tiver)
user_display_name = st.session_state.user.user_metadata.get("display_name", "")

# ─────────────────────────────────────────────
# 4. CONFIGURAÇÃO DE NOME (Primeiro Acesso)
# ─────────────────────────────────────────────
if not user_display_name:
    st.sidebar.markdown("<div class='logo-container'><img src='https://raw.githubusercontent.com/BrunoAlexandreXX/bhydra-project/main/bhydra_logo.jpeg' class='logo-img'></div>", unsafe_allow_html=True)
    st.title("👋 Olá!")
    st.write("Parece que é sua primeira vez aqui. Como você gostaria de ser chamado?")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        novo_nome = st.text_input("Seu nome ou apelido", placeholder="Ex: Bruno, Chefe, Mestre...")
    with col2:
        st.write("") # Espaço vazio para alinhar
        st.write("")
        if st.button("Salvar", type="primary"):
            if novo_nome:
                # Atualiza o metadado do usuário no Supabase
                supabase.auth.update_user({"data": {"display_name": novo_nome}})
                # Atualiza localmente para usar imediatamente
                st.session_state.user.user_metadata['display_name'] = novo_nome
                st.rerun()
            else:
                st.warning("Por favor, insira um nome.")
    st.stop()

# Nome definido para o prompt
nome_usuario = user_display_name

# ─────────────────────────────────────────────
# 5. SYSTEM PROMPT (Personalizado)
# ─────────────────────────────────────────────
SYSTEM_PROMPT = f"""Voce e a BHyDra IA - uma assistente tecnica futurista e direta.
Hoje e {DATA_HOJE}.
O nome do usuario e {nome_usuario}.
- Sempre saude o usuario pelo nome ({nome_usuario}) no inicio da conversa ou quando apropriado.
- Responda de forma clara, objetiva e tecnica quando necessario.
- Para saudacoes, seja breve e amigavel.
- Voce pode acessar a internet para dados atualizados de 2026 via ZhipuAI.
- Quando receber conteudo de arquivo, analise-o com atencao antes de responder.
- Voce pode gerar imagens via comando /imagem descricao."""

# ─────────────────────────────────────────────
# 6. FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def ler_arquivo(arquivo):
    nome = arquivo.name.lower()
    try:
        if nome.endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(arquivo.read()))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            return arquivo.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[Erro ao ler arquivo: {e}]"

def montar_mensagens(historico, prompt, contexto_arquivo):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in historico[-MAX_HISTORICO:]:
        msgs.append({"role": m["role"], "content": m["content"]})
    conteudo_usuario = prompt
    if contexto_arquivo:
        conteudo_usuario += f"\n\n[CONTEUDO DO ARQUIVO ANEXADO]:\n{contexto_arquivo}"
    msgs.append({"role": "user", "content": conteudo_usuario})
    return msgs

def detectar_busca_web(prompt):
    palavras_chave = ["hoje", "noticia", "fii", "2026", "agora", "preco",
                      "cotacao", "ultima", "recente", "atual", "novo"]
    return any(k in prompt.lower() for k in palavras_chave)

def gerar_resposta(msgs, prompt):
    if detectar_busca_web(prompt):
        try:
            search_res = client_glm.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=msgs,
                tools=[{"type": "web_search", "web_search": {"search_query": f"{prompt} {DATA_HOJE}"}}]
            )
            return search_res.choices[0].message.content, "ZhipuAI"
        except Exception as e:
            pass # Tenta fallback silenciosamente

    try:
        res = client_groq.chat.completions.create(model=GROQ_MODEL, messages=msgs)
        return res.choices[0].message.content, "Groq"
    except Exception as e:
        try:
            res = client_glm.chat.completions.create(model=ZHIPU_MODEL, messages=msgs)
            return res.choices[0].message.content, "ZhipuAI"
        except Exception as e:
            return f"Nao foi possivel gerar resposta. Erro: {e}", "Erro"

def traduzir_prompt_imagem(descricao):
    try:
        instruction = "Translate to English and enrich for high-quality AI image generation. Return ONLY the prompt."
        prompt_completo = f"{instruction}\n\nDescription: {descricao}"
        res = client_groq.chat.completions.create(model=GROQ_MODEL, messages=[{"role": "user", "content": prompt_completo}])
        return res.choices[0].message.content.strip()
    except Exception:
        return descricao

def gerar_imagem(descricao):
    prompt_en = traduzir_prompt_imagem(descricao)
    prompt_encoded = urllib.parse.quote(prompt_en)
    url = POLLINATIONS_URL.format(prompt=prompt_encoded)
    try:
        resp = requests.head(url, timeout=20, allow_redirects=True)
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            return url, prompt_en
        else:
            return None, "Falha ao gerar imagem."
    except Exception:
        return None, "Timeout."

def detectar_comando_imagem(prompt):
    prompt_strip = prompt.strip()
    for cmd in ["/imagem ", "/img ", "/image "]:
        if prompt_strip.lower().startswith(cmd):
            return prompt_strip[len(cmd):].strip()
    return None

def salvar_mensagem(chat_id, role, content):
    try:
        supabase.table("chat_history").insert({"chat_id": chat_id, "role": role, "content": content}).execute()
    except Exception:
        pass

def criar_novo_chat(prompt):
    try:
        titulo = client_groq.chat.completions.create(
            model=GROQ_MODEL, messages=[{"role": "user", "content": f"Resuma em 2 palavras: {prompt}"}]
        ).choices[0].message.content.strip()[:20]
    except: titulo = prompt[:20]
    novo_chat = supabase.table("chats").insert({"title": titulo, "user_id": user_id_real}).execute()
    return novo_chat.data[0]["id"]

def apagar_chat(chat_id):
    try:
        supabase.table("chat_history").delete().eq("chat_id", chat_id).execute()
        supabase.table("chats").delete().eq("id", chat_id).execute()
    except: pass

# ─────────────────────────────────────────────
# 7. SIDEBAR (Design Limpo)
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo natural com CSS
    st.markdown("<div class='logo-container'><img src='https://raw.githubusercontent.com/BrunoAlexandreXX/bhydra-project/main/bhydra_logo.jpeg' class='logo-img'></div>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; margin-top: -10px;'>BHyDra IA</h3>", unsafe_allow_html=True)
    st.caption(f"Usuário: **{nome_usuario}**")
    
    if st.button("Sair", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.supabase_session = None
        st.rerun()

    st.write("") # Espaçamento

    if st.button("➕ Nova Conversa", type="primary", use_container_width=True):
        for key in ["chat_id", "arquivo_conteudo", "arquivo_nome"]:
            st.session_state.pop(key, None)
        st.rerun()

    arquivo_anexado = st.file_uploader("📎 Anexar Arquivo", type=["pdf", "txt", "csv"])
    if arquivo_anexado:
        if st.session_state.get("arquivo_nome") != arquivo_anexado.name:
            st.session_state["arquivo_conteudo"] = ler_arquivo(arquivo_anexado)
            st.session_state["arquivo_nome"] = arquivo_anexado.name
            st.toast(f"Arquivo '{arquivo_anexado.name}' carregado!")

    st.write("")
    
    st.markdown("**Histórico**")
    try:
        chats = supabase.table("chats").select("*").order("created_at", desc=True).limit(15).execute().data
    except: chats = []

    for c in chats:
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"💬 {c['title']}", key=f"chat_{c['id']}", use_container_width=True):
                st.session_state.chat_id = c["id"]
                st.rerun()
        with cols[1]:
            if st.button("🗑️", key=f"del_{c['id']}", help="Apagar"):
                apagar_chat(c["id"])
                if st.session_state.get("chat_id") == c["id"]:
                    st.session_state.pop("chat_id", None)
                st.rerun()

# ─────────────────────────────────────────────
# 8. AREA PRINCIPAL
# ─────────────────────────────────────────────
historico_db = []

if "chat_id" in st.session_state:
    try:
        info_chat = supabase.table("chats").select("title").eq("id", st.session_state.chat_id).execute().data
        titulo_chat = info_chat[0]["title"] if info_chat else "BHyDra"
    except: titulo_chat = "BHyDra"

    st.header(f"🐍 {titulo_chat}")

    try:
        historico_db = supabase.table("chat_history").select("*").eq("chat_id", st.session_state.chat_id).order("created_at").execute().data
    except: pass

    for msg in historico_db:
        avatar = "🐍" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
else:
    st.header("🐍 BHyDra IA")
    st.write(f"Bem-vindo de volta, **{nome_usuario}**! Como posso ajudar você hoje?")

# ─────────────────────────────────────────────
# 9. INPUT E RESPOSTA
# ─────────────────────────────────────────────
if prompt := st.chat_input(f"Envie uma mensagem para BHyDra..."):

    if "chat_id" not in st.session_state:
        try:
            st.session_state.chat_id = criar_novo_chat(prompt)
        except Exception as e:
            st.error(f"Erro ao criar conversa: {e}")
            st.stop()

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    salvar_mensagem(st.session_state.chat_id, "user", prompt)

    descricao_imagem = detectar_comando_imagem(prompt)

    if descricao_imagem:
        with st.chat_message("assistant", avatar="🐍"):
            with st.spinner("🎨 Gerando imagem..."):
                url_imagem, prompt_usado = gerar_imagem(descricao_imagem)

            if url_imagem:
                st.image(url_imagem, caption=f"🎨 {descricao_imagem}", use_container_width=True)
                conteudo_salvo = f"🎨 **Imagem:** {descricao_imagem}\n![img]({url_imagem})"
            else:
                st.error("Falha ao gerar imagem.")
                conteudo_salvo = "Falha na geração."

        salvar_mensagem(st.session_state.chat_id, "assistant", conteudo_salvo)

    else:
        contexto_arquivo = st.session_state.get("arquivo_conteudo", "")
        msgs = montar_mensagens(historico_db, prompt, contexto_arquivo)

        with st.chat_message("assistant", avatar="🐍"):
            with st.spinner("Pensando..."):
                res_final, modelo_usado = gerar_resposta(msgs, prompt)
            st.markdown(res_final)
            st.caption(f"Modelo: {modelo_usado}")

        salvar_mensagem(st.session_state.chat_id, "assistant", res_final)