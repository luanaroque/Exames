
import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="Transcritor de Exames", page_icon=":clipboard:", layout="centered")

# Fundo lavanda
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom, #E6E6FA, #FFFFFF);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Transcritor de Exames")

uploaded_file = st.file_uploader("Faça upload do PDF de exames", type="pdf")

# Dicionário de abreviações
abreviacoes = {
    "Hemoglobina": "Hb",
    "Hematócrito": "Ht",
    "Leucócitos": "Leuco",
    "Plaquetas": "Plaq",
    "Creatinina": "Cr",
    "Ureia": "U",
    "Glicose": "Gj",
    "Hemoglobina Glicada": "HbA1c",
    "Colesterol Total": "CT",
    "HDL": "HDL",
    "LDL": "LDL",
    "VLDL": "VLDL",
    "Triglicerídeos": "Tg",
    "Sódio": "Na",
    "Potássio": "K",
    "Cálcio": "Ca",
    "Magnésio": "Mg",
    "Bilirrubina Total": "BT",
    "Bilirrubina Direta": "BD",
    "Bilirrubina Indireta": "BI",
    "Fosfatase Alcalina": "FAL",
    "Gama Glutamil Transferase": "GGT",
    "Vitamina D": "Vit D",
    "Vitamina B12": "Vit B12",
    "PCR": "PCR",
    "Ferritina": "Ferritina",
    "Saturação Transferrina": "Sat Transferrina"
}

def aplicar_abreviacoes(nome_exame):
    for completo, abreviado in abreviacoes.items():
        if completo.lower() in nome_exame.lower():
            return abreviado
    return nome_exame  # se não encontrar, retorna como está

def extrair_dados(texto):
    linhas = texto.split("\n")
    resultados = []
    for linha in linhas:
        match = re.search(r"([A-Za-zçÇãõÕéÉêÊáÁíÍóÓúÚâÂôÔûÛ\/\-\s]+)\s+([-+]?[0-9]*\.?[0-9]+)", linha)
        if match:
            exame, valor = match.groups()
            exame = exame.strip()
            valor = valor.replace(",", ".")
            if not any(x in exame.lower() for x in ["crm", "tel", "telefone", "página", "cpf", "registro", "anvisa", "código", "nome", "idade", "sexo"]):
                exame = aplicar_abreviacoes(exame)
                resultados.append(f"{exame} {valor}")
    return resultados

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    resultados = extrair_dados(texto)

    laboratorio = st.text_input("Nome do laboratório:", value="")
    data_coleta = st.text_input("Data da coleta (DD/MM/AAAA):", value="")

    if resultados:
        resumo_final = f"{laboratorio}, {data_coleta}: " + " | ".join(resultados)
    else:
        resumo_final = "Nenhum exame válido encontrado."

    st.subheader("Resumo gerado:")
    st.text_area("Resumo:", resumo_final, height=300)
    st.download_button("Copiar Resumo", resumo_final, file_name="resumo.txt", mime="text/plain")

        st.subheader("Resumo final:")
        st.text_area("Resumo:", value=resumo_final, height=300)
        st.download_button("Baixar Resumo", resumo_final, file_name="resumo_exames.txt")
    else:
        st.warning("Nenhum resultado numérico encontrado no PDF.")
