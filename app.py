
import streamlit as st
import re
import pdfplumber

st.set_page_config(page_title="Resumo de Exames - Luana", layout="centered")

# Estilização geral
st.markdown(
    """
    <style>
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

# Títulos
st.markdown('<div class="title">Resumo de Exames Laboratoriais</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transforme rapidamente PDFs de exames em resumos prontos para o prontuário</div>', unsafe_allow_html=True)

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

def encontrar_lab_data(texto):
    lab_name = ""
    data_coleta = ""
    # Tenta encontrar laboratório pelo site ou nome
    lab_match = re.search(r"(Alta Diagnósticos|Fleury|Dasa|Sabin|Laboratório [\w\s]+)", texto, re.IGNORECASE)
    if lab_match:
        lab_name = lab_match.group(0).strip()
    # Tenta encontrar data
    data_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    if data_match:
        data_coleta = data_match.group(0)
    return lab_name, data_coleta

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

def formatar_linha(exames_dict, lab, data):
    componentes = [f"{ex} {valor}" for ex, valor in exames_dict.items()]
    return f"{lab}, {data}: " + " ".join(componentes)

if uploaded_file:
    texto = extrair_texto(uploaded_file)
    lab_name, data_coleta = encontrar_lab_data(texto)

    st.subheader("Informações do Exame")
    col1, col2 = st.columns(2)
    with col1:
        lab_name = st.text_input("Nome do laboratório:", value=lab_name if lab_name else "")
    with col2:
        data_coleta = st.text_input("Data da coleta:", value=data_coleta if data_coleta else "")

    exames_dict, alterados = extrair_exames(texto)

    if exames_dict:
        resumo = formatar_linha(exames_dict, lab=lab_name if lab_name else "LABORATÓRIO", data=data_coleta if data_coleta else "DATA")
        st.subheader("Linha pronta para o prontuário:")
        resumo_area = st.text_area("Resumo:", value=resumo, height=200)

        # Botão de copiar
        st.markdown(f"""
            <button class="copy-button" onclick="navigator.clipboard.writeText(`{resumo}`)">
            Copiar Resumo
            </button>
            """, unsafe_allow_html=True)

    if alterados:
        st.subheader("Observações (valores alterados):")
        for a in alterados:
            st.markdown(f"- **{a}**")
