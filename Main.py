import streamlit as st
import google.generativeai as genai
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ElevateProfile IA", page_icon="🚀", layout="wide")

# Estilização para o Chat
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px;  background-color: #000000;}
    [data-testid="stSidebar"] { background-color: #000000; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DE SEGURANÇA (API KEY) ---
try:
    # No Streamlit Cloud, adicione GEMINI_API_KEY em Advanced Settings > Secrets
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Chave de API não encontrada nos Secrets do Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"Erro ao configurar IA: {e}")
    st.stop()

# --- SIDEBAR (Entrada de Dados e Contexto) ---
with st.sidebar:
    st.title("⚙️ Configurações")
    st.markdown("Forneça o contexto para a IA analisar seu perfil de forma precisa.")
    
    linkedin_url = st.text_input("🔗 Link do LinkedIn", placeholder="https://linkedin.com/in/usuario")
    
    setor = st.selectbox(
        "💼 Área de Atuação",
        ["Tecnologia", "Marketing", "Finanças", "Design", "Engenharia", "Saúde", "Vendas", "Outros"]
    )
    
    objetivo = st.text_area(
        "🎯 Seu Objetivo", 
        placeholder="Ex: Transição de carreira para dados ou promoção para gerência..."
    )
    
    st.markdown("---")
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# --- INTERFACE DE CHAT ---
st.title("💬 Consultor de Carreira IA")
st.caption("Sugestões personalizadas para alavancar seu perfil profissional.")

# Inicialização do histórico
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Preencha seus dados na barra lateral e me pergunte qualquer coisa sobre como melhorar seu perfil ou carreira."}
    ]

# Exibição das mensagens existentes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FUNÇÃO DE ABSTRAÇÃO DA IA ---
def processar_resposta_ia(prompt_usuario):
    """
    Abstrai o prompt mestre injetando os dados da sidebar 
    sem que o usuário final veja a complexidade da instrução.
    """
    contexto_mestre = f"""
    Você é um consultor sênior de Personal Branding e Recrutamento.
    CONTEXTO DO USUÁRIO:
    - LinkedIn: {linkedin_url if linkedin_url else "Não informado"}
    - Setor: {setor}
    - Objetivo Atual: {objetivo if objetivo else "Evolução profissional geral"}

    INSTRUÇÕES:
    1. Analise o objetivo e o setor para dar dicas de SEO de LinkedIn (palavras-chave).
    2. Sugira pelo menos 1 livro relevante para o objetivo de '{objetivo}'.
    3. Se o link do LinkedIn for fornecido, oriente como destacar experiências nele.
    4. Responda em Português (Brasil) com tom profissional e encorajador.
    5. Formate a saída com Markdown (negritos, listas e títulos).

    PERGUNTA DO USUÁRIO: {prompt_usuario}
    """
    
    response = model.generate_content(contexto_mestre)
    return response.text

# --- ENTRADA DO USUÁRIO NO CHAT ---
if user_input := st.chat_input("Diga algo como: 'Como melhorar meu resumo?'"):
    
    # 1. Adiciona pergunta do usuário ao chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Resposta da IA
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Consultando especialistas em carreira..."):
            try:
                full_response = processar_resposta_ia(user_input)
                
                # Efeito de digitação (UX)
                displayed_text = ""
                for char in full_response:
                    displayed_text += char
                    message_placeholder.markdown(displayed_text + "▌")
                    time.sleep(0.003)
                message_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error("Erro ao gerar resposta. Verifique sua conexão e chave de API.")