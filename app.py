import streamlit as st
import fitz  # PyMuPDF
import re
import streamlit.components.v1 as components

# Estilo
st.set_page_config(page_title="Transcritor de Exames", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #6EA1C7;}
    input, textarea {background-color: #ffffff !important; color: #333333 !important; font-size: 16px !important;}
    label, h1, h2, h3, .stMarkdown p {color: #ffffff !important; font-weight: bold;}
    .stButton button {background-color: #4d79ff; color: white; font-weight: bold; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

st.title("Transcritor de Exames")

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
    "Colesterol não-HDL": "não-HDL",
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
    "TSH": "TSH",
    "T4 livre": "T4l",
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
    "TGO": "TGO",
    "TGP": "TGP"
}

def extrair_texto(pdf_file):
    texto = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def limpar_texto(texto):
    texto = re.sub(r'\n+', '\n', texto)
    texto = re.sub(r'CRM.*|ANVISA.*|Tel.*|Página.*', '', texto)
    return texto

def encontrar_exames_com_referencia(texto):
    resultados = {}
    linhas = texto.split('\n')
    for i in range(len(linhas)):
        linha = linhas[i].strip()
        for nome, abrev in abreviacoes.items():
            if nome.lower() in linha.lower():
                # Valor provável na linha atual ou nas 2 seguintes
                bloco = " ".join(linhas[i:i+3])
                valor_match = re.search(r"[><]?\s*\d[\d,\.]*", bloco)
                referencia_match = re.findall(r"\d[\d,\.]*\s*[-–]\s*\d[\d,\.]*", bloco)

                if valor_match:
                    bruto = valor_match.group().replace(",", ".").replace(" ", "")
                    try:
                        valor = float(re.sub(r"[><]", "", bruto))
                        alterado = False
                        if referencia_match:
                            faixa = referencia_match[0]
                            lim = re.findall(r"\d[\d,\.]*", faixa)
                            if len(lim) == 2:
                                minimo = float(lim[0])
                                maximo = float(lim[1])
                                alterado = valor < minimo or valor > maximo
                        resultados[abrev] = f"**{valor}***" if alterado else f"{valor}"
                    except:
                        continue
    return resultados

def encontrar_lab_data(texto):
    lab = ""
    data = ""
    if "Albert Einstein" in texto:
        lab = "Einstein"
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
    exames = encontrar_exames_com_referencia(texto)
    lab, data = encontrar_lab_data(texto)

    col1, col2 = st.columns(2)
    with col1:
        laboratorio = st.text_input("Laboratório", lab)
    with col2:
        data_exame = st.text_input("Data da coleta", data)

    if exames:
        ordem = list(dict.fromkeys(abreviacoes.values()))
        resumo_exames = [f"{exame} {exames[exame]}" for exame in ordem if exame in exames]

        resumo_final = ""
        if laboratorio:
            resumo_final += laboratorio
        if data_exame:
            resumo_final += f", {data_exame}"
        if resumo_exames:
            resumo_final += ": " + " | ".join(resumo_exames)

        st.subheader("Resumo gerado")
        st.markdown(f"""
            <div style="background-color:#ffffff; color:#000000;
                        padding:15px; border-radius:8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        font-size: 16px;">
                <strong>{resumo_final}</strong>
            </div>
        """, unsafe_allow_html=True)

        # Botão copiar
        copy_html = f"""
        <script>
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(function() {{
                alert("Resumo copiado com sucesso!");
            }});
        }}
        </script>
        <button onclick="copyToClipboard(`{resumo_final}`)"
        style="background-color:#4d79ff;color:white;padding:10px 20px;border:none;border-radius:8px;font-weight:bold;font-size:16px;cursor:pointer;">
        Copiar resumo
        </button>
        """
        components.html(copy_html, height=100)

    else:
        st.warning("Nenhum exame encontrado.")
