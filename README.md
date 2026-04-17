# 🐍 BHyDra IA

A **BHyDra IA** é uma assistente virtual inteligente desenvolvida em Python, utilizando a infraestrutura da **Groq Cloud** e o modelo de linguagem **Llama 3.1**. O projeto foi criado para explorar a integração de APIs de IA generativa com interfaces web modernas e seguras.

🚀 **Acesse o projeto online:** https://bhydra.streamlit.app/

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface:** [Streamlit](https://streamlit.io/) (Framework para apps de dados)
* **Cérebro da IA:** [Groq Cloud](https://groq.com/) (Modelo Llama 3.1 8B)
* **Segurança:** Variáveis de ambiente via Streamlit Secrets
* **Versionamento:** Git & GitHub

---

## 📌 Funcionalidades

* 💬 Chat em tempo real com memória de contexto na sessão.
* ⚡ Respostas ultra-rápidas utilizando a tecnologia de inferência da Groq.
* 📱 Interface responsiva (funciona em PC e Celular).
* 🔒 Arquitetura segura (chaves de API protegidas).

---

## 🚀 Como rodar o projeto localmente

Se você é desenvolvedor e quer testar na sua máquina, siga os passos:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/BrunoAlexandreXX/bhydra-project.git](https://github.com/BrunoAlexandreXX/bhydra-project.git)
   cd bhydra-project
Crie um ambiente virtual e instale as dependências:

Bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
Configure sua chave:
Crie uma pasta .streamlit/ e dentro dela um arquivo secrets.toml com sua chave:

Ini, TOML
GROQ_API_KEY = "sua_chave_aqui"
Inicie o App:

Bash
streamlit run app.py
🧪 Foco em QA (Qualidade)
Como entusiasta da área de Quality Assurance, este projeto foi desenvolvido seguindo boas práticas de:

Segurança: Prevenção de exposição de credenciais (Secret Scanning).

Clean Code: Estrutura de código legível e modular.

User Experience: Interface intuitiva e feedback de erro amigável.

👤 Autor
Bruno Alexandre

Estudante de Engenharia de Software

Atuando como Suporte Técnico 

Focado em transição de carreira para QA Junior/ Dev.