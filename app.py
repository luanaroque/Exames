
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

# Função para extrair texto do PDF
def extrair_texto_pdf(uploaded_file):
    texto = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() + "\n"
    return texto

# Função para processar texto e gerar resumo
def gerar_resumo(texto):
    linhas = texto.splitlines()
    exames = []
    laboratorio = ""
    data_coleta = ""

    # Tentativas de identificar laboratório e data
    for linha in linhas:
        if "Laboratório" in linha or "Laboratorio" in linha:
            laboratorio = linha.strip()
        if re.search(r"\d{2}/\d{2}/\d{4}", linha):
            data_coleta = re.search(r"\d{2}/\d{2}/\d{4}", linha).group(0)

    # Processar cada linha para capturar exames
    for linha in linhas:
        for exame_nome, abreviacao in ABREVIACOES.items():
            if exame_nome.lower() in linha.lower():
                numeros = re.findall(r"[-+]?\d*\.\d+|\d+", linha)
                if numeros:
                    valor = numeros[0]
                    exames.append(f"{abreviacao} {valor}")

    # Agrupar em blocos separados por |
    blocos = []
    bloco_atual = []

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

    laboratorio_final = laboratorio if laboratorio else st.text_input("Digite o nome do Laboratório")
    data_final = data_coleta if data_coleta else st.text_input("Digite a data de coleta (dd/mm/aaaa)")

    resumo_formatado = f"{laboratorio_final}, {data_final}: {resumo_final}"

    return resumo_formatado

# Layout Streamlit
st.set_page_config(page_title="Transcritor de Exames")

st.title("Transcritor de exames")

uploaded_file = st.file_uploader("Faça upload do PDF com exames", type=["pdf"])

if uploaded_file:
    texto_extraido = extrair_texto_pdf(uploaded_file)
    resumo = gerar_resumo(texto_extraido)

    st.subheader("Resumo Gerado")
    st.text_area("Resumo:", resumo, height=200)

    if st.button("Copiar Resumo"):
        pyperclip.copy(resumo)
        st.success("Resumo copiado para a área de transferência!")
