import streamlit as st
import fitz  # PyMuPDF
import re

# Estilo personalizado
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

# Lista de abreviações
abreviacoes = {
    "Hemoglobina": "Hb",
    "Leucócitos": "Leuco",
    "Plaquetas": "Plaq",
    "Glicose": "Gj",
    "Creatinina": "Cr",
    "Ureia": "U",
    "Ácido úrico": "Ácido úrico",
    "Sódio": "Na",
    "Potássio": "K",
    "Cálcio": "Ca",
    "Cálcio ionizado": "Ca ionizado",
    "Ferro": "Ferro",
    "Saturação da transferrina": "Sat Transferrina",
    "Zinco": "Zinco",
    "Ácido fólico": "Ácido fólico",
    "Vitamina B12": "Vit B12",
    "Vitamina D": "Vit D",
    "1,25-dihidroxivitamina D": "1,25 Vit D",
    "Colesterol total": "CT",
    "HDL colesterol": "HDL",
    "LDL colesterol": "LDL",
    "VLDL colesterol": "VLDL",
    "Não-HDL colesterol": "não-HDL",
    "Triglicerídeos": "Tg",
    "TGO": "TGO",
    "TGP": "TGP",
    "Fosfatase alcalina": "FAL",
    "Gama GT": "GGT",
    "TSH": "TSH",
    "T4 livre": "T4L",
    "T3": "T3",
    "FSH": "FSH",
    "LH": "LH",
    "Estradiol": "E2",
    "Progesterona": "Prog",
    "Testosterona total": "Testo",
    "SHBG": "SHBG",
    "DHEA-S": "DHEA-S",
    "HCG": "HCG",
    "Paratormônio": "PTH",
    "17-alfa-hidroxiprogesterona": "17-OH-Pg",
    "Proteína C reativa": "PCR",
    "HIV 1/2": "HIV",
    "Anti-HCV": "Anti-HCV",
    "Anti-HBs": "Anti-HBs",
    "Antígeno HBs": "AgHBs",
    "Antígeno HBe": "AgHBe",
    "Anti-HBe": "Anti-HBe",
    "Anti-HBc IgG": "Anti-HBc IgG",
    "Anti-HBc IgM": "Anti-HBc IgM",
    "Sífilis": "Sífilis",
    "VDRL": "VDRL",
    "FTA-ABS": "FTA-ABS"
}

exames_hemograma = {"Hb", "Leuco", "Plaq"}

faixas_padroes = {
    "Ferro": (30, 300),
    "Sat Transferrina": (20, 60),
    "PCR": (0, 10),
    "Gj": (60, 110),
    "Cr": (0.4, 2),
}

# Funções de extração
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
    texto = re.sub(r'Página.*', '', texto)
    return texto

def encontrar_valor_puro(trecho, exame):
    if re.search(r"indetectável|não reagente|não detectado", trecho, re.IGNORECASE):
        return "NR"
    matches = re.findall(r'([-+]?\d+[.,]?\d*)', trecho)
    numeros = [float(m.replace(",", ".")) for m in matches if '-' not in m]
    if not numeros:
        return None
    if exame in faixas_padroes:
        faixa = faixas_padroes[exame]
        numeros_filtrados = [n for n in numeros if faixa[0] <= n <= faixa[1]]
        if numeros_filtrados:
            return str(int(numeros_filtrados[0]) if numeros_filtrados[0].is_integer() else numeros_filtrados[0])
    maior = max(numeros)
    return str(int(maior) if maior.is_integer() else maior)

def encontrar_exames(texto):
    resultados = {}
    linhas = texto.split('\n')
    for idx, linha in enumerate(linhas):
        for nome, abrev in abreviacoes.items():
            if re.search(rf"\b{nome}\b", linha, re.IGNORECASE):
                trecho = linha
                if idx + 1 < len(linhas):
                    trecho += ' ' + linhas[idx + 1]
                if idx + 2 < len(linhas):
                    trecho += ' ' + linhas[idx + 2]
                valor = encontrar_valor_puro(trecho, abrev)
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
    elif "Hospital do Coração" in texto or "HCor" in texto:
        lab = "HCor"
    datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    if datas:
        data = datas[0]
    return lab, data



# Upload do PDF e Geração do Resumo
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
        ordem = [
            "Hb", "Leuco", "Plaq", "Cr", "U", "Gj", "CT", "HDL", "LDL", "não-HDL", "VLDL", "Tg",
            "TGO", "TGP", "FAL", "GGT", "Vit D", "Vit B12", "TSH", "T4L", "T3", "FSH", "LH", "E2",
            "Prog", "Testo", "SHBG", "DHEA-S", "PTH", "1,25 Vit D", "17-OH-Pg", "Ácido úrico", "Na",
            "K", "Ca", "Ca ionizado", "PCR", "Sat Transferrina", "Ferro",
            "HCG", "HIV", "Sífilis", "Anti-HCV", "Anti-HBs", "AgHBs", "AgHBe", "Anti-HBe", "Anti-HBc IgG", "Anti-HBc IgM"
        ]
        for exame in ordem:
            if exame in exames:
                grupo.append(f"{exame} {exames[exame]}")
                if exame in ["Plaq", "Tg", "GGT", "Vit D", "Vit B12", "PCR", "Sat Transferrina", "Ferro", "Anti-HBs"]:
                    partes.append(" ".join(grupo))
                    grupo = []
        if grupo:
            partes.append(" ".join(grupo))

        resumo = f"{laboratorio}, {data_exame}: " + " | ".join(partes)

        st.subheader("Resumo gerado")
        resumo_area = st.text_area("Resumo gerado:", resumo, height=300, key="resumo_area")

        # Botão de copiar funcional usando JavaScript
        copy_button = st.button("Copiar resumo")
        if copy_button:
            st.markdown(
                f"""
                <script>
                navigator.clipboard.writeText(`{resumo}`);
                </script>
                """,
                unsafe_allow_html=True,
            )

        st.caption("O botão 'Copiar resumo' agora copia diretamente para a área de transferência!")
    else:
        st.warning("Nenhum exame encontrado no documento.")
