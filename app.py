
import streamlit as st
import pdfplumber
import re
import pyperclip
from io import BytesIO

# Dicionário de abreviações
ABREVIACOES = {
    "Hemoglobina": "Hb",
    "Hematócrito": "Ht",
    "Leucócitos": "Leuco",
    "Plaquetas": "Plaq",
    "Creatinina": "Cr",
    "Ureia": "U",
    "Glicose": "Gj",
    "Hemoglobina glicada": "HbA1c",
    "Colesterol total": "CT",
    "HDL colesterol": "HDL",
    "LDL colesterol": "LDL",
    "VLDL": "VLDL",
    "Triglicerídeos": "Tg",
    "Sódio": "Na",
    "Potássio": "K",
    "Cálcio": "Ca",
    "Magnésio": "Mg",
    "Bilirrubina total": "BT",
    "Bilirrubina direta": "BD",
    "Bilirrubina indireta": "BI",
    "Fosfatase alcalina": "FAL",
    "Gama GT": "GGT",
    "Vitamina D": "Vit D",
    "Vitamina B12": "Vit B12",
    "PCR": "PCR",
    "Ferritina": "Ferritina",
    "Saturação transferrina": "Sat Transferrina",
}

def extrair_texto_pdf(uploaded_file):
    texto = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"
    return texto

def gerar_resumo(texto, laboratorio_manual, data_manual):
    linhas = texto.splitlines()
    exames = []

    for linha in linhas:
        for exame_nome, abreviacao in ABREVIACOES.items():
            if exame_nome.lower() in linha.lower():
                numeros = re.findall(r"[-+]?\d*\.\d+|\d+", linha)
                if numeros:
                    valor = numeros[0]
                    exames.append(f"{abreviacao} {valor}")

    blocos = []
    ordem_blocos = [
        ["Hb", "Ht", "Leuco", "Plaq"],
        ["Cr"],
        ["U"],
        ["TGO", "TGP", "FAL", "GGT"],
        ["BT", "BD", "BI"],
        ["Vit D"],
        ["Vit B12"],
        ["TSH", "T4l"],
        ["Gj", "HbA1c"],
        ["CT", "HDL", "VLDL", "LDL", "não-HDL", "Tg"],
        ["Ferritina", "Sat Transferrina"],
        ["PCR"],
        ["Na", "K", "Ca", "Mg"],
    ]

    for grupo in ordem_blocos:
        bloco = " ".join(exame for exame in exames if exame.split()[0] in grupo)
        if bloco:
            blocos.append(bloco)

    resumo_final = " | ".join(blocos)
    resumo_formatado = f"{laboratorio_manual}, {data_manual}: {resumo_final}"
    return resumo_formatado

# Streamlit App
st.set_page_config(page_title="Transcritor de Exames")

st.title("Transcritor de exames")

uploaded_file = st.file_uploader("Faça upload do PDF com exames", type=["pdf"])

if uploaded_file:
    texto_extraido = extrair_texto_pdf(uploaded_file)

    st.subheader("Preencha os dados do cabeçalho:")
    laboratorio_manual = st.text_input("Nome do Laboratório")
    data_manual = st.text_input("Data da Coleta (dd/mm/aaaa)")

    if laboratorio_manual and data_manual:
        resumo = gerar_resumo(texto_extraido, laboratorio_manual, data_manual)

        st.subheader("Resumo Gerado")
        st.text_area("Resumo:", resumo, height=200)

        if st.button("Copiar Resumo"):
            pyperclip.copy(resumo)
            st.success("Resumo copiado para a área de transferência!")
    else:
        st.warning("Preencha o Nome do Laboratório e a Data de Coleta para gerar o resumo.")
