
import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="Transcritor de Exames", layout="centered")

# Fundo lavanda degradê
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #E6E6FA 0%, #FFFFFF 100%);
    }
    .title {
        font-size: 42px;
        color: #6A5ACD;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 20px;
        color: #7A7A7A;
        text-align: center;
        margin-bottom: 30px;
    }
    .copy-button {
        background-color: #C3B1E1;
        color: black;
        padding: 12px 24px;
        border-radius: 10px;
        font-size: 18px;
        border: none;
        cursor: pointer;
        margin-top: 10px;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">Transcritor de Exames</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transforme rapidamente PDFs de exames em resumos prontos para o prontuário</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Escolha o arquivo PDF do exame", type=["pdf"])

def extrair_texto(file):
    with pdfplumber.open(file) as pdf:
        texto = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + "\n"
        return texto

def extrair_exames_puros(texto):
    exames = []
    linhas = texto.split("\n")
    for linha in linhas:
        linha = linha.strip()
        # Buscar apenas linhas com "nome exame + número"
        match = re.match(r"([A-Za-zÀ-ÿ\-\s/]+)\s+([-<]?[0-9]+[.,]?[0-9]*)", linha)
        if match:
            nome = match.group(1).strip()
            valor = match.group(2).replace(",", ".")
            if len(nome.split()) <= 7:  # nome curto, tipo "Hemoglobina", "Glicose", "Colesterol LDL"
                exames.append(f"{nome} {valor}")
    return exames

def encontrar_lab(texto):
    match = re.search(r"(Alta Diagnósticos|Fleury|Dasa|Sabin|Einstein|Laboratório [\w\s]+)", texto, re.IGNORECASE)
    return match.group(0).strip() if match else ""

def encontrar_data_coleta(texto):
    for linha in texto.split("\n"):
        if "coleta" in linha.lower() or "recebimento" in linha.lower():
            match = re.search(r"(\d{2}/\d{2}/\d{4})", linha)
            if match:
                return match.group(0)
    return ""

if uploaded_file:
    texto_extraido = extrair_texto(uploaded_file)
    exames_encontrados = extrair_exames_puros(texto_extraido)
    lab = encontrar_lab(texto_extraido)
    data_coleta = encontrar_data_coleta(texto_extraido)

    st.success("Exames extraídos com sucesso! Confira abaixo:")

    st.subheader("Informações do Exame")
    col1, col2 = st.columns(2)
    with col1:
        lab = st.text_input("Nome do laboratório:", value=lab if lab else "")
    with col2:
        data_coleta = st.text_input("Data da coleta:", value=data_coleta if data_coleta else "")

    if exames_encontrados:
        resumo = f"{lab}, {data_coleta}: " + " ".join(exames_encontrados)
        st.subheader("Linha pronta para o prontuário:")
        resumo_area = st.text_area("Resumo:", value=resumo, height=300)

        st.markdown(f"""
            <button class="copy-button" onclick="navigator.clipboard.writeText(`{resumo}`)">
            Copiar Resumo
            </button>
            """, unsafe_allow_html=True)
