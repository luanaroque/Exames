import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Transcritor de exames", layout="wide")
st.title("Transcritor de exames")

# Lista de exames e suas abreviações
abreviacoes = {
    "Hemoglobina": "Hb",
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
    "VLDL colesterol": "VLDL",
    "Triglicerídeos": "Tg",
    "Triglicérides": "Tg",
    "Não-HDL colesterol": "não-HDL",
    "TGO": "TGO",
    "AST": "TGO",
    "TGP": "TGP",
    "ALT": "TGP",
    "Fosfatase alcalina": "FAL",
    "Gama GT": "GGT",
    "Gama glutamil transferase": "GGT",
    "Bilirrubina total": "BT",
    "Bilirrubina direta": "BD",
    "Bilirrubina indireta": "BI",
    "PCR": "PCR",
    "Proteína C reativa": "PCR",
    "Ferro": "Ferro",
    "Saturação da transferrina": "Sat Transferrina",
    "TSH": "TSH",
    "T4 livre": "T4L",
    "Tiroxina livre": "T4L",
    "T3": "T3",
    "Vitamina D": "Vit D",
    "25-hidroxivitamina D": "Vit D",
    "Vitamina B12": "Vit B12",
    "HCG": "HCG",
}

# Exames do hemograma que queremos manter
exames_hemograma = {"Hb", "Leuco", "Plaq"}

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
    texto = re.sub(r'Página:.*', '', texto)
    return texto

def encontrar_exames(texto):
    resultados = {}
    linhas = texto.split('\n')
    for idx, linha in enumerate(linhas):
        for nome, abrev in abreviacoes.items():
            if re.search(rf"\b{nome}\b", linha, re.IGNORECASE):
                # Procurar o valor no mesmo lugar ou na linha de baixo
                match = re.search(r'([-+]?\d+[\d\.,]*)', linha)
                if not match and idx + 1 < len(linhas):
                    match = re.search(r'([-+]?\d+[\d\.,]*)', linhas[idx + 1])
                if match:
                    valor = match.group(1).replace(",", ".")
                    # Somente pega Hb, Leuco, Plaq se for Hemograma
                    if abrev in exames_hemograma or abrev not in {"Hb", "Ht", "Eri", "Neutro", "Eos", "Baso", "Linf", "Mono", "RDW", "VCM", "HCM", "CHCM"}:
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
        ordem = ["Hb", "Leuco", "Plaq", "Cr", "U", "Gj", "CT", "HDL", "LDL", "não-HDL", "VLDL", "Tg", "TGO", "TGP", "FAL", "GGT", "Vit D", "Vit B12", "TSH", "T4L", "T3", "PCR", "Ferro", "Sat Transferrina", "HCG"]
        for exame in ordem:
            if exame in exames:
                grupo.append(f"{exame} {exames[exame]}")
                if exame in ["Plaq", "Tg", "GGT", "Vit D", "Vit B12", "PCR", "Sat Transferrina"]:
                    partes.append(" ".join(grupo))
                    grupo = []
        if grupo:
            partes.append(" ".join(grupo))

        resumo = f"{laboratorio}, {data_exame}: " + " | ".join(partes)

        st.subheader("Resumo")
        resumo_area = st.text_area("Resumo gerado:", resumo, height=300)
        st.button("Copiar resumo", on_click=lambda: st.session_state.update({"_clipboard": resumo_area}))

        st.caption("Selecione e copie o texto acima manualmente se necessário.")
    else:
        st.warning("Nenhum exame conhecido encontrado no documento.")
