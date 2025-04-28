import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Transcritor de exames", layout="wide")
st.title("Transcritor de exames")

# Lista de abreviações dos exames
abreviacoes = {
    "Hemoglobina": "Hb",
    "Leucócitos": "Leuco",
    "Plaquetas": "Plaq",
    "Glicose": "Gj",
    "Glicemia de jejum": "Gj",
    "Creatinina": "Cr",
    "Ureia": "U",
    "Ácido úrico": "Ácido úrico",
    "Sódio": "Na",
    "Potássio": "K",
    "Cálcio": "Ca",
    "Cálcio ionizado": "Ca ionizado",
    "Ferro": "Ferro",
    "Zinco": "Zinco",
    "Ácido fólico": "Ácido fólico",
    "Vitamina B12": "Vit B12",
    "Vitamina D": "Vit D",
    "25-hidroxivitamina D": "Vit D",
    "1,25-dihidroxivitamina D": "1,25 Vit D",
    "Colesterol total": "CT",
    "HDL colesterol": "HDL",
    "LDL colesterol": "LDL",
    "VLDL colesterol": "VLDL",
    "Não-HDL colesterol": "não-HDL",
    "Triglicerídeos": "Tg",
    "TGO": "TGO",
    "AST": "TGO",
    "TGP": "TGP",
    "ALT": "TGP",
    "Fosfatase alcalina": "FAL",
    "Gama GT": "GGT",
    "Gama glutamil transferase": "GGT",
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
    "Hormônio paratireoideo": "PTH",
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

def encontrar_exames(texto):
    resultados = {}
    linhas = texto.split('\n')
    for idx, linha in enumerate(linhas):
        for nome, abrev in abreviacoes.items():
            if re.search(rf"\b{nome}\b", linha, re.IGNORECASE):
                # Procurar valor real nas próximas 2 linhas se não achar na mesma
                match = re.search(r'([-+]?\d+[\d\.,]*)', linha)
                if not match and idx + 1 < len(linhas):
                    match = re.search(r'([-+]?\d+[\d\.,]*)', linhas[idx + 1])
                if not match and idx + 2 < len(linhas):
                    match = re.search(r'([-+]?\d+[\d\.,]*)', linhas[idx + 2])
                if match:
                    valor = match.group(1).replace(",", ".")
                    if abrev in exames_hemograma or abrev not in {"Eri", "Ht", "VCM", "HCM", "CHCM", "Neutro", "Eos", "Baso", "Linf", "Mono", "RDW"}:
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
        ordem = ["Hb", "Leuco", "Plaq", "Cr", "U", "Gj", "CT", "HDL", "LDL", "não-HDL", "VLDL", "Tg",
                 "TGO", "TGP", "FAL", "GGT", "Vit D", "Vit B12", "TSH", "T4L", "T3", "T4", 
                 "FSH", "LH", "E2", "Prog", "Testo", "SHBG", "DHEA-S", "PTH", "1,25 Vit D", "17-OH-Pg",
                 "Ácido úrico", "Na", "K", "Ca", "Ca ionizado", "PCR", "HIV", "Anti-HCV", "Anti-HBs",
                 "AgHBs", "AgHBe", "Anti-HBe", "Anti-HBc IgG", "Anti-HBc IgM", "Sífilis", "VDRL", "FTA-ABS", "HCG", "Zinco", "Ácido fólico", "Ferro"]

        for exame in ordem:
            if exame in exames:
                grupo.append(f"{exame} {exames[exame]}")
                if exame in ["Plaq", "Tg", "GGT", "Vit D", "Vit B12", "PCR", "HIV", "Anti-HCV", "Ferro"]:
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
        st.warning("Nenhum exame encontrado no documento.")
