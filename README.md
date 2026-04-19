[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg.svg)](https://bhydra.streamlit.app)
# 🐍 BHyDra IA - Assistente Inteligente com Memória

O **BHyDra IA** é um assistente conversacional desenvolvido para facilitar a interação com modelos de linguagem avançados, contando com um sistema de persistência de dados para que você nunca perca o contexto das suas conversas.

## 🚀 Funcionalidades
- **Histórico Persistente:** Conversas salvas automaticamente via Supabase.
- **Gestão de Chats (CRUD):** Criação, listagem e deleção de chats diretamente pela interface.
- **Análise de Documentos:** Suporte para upload de arquivos (PDF/TXT) para análise contextual.
- **Interface Neon:** UI moderna e responsiva otimizada para Desktop e Mobile.
- **Títulos Automáticos:** O sistema gera títulos inteligentes para suas conversas baseados no seu primeiro prompt.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** [Python](https://www.python.org/)
- **Framework Web:** [Streamlit](https://streamlit.io/)
- **Inteligência Artificial:** [Groq API](https://groq.com/) (Modelo Llama 3.1 8B)
- **Banco de Dados (Backend):** [Supabase](https://supabase.com/) (PostgreSQL)
- **Versionamento:** Git & GitHub

## 📂 Estrutura do Projeto
- `app.py`: Código principal da aplicação e interface.
- `requirements.txt`: Dependências do projeto.
- `.streamlit/`: Configurações de tema e segredos locais (não versionado por segurança).

## 👷 Como executar localmente
1. Clone o repositório:
   ```bash
   git clone [https://github.com/BrunoAlexandreXX/bhydra-project.git](https://github.com/BrunoAlexandreXX/bhydra-project.git)
Instale as dependências:

Bash
pip install -r requirements.txt
Configure seus secrets.toml na pasta .streamlit/ com as chaves da Groq e Supabase.

Execute o app:

Bash
streamlit run app.py
Desenvolvido por Bruno Alexandre A. Ribeiro como parte do portfólio de Engenharia de Software e QA.

