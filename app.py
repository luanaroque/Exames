import streamlit as st
import fitz  # PyMuPDF
import re

# Estilo da página
st.set_page_config(page_title="Transcritor de exames", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #6EA1C7;
    }
    input, textarea {
        background-color: #ffffff !important;
        color: #333333 !important;
        font-size: 16px !important;
    }
    label, h1, h2, h3, .stMarkdown p {
        color: #ffffff !important;
        font-weight: bold;
    }
    .stButton button {
        background-color: #4d79ff;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Transcritor de exames")

# Abreviações
abreviacoes = {
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
    "Saturação da transferrina": "Sat Transferrina",
    "FSH": "FSH",
    "LH": "LH",
    "Estradiol": "E2",
    "Progesterona": "Prog",
    "Testosterona total": "Testo",
    "HCG": "HCG",
    "HIV 1/2": "HIV",
    "Anti-HCV": "Anti-HCV",
    "Sífilis": "Sífilis",
    "Hormônio Anti-Mulleriano": "AMH",
}

def extrair_texto(pdf_file):
    texto = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def limpar_texto(texto):
    texto = re.sub(r'(\n)+', '\n', texto)
    texto = re.sub(r'CRM.*', '', texto)
    texto = re.sub(r'ANVISA.*', '', texto)
    texto = re.sub(r'Tel.*', '', texto)
    texto = re.sub(r'Página.*', '', texto)
    return texto

def encontrar_valor(trecho):
    if re.search(r"(não reagente|indetectável|não detectado)", trecho, re.IGNORECASE):
        return "NR"
    numeros = re.findall(r'[-+]?\d[\d,.]*', trecho)
    if numeros:
        valor = numeros[0].replace(",", ".")
        return valor
    return None

def encontrar_exames(texto):
    resultados = {}
    linhas = texto.split('\n')
    for idx, linha in enumerate(linhas):
        for nome, abrev in abreviacoes.items():
            if nome.lower() in linha.lower():
                trecho = linha
                if idx + 1 < len(linhas):
                    trecho += ' ' + linhas[idx + 1]
                valor = encontrar_valor(trecho)
                if valor:
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

# App
uploaded_file = st.file_uploader("Envie o PDF de exames", type=["pdf"])

if uploaded_file:
    texto = extrair_texto(uploaded_file)
    texto = limpar_texto(texto)
    exames = encontrar_exames(texto)
    lab, data = encontrar_lab_data(texto)

    col1, col2 = st.columns(2)
    with col1:
        laboratorio = st.text_input("Laboratório", lab if lab else "")
    with col2:
        data_exame = st.text_input("Data da coleta", data if data else "")

    if exames:
        ordem = [
            "Hb", "Ht", "Leuco", "Plaq", "Cr", "U", "Gj", "HbA1c", "CT", "HDL", "LDL", "não-HDL", "VLDL", "Tg",
            "TGO", "TGP", "FAL", "GGT", "Vit D", "Vit B12", "PCR", "Ferritina", "Sat Transferrina",
            "FSH", "LH", "E2", "Prog", "Testo", "HCG", "HIV", "Anti-HCV", "Sífilis", "AMH"
        ]
        resumo_exames = []
        for exame in ordem:
            if exame in exames:
                resumo_exames.append(f"{exame} {exames[exame]}")

        resumo_final = f"{laboratorio}, {data_exame}: " + " | ".join(resumo_exames)

        st.subheader("Resumo gerado")
        st.text_area("Resumo:", resumo_final, height=300, key="resumo_texto")

        # Botão de copiar
        st.markdown(
            f"""
            <button onclick="navigator.clipboard.writeText(`{resumo_final}`)" style="background-color:#4d79ff;color:white;padding:10px 20px;border:none;border-radius:8px;font-weight:bold;font-size:16px;cursor:pointer;">
                Copiar resumo
            </button>
            """,
            unsafe_allow_html=True
        )

    else:
        st.warning("Nenhum exame encontrado no documento.")
