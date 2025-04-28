import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Transcritor de exames", layout="wide")
st.title("Transcritor de exames")

abreviacoes = {
    "Hemoglobina": "Hb",
    "Hematócrito": "Ht",
    "Leucócitos": "Leuco",
    "Plaquetas": "Plaq",
    "Creatinina": "Cr",
    "Ureia": "U",
    "Glicose": "Gj",
    "Glicemia de jejum": "Gj",
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
    "Gama glutamil transferase": "GGT",
    "Vitamina D": "Vit D",
    "Vitamina B12": "Vit B12",
    "PCR": "PCR",
    "Proteína C reativa": "PCR",
    "Ferritina": "Ferritina",
    "Saturação transferrina": "Sat Transferrina",
}

def extrair_texto(pdf_file):
    texto = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def limpar_texto(texto):
    texto = re.sub(r'\n+', '\n', texto)
    texto = re.sub(r'CRM.*', '', texto)
    texto = re.sub(r'ANVISA.*', '', texto)
    texto = re.sub(r'Tel.*', '', texto)
    texto = re.sub(r'Canal Médico.*', '', texto)
    return texto

def encontrar_exames(texto):
    resultados = {}
    for nome, abrev in abreviacoes.items():
        padrao = rf"{nome}.*?([-+]?\d+[\d\.,]*)"
        matches = re.findall(padrao, texto, re.IGNORECASE | re.DOTALL)
        if matches:
            valor = matches[0].replace(",", ".")
            resultados[abrev] = valor
    return resultados

def encontrar_lab_data(texto):
    lab = None
    data = None
    if "Albert Einstein" in texto:
        lab = "Albert Einstein"
    elif "Fleury" in texto or "Edgar Rizzatti" in texto:
        lab = "Fleury"

    datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    if datas:
        data = datas[0]
    return lab, data

uploaded_file = st.file_uploader("Envie o PDF de exames", type=["pdf"])

if uploaded_file:
    texto = extrair_texto(uploaded_file)
    texto = limpar_texto(texto)
    exames = encontrar_exames(texto)
    lab, data = encontrar_lab_data(texto)

    st.subheader("Informações do Exame")

    col1, col2 = st.columns(2)
    with col1:
        laboratorio = st.text_input("Laboratório", lab if lab else "")
    with col2:
        data_exame = st.text_input("Data da coleta", data if data else "")

    if exames:
        partes = []
        grupo = []
        for exame, valor in exames.items():
            grupo.append(f"{exame} {valor}")
            if exame in ["Plaq", "GGT", "Tg", "PCR", "Vit D", "Vit B12", "Ferritina", "Sat Transferrina"]:
                partes.append(" ".join(grupo))
                grupo = []
        if grupo:
            partes.append(" ".join(grupo))

        resumo = f"{laboratorio}, {data_exame}: " + " | ".join(partes)

        st.subheader("Resumo")
        resumo_area = st.text_area("Resumo gerado:", resumo, height=200)
        st.button("Copiar resumo", on_click=lambda: st.session_state.update({"_clipboard": resumo_area}))

        # Pequena dica de uso
        st.caption("Selecione e copie o texto acima manualmente se necessário.")
    else:
        st.warning("Nenhum exame conhecido encontrado no documento.")
