
import streamlit as st
import re
import pdfplumber

st.set_page_config(page_title="Resumo de Exames - Luana", layout="centered")

# Estilização geral
st.markdown(
    """
    <style>
    .title {
        font-size: 42px;
        color: #6EB5FF;
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
    .block {
        background-color: #FFFFFF;
        padding: 20px;
        border: 1px solid #DDDDDD;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Títulos
st.markdown('<div class="title">Resumo de Exames Laboratoriais</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transforme rapidamente PDFs de exames em resumos prontos para o prontuário</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Escolha o arquivo PDF do exame", type="pdf")

exames_padrao = [
    "Hb", "Ht", "Leuco", "Plaq", "Cr", "U", "TGO", "TGP", "FAL", "GGT",
    "BT", "BD", "BI", "Vit D", "Vit B12", "TSH", "T4l", "Gj", "HbA1c",
    "CT", "HDL", "VLDL", "LDL", "não-HDL", "Tg", "Ferritina", "Sat Transferrina",
    "PCR", "Na", "K", "Ca", "Mg", "Estradiol", "Testosterona Total", "Anti-Tg", "Anti-TPO", "eGFR"
]

def extrair_texto(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extrair_exames(texto):
    exames = {}
    alterados = []
    for exame in exames_padrao:
        pattern = re.compile(rf"{exame}[\s:]*([-<]?[0-9]+[.,]?[0-9]*)", re.IGNORECASE)
        match = pattern.search(texto)
        if match:
            valor = match.group(1).replace(",", ".")
            exames[exame] = valor
            if exame == "U" and float(valor) < 19:
                alterados.append(f"{exame} {valor} (baixo)")
            elif exame == "LDL" and float(valor) > 100:
                alterados.append(f"{exame} {valor} (elevado)")
            elif exame == "Anti-TPO" and float(valor) > 60:
                alterados.append(f"{exame} {valor} (elevado)")
    return exames, alterados

def formatar_linha(exames_dict, lab="LABORATÓRIO", data="DATA"):
    componentes = [f"{ex} {valor}" for ex, valor in exames_dict.items()]
    return f"{lab}, {data}: " + " ".join(componentes)

if uploaded_file:
    texto = extrair_texto(uploaded_file)
    exames_dict, alterados = extrair_exames(texto)
    if exames_dict:
        linha = formatar_linha(exames_dict, lab="LAB", data="05/04/2025")
        st.markdown('<div class="block">', unsafe_allow_html=True)
        st.subheader("Linha pronta para o prontuário:")
        st.code(linha, language="markdown")
        st.markdown('</div>', unsafe_allow_html=True)
    if alterados:
        st.subheader("Observações (valores alterados):")
        for a in alterados:
            st.markdown(f"- **{a}**")
