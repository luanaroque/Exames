import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Transcritor de exames", layout="wide")
st.title("Transcritor de exames")

abreviacoes = {
    "Eritrócitos": "Eri",
    "Hemoglobina": "Hb",
    "Hematócrito": "Ht",
    "Hemoglobina corpuscular média": "HCM",
    "Volume corpuscular médio": "VCM",
    "Concentração de hemoglobina corpuscular média": "CHCM",
    "RDW": "RDW",
    "Leucócitos": "Leuco",
    "Neutrófilos": "Neutro",
    "Eosinófilos": "Eos",
    "Basófilos": "Baso",
    "Linfócitos": "Linf",
    "Monócitos": "Mono",
    "Plaquetas": "Plaq",
    "Volume plaquetário médio": "VPM",
    "Creatinina": "Cr",
    "Ureia": "U",
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
    "Homocisteína": "Homocist",
    "TSH": "TSH",
    "T4 livre": "T4L",
    "Tiroxina livre": "T4L",
    "T3": "T3",
    "Triiodotironina": "T3",
    "25 hidroxi-vitamina D": "Vit D",
    "25-hidroxivitamina D": "Vit D",
    "1,25 dihidroxivitamina D": "1,25 Vit D",
    "Vitamina D": "Vit D",
    "Vitamina B12": "Vit B12",
    "Glicose": "Gj",
    "Glicemia de jejum": "Gj",
    "Hemoglobina glicada": "HbA1c",
    "Colesterol total": "CT",
    "HDL colesterol": "HDL",
    "LDL colesterol": "LDL",
    "VLDL colesterol": "VLDL",
    "Não-HDL colesterol": "não-HDL",
    "Triglicerídeos": "Tg",
    "Triglicérides": "Tg",
    "HCG": "HCG",
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
    texto = re.sub(r'Página:.*', '', texto)
    return texto

def encontrar_exames(texto):
    resultados = {}
    linhas = texto.split('\n')
    for idx, linha in enumerate(linhas):
        for nome, abrev in abreviacoes.items():
            if re.search(rf"\b{nome}\b", linha, re.IGNORECASE):
                # Tenta encontrar valor na mesma linha
                match = re.search(r'([-+]?\d+[\d\.,]*)', linha)
                # Se não encontrar, tenta buscar na próxima linha
                if not match and idx + 1 < len(linhas):
                    match = re.search(r'([-+]?\d+[\d\.,]*)', linhas[idx + 1])
                if match:
                    valor = match.group(1).replace(",", ".")
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
        resumo_area = st.text_area("Resumo gerado:", resumo, height=300)
        st.button("Copiar resumo", on_click=lambda: st.session_state.update({"_clipboard": resumo_area}))

        st.caption("Selecione e copie o texto acima manualmente se necessário.")
    else:
        st.warning("Nenhum exame conhecido encontrado no documento.")
