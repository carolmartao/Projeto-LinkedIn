import streamlit as st
import google.generativeai as genai
import time
from pypdf import PdfReader

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ElevateProfile IA", page_icon="🚀", layout="wide")

# --- CONFIGURAÇÃO DE SEGURANÇA ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Configure 'GEMINI_API_KEY' nos Secrets do Streamlit Cloud.")
        st.stop()
except Exception as e:
    st.error(f"Erro na API: {e}")
    st.stop()

# --- FUNÇÃO PARA EXTRAIR TEXTO DO PDF ---
def extrair_texto_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text()
        return texto_completo
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

# --- LÓGICA DA IA ---
def chamar_ia(pergunta_usuario, setor, objetivo):
    texto_perfil = st.session_state.get('perfil_texto', "Nenhum perfil enviado.")
    
    prompt_mestre = f"""
    Você é um consultor de carreira sênior.
    CONTEXTO DO PERFIL:
    {texto_perfil}
    
    CONTEXTO ADICIONAL:
    - Setor: {setor}
    - Objetivo: {objetivo}

    INSTRUÇÕES:
    1. Responda à pergunta: "{pergunta_usuario}"
    2. Identifique pontos de melhoria em SEO e clareza no perfil.
    3. Sugira 2 livros úteis para quem deseja atuar em {setor} com o objetivo de {objetivo}.
    4. Use Markdown e Português do Brasil.
    """
    
    response = model.generate_content(prompt_mestre)
    return response.text

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    
    st.subheader("📄 Seu Perfil LinkedIn")
    pdf_upload = st.file_uploader("Suba o PDF do seu perfil", type="pdf")
    
    if pdf_upload is not None:
        if 'perfil_texto' not in st.session_state:
            with st.spinner("Extraindo dados..."):
                st.session_state['perfil_texto'] = extrair_texto_pdf(pdf_upload)
                st.success("Perfil carregado!")
    
    st.markdown("---")
    setor_selecionado = st.selectbox("💼 Setor", ["Tecnologia", "Marketing", "Gestão", "Vendas", "Saúde", "Outros"])
    objetivo_texto = st.text_area("🎯 Seu Objetivo", placeholder="Ex: Transição para análise de dados")

    # BOTÃO DE ANALISAR
    # O botão só funciona se houver PDF e Objetivo preenchido
    botao_analisar = st.button("🚀 Iniciar Análise Completa", disabled=not (pdf_upload and objetivo_texto))
    
    if st.button("🗑️ Limpar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- INTERFACE DE CHAT ---
st.title("💬 Consultor de Carreira")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Complete os dados na lateral e clique em 'Iniciar Análise' para começarmos."}]

# Exibição do Histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GATILHO: ANÁLISE INICIAL PELO BOTÃO ---
if botao_analisar:
    pergunta_inicial = "Faça uma análise inicial detalhada do meu perfil com base no meu objetivo e setor."
    st.session_state.messages.append({"role": "user", "content": pergunta_inicial})
    
    with st.chat_message("user"):
        st.markdown(pergunta_inicial)

    with st.chat_message("assistant"):
        with st.spinner("Gerando diagnóstico inicial..."):
            resposta = chamar_ia(pergunta_inicial, setor_selecionado, objetivo_texto)
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})

# --- CAMPO DE CHAT (PERGUNTAS LIVRES) ---
if prompt := st.chat_input("Dúvida específica? Ex: Como descrever meu último cargo?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            resposta = chamar_ia(prompt, setor_selecionado, objetivo_texto)
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})