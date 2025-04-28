
import streamlit as st
import re
import pdfplumber

st.set_page_config(page_title="Transcritor de Exames", layout="centered")

# Estilo com degradê lavanda para branco
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #F3E8FF 0%, #FFFFFF 100%);
    }
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
    .copy-button {
        background-color: #C3B1E1;
        color: black;
        padding: 12px 24px;
        border-radius: 10px;
        font-size: 18px;
        border: none;
        cursor: pointer;
        margin-top: 10px;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">Transcritor de Exames</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transforme PDFs de exames em linhas prontas para o prontuário</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Escolha o arquivo PDF do exame", type="pdf")

# Mapeamento para abreviações
mapeamento_exames = {
    "hemoglobina": "Hb",
    "hematócrito": "Ht",
    "leucócitos": "Leuco",
    "plaquetas": "Plaq",
    "glicose": "Gj",
    "hemoglobina glicada": "HbA1c",
    "colesterol total": "CT",
    "hdl colesterol": "HDL",
    "ldl colesterol": "LDL",
    "vldl colesterol": "VLDL",
    "triglicerídeos": "Tg",
    "sódio": "Na",
    "potássio": "K",
    "cálcio": "Ca",
    "magnésio": "Mg",
    "tgo": "TGO",
    "ast": "TGO",
    "tgp": "TGP",
    "alt": "TGP",
    "gama-glutamil transferase": "GGT",
    "gama gt": "GGT",
    "proteína c reativa": "PCR",
    "ferritina": "Ferritina",
    "vitamina d": "Vit D",
    "vitamina b12": "Vit B12",
    "tsh": "TSH",
    "t4 livre": "T4l",
    "estradiol": "Estradiol",
    "testosterona total": "Testosterona Total",
    "bilirrubina total": "BT",
    "bilirrubina direta": "BD",
    "bilirrubina indireta": "BI",
    "egrf": "eGFR"
}

def extrair_texto(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def encontrar_data_coleta(texto):
    # Procurar onde menciona coleta ou recebimento
    linhas = texto.split("\n")
    for linha in linhas:
        if "coleta" in linha.lower() or "recebimento" in linha.lower():
            match = re.search(r"(\d{2}/\d{2}/\d{4})", linha)
            if match:
                return match.group(0)
    return ""

def encontrar_lab(texto):
    lab_match = re.search(r"(Alta Diagnósticos|Fleury|Dasa|Sabin|Einstein|Laboratório [\w\s]+)", texto, re.IGNORECASE)
    if lab_match:
        return lab_match.group(0).strip()
    return ""

def extrair_exames_limpos(texto):
    exames = {}
    linhas = texto.split("\n")
    for linha in linhas:
        linha = linha.strip()
        if len(linha) < 80:  # Ignorar textos muito longos
            match = re.match(r"([A-Za-zÀ-ÿ\s\-]+)\s+([-<]?[0-9]+[.,]?[0-9]*)", linha)
            if match:
                nome_exame = match.group(1).strip().lower()
                valor = match.group(2).replace(",", ".")
                nome_abreviado = mapeamento_exames.get(nome_exame, match.group(1).strip())
                exames[nome_abreviado] = valor
    return exames

def formatar_linha(exames_dict, lab, data):
    componentes = [f"{ex} {valor}" for ex, valor in exames_dict.items()]
    return f"{lab}, {data}: " + " ".join(componentes)

if uploaded_file:
    texto = extrair_texto(uploaded_file)
    lab_name = encontrar_lab(texto)
    data_coleta = encontrar_data_coleta(texto)

    st.success("Exames extraídos com sucesso! Confira abaixo.")

    st.subheader("Informações do Exame")
    col1, col2 = st.columns(2)
    with col1:
        lab_name = st.text_input("Nome do laboratório:", value=lab_name if lab_name else "")
    with col2:
        data_coleta = st.text_input("Data da coleta:", value=data_coleta if data_coleta else "")

    exames_dict = extrair_exames_limpos(texto)

    if exames_dict:
        resumo = formatar_linha(exames_dict, lab=lab_name if lab_name else "LABORATÓRIO", data=data_coleta if data_coleta else "DATA")
        st.subheader("Linha pronta para o prontuário:")
        resumo_area = st.text_area("Resumo:", value=resumo, height=200)

        st.markdown(f"""
            <button class="copy-button" onclick="navigator.clipboard.writeText(`{resumo}`)">
            Copiar Resumo
            </button>
            """, unsafe_allow_html=True)
