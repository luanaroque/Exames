
import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="Transcritor de exames", page_icon=":clipboard:", layout="centered")

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

st.title("Transcritor de exames")

uploaded_file = st.file_uploader("Escolha o arquivo PDF do exame", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Tentativa de extrair a data de coleta
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    data_coleta = datas[-1] if datas else ""

    # Tentativa de extrair o nome do laboratório
    laboratorio = ""
    if "Einstein" in text:
        laboratorio = "Einstein"
    elif "Fleury" in text:
        laboratorio = "Fleury"
    elif "Delboni" in text:
        laboratorio = "Delboni"

    # Extrair exames com valores numéricos
    linhas = text.split("\n")
    resultados = []
    for linha in linhas:
        matches = re.findall(r"([A-Za-zçÇãõÕéÉêÊáÁíÍóÓúÚâÂôÔûÛ\-\s]+)\s*(-?\d+[.,]?\d*)", linha)
        for exame, valor in matches:
            exame = exame.strip()
            valor = valor.replace(",", ".").strip()
            if exame and valor:
                resultados.append(f"{exame} {valor}")

    if resultados:
        resumo = f"{laboratorio}, {data_coleta}: " + " | ".join(resultados)
    else:
        resumo = "Não foi possível extrair resultados numéricos."

    st.subheader("Linha pronta para o prontuário:")
    st.code(resumo, language="")

    st.button("Copiar Resumo", on_click=lambda: st.toast("Copie manualmente o texto acima."))
