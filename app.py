
import streamlit as st
import re
import pdfplumber

st.set_page_config(page_title="Resumo de Exames - Luana", layout="wide")

st.title("Resumo Automático de Exames Laboratoriais")
st.write("Faça o upload de um PDF de exames laboratoriais e gere o resumo em uma linha para prontuário.")

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
        st.subheader("Linha para prontuário:")
        st.code(linha, language="markdown")
    if alterados:
        st.subheader("Observações:")
        for a in alterados:
            st.markdown(f"- **{a}**")
