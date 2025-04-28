
import streamlit as st
import pdfplumber
import re

# Função para extrair resultados
def extrair_resultados(texto):
    padrao = r"(\b[A-Za-zÀ-ÖØ-öø-ÿ0-9/().% +-]+\b)\s*([<>]?-?\d+[,.]?\d*)"
    matches = re.findall(padrao, texto)
    resultados = []
    for match in matches:
        exame = match[0].strip()
        valor = match[1].strip()
        if valor != "":
            resultados.append(f"{exame} {valor}")
    return " | ".join(resultados)

# Função para extrair a data de coleta
def extrair_data(texto):
    datas = re.findall(r"(\d{2}/\d{2}/\d{4})", texto)
    for data in datas:
        if not re.search(r"nascimento", texto.lower()):
            return data
    return ""

# Layout da página
st.set_page_config(page_title="Transcritor de exames", page_icon=":memo:", layout="centered")
st.markdown(
    '''
    <style>
        body {
            background: linear-gradient(to bottom, #E6E6FA, #FFFFFF);
        }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("Transcritor de exames")

st.header("Informações do Exame")

uploaded_file = st.file_uploader("Escolha o arquivo PDF do exame", type="pdf")

nome_laboratorio = st.text_input("Nome do laboratório:")
data_coleta = st.text_input("Data da coleta (dd/mm/aaaa):")

resumo = ""

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        texto_pdf = ""
        for page in pdf.pages:
            texto_pdf += page.extract_text() + "\n"

    if not data_coleta:
        data_coleta = extrair_data(texto_pdf)

    resultados = extrair_resultados(texto_pdf)

    if resultados:
        resumo = f"{nome_laboratorio.upper()}, {data_coleta}: {resultados}"

st.header("Linha pronta para o prontuário:")
st.text_area("Resumo:", value=resumo, height=300)

if resumo:
    st.button("Copiar Resumo", on_click=lambda: st.session_state.update({"resumo_copiado": True}))
