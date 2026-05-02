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

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    
    # Campo de Upload do PDF
    st.subheader("📄 Seu Perfil LinkedIn")
    pdf_upload = st.file_uploader("Suba o PDF do seu perfil (Clique em Perfil > Botão 'Recursos' > 'Salvar como PDF' no LinkedIn)", type="pdf")
    
    # Armazena o texto do PDF no estado da sessão se houver upload
    if pdf_upload is not None:
        with st.spinner("Extraindo dados do currículo..."):
            st.session_state['perfil_texto'] = extrair_texto_pdf(pdf_upload)
            st.success("Perfil carregado!")
    
    st.markdown("---")
    setor = st.selectbox("💼 Setor", ["Tecnologia", "Marketing", "Gestão", "Vendas", "Saúde", "Outros"])
    objetivo = st.text_area("🎯 Seu Objetivo", placeholder="Ex: Transição para análise de dados")

# --- INTERFACE DE CHAT ---
st.title("💬 Consultor de Carreira")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Suba o PDF do seu perfil na barra lateral para começarmos a análise personalizada."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DA IA ---
def chamar_ia(pergunta_usuario):
    # Recupera o texto extraído do PDF
    texto_perfil = st.session_state.get('perfil_texto', "Nenhum perfil em PDF foi enviado.")
    
    prompt_mestre = f"""
    Você é um consultor de carreira sênior.
    CONTEXTO DO PERFIL (Extraído de PDF):
    {texto_perfil}
    
    CONTEXTO ADICIONAL:
    - Setor: {setor}
    - Objetivo: {objetivo}

    PERGUNTA DO USUÁRIO: "{pergunta_usuario}"

    INSTRUÇÕES:
    1. Baseie suas sugestões estritamente no conteúdo do PDF fornecido acima.
    2. Identifique pontos fracos no resumo ou experiências e sugira melhorias com foco em SEO para recrutadores.
    3. Recomende livros específicos para o objetivo '{objetivo}'.
    4. Responda em Português com Markdown.
    """
    
    response = model.generate_content(prompt_mestre)
    return response.text

# --- CAMPO DE CHAT ---
if user_input := st.chat_input("Ex: Analise minhas experiências e sugira 3 mudanças."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analisando seu PDF..."):
            try:
                full_response = chamar_ia(user_input)
                displayed_text = ""
                for char in full_response:
                    displayed_text += char
                    message_placeholder.markdown(displayed_text + "▌")
                    time.sleep(0.002)
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Erro: {e}")