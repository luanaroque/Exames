import streamlit as st
import fitz  # PyMuPDF
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Transcritor de exames", layout="wide")

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

st.title("Transcritor de exames")

# Abreviações conhecidas
abreviacoes = {
    "Hemoglobina": "Hb", "Hematócrito": "Ht", "Leucócitos": "Leuco", "Plaquetas": "Plaq",
    "Creatinina": "Cr", "Ureia": "U", "Glicose": "Gj", "Hemoglobina glicada": "HbA1c",
    "Colesterol total": "CT", "HDL colesterol": "HDL", "LDL colesterol": "LDL",
    "VLDL": "VLDL", "Triglicerídeos": "Tg", "Sódio": "Na", "Potássio": "K",
    "Cálcio": "Ca", "Cálcio ionizado": "Ca ionizado", "Magnésio": "Mg",
    "Ácido Úrico": "AcU", "Ferro": "Ferro", "Ferritina": "Ferritina",
    "Vitamina D": "Vit D", "Vitamina B12": "Vit B12", "Proteína C reativa": "PCR",
    "Fosfatase alcalina": "FAL", "Gama GT": "GGT", "TGO": "TGO", "TGP": "TGP",
    "TSH": "TSH", "T4 livre": "T4L", "T3": "T3", "FSH": "FSH", "LH": "LH",
    "Estradiol": "E2", "Progesterona": "Prog", "Testosterona total": "Testo",
    "Paratormônio": "PTH", "HCG": "HCG", "HIV 1/2": "HIV", "Anti-HCV": "Anti-HCV",
    "Sífilis": "Sífilis", "VDRL": "Sífilis", "AgHBs": "AgHBs", "Anti-HBs": "Anti-HBs",
    "Anti-HBe": "Anti-HBe", "Anti-HBc IgG": "Anti-HBc IgG", "Anti-HBc IgM": "Anti-HBc IgM",
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

def encontrar_valor(trecho, exame_nome):
    if re.search(r"não reagente|indetectável|não detectado", trecho, re.IGNORECASE):
        return "NR"
    numeros = re.findall(r'[-+]?\d[\d.,]*', trecho)
    if numeros:
        numeros = [n.replace(",", ".") for n in numeros]
        # Correção específica para Ferro
        if exame_nome.lower() == "ferro":
            return numeros[0] if len(numeros) >= 1 else None
        return numeros[0]
    return None

def encontrar_exames(texto):
    resultados = {}
    linhas = texto.split('\n')
    for idx, linha in enumerate(linhas):
        trecho = linha
        if idx + 1 < len(linhas):
            trecho += ' ' + linhas[idx + 1]
        for nome, abrev in abreviacoes.items():
            if nome.lower() in linha.lower():
                valor = encontrar_valor(trecho, nome)
                if valor:
                    resultados[abrev] = valor
        # Também pega qualquer exame diferente
        if ":" in linha and any(char.isdigit() for char in linha):
            exame_nome = linha.split(":")[0].strip()
            if exame_nome not in resultados.values() and exame_nome not in abreviacoes:
                valor = encontrar_valor(trecho, exame_nome)
                if valor:
                    resultados[exame_nome] = valor
    return resultados

def encontrar_lab_data(texto):
    lab = None
    data = None
    if "Albert Einstein" in texto:
        lab = "Albert Einstein"
    elif "Fleury" in texto or "Edgar Rizzatti" in texto:
        lab = "Fleury"
    elif "Hospital do Coração" in texto or "HCor" in texto:
        lab = "HCor"
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

    col1, col2 = st.columns(2)
    with col1:
        laboratorio = st.text_input("Laboratório", lab if lab else "")
    with col2:
        data_exame = st.text_input("Data da coleta", data if data else "")

    if exames:
        resumo_exames = [f"{exame} {valor}" for exame, valor in exames.items()]
        resumo_final = f"{laboratorio}, {data_exame}: " + " | ".join(resumo_exames)

        st.subheader("Resumo gerado")
        st.text_area("Resumo:", resumo_final, height=300)

        # Botão Copiar via JavaScript
        components.html(f"""
            <textarea id="to_copy" style="opacity:0;">{resumo_final}</textarea>
            <button onclick="copyToClipboard()">Copiar resumo</button>
            <script>
            function copyToClipboard() {{
                var copyText = document.getElementById("to_copy");
                copyText.select();
                document.execCommand("copy");
                alert("Resumo copiado para a área de transferência!");
            }}
            </script>
        """, height=100)
    else:
        st.warning("Nenhum exame encontrado no documento.")
