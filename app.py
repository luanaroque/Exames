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

# Funções
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
                # Buscar valor na linha "Resultado" que aparece logo após
                for j in range(i, min(i + 5, len(linhas))):
                    if "resultado" in linhas[j].lower():
                        valor_linha = linhas[j + 1] if j + 1 < len(linhas) else linhas[j]
                        break
                else:
                    continue

                # Buscar faixa de referência nas próximas linhas
                referencia = ""
                for k in range(i, min(i + 10, len(linhas))):
                    if re.search(r"\d", linhas[k]) and "-" in linhas[k]:
                        referencia = linhas[k]
                        break

                # Pega o valor numérico (mesmo com > ou <)
                match_valor = re.search(r"[><]?\s*\d[\d,\.]*", valor_linha)
                if match_valor:
                    valor_bruto = match_valor.group().replace(",", ".").replace(" ", "")
                    valor_formatado = valor_bruto
                    try:
                        valor_num = float(re.sub(r"[><]", "", valor_bruto))
                        # Comparar com faixa de referência
                        ref_nums = re.findall(r"\d[\d,\.]*", referencia)
                        if len(ref_nums) >= 2:
                            ref_min = float(ref_nums[0].replace(",", "."))
                            ref_max = float(ref_nums[1].replace(",", "."))
                            if valor_num < ref_min or valor_num > ref_max:
                                valor_formatado = f"**{valor_num}***"
                            else:
                                valor_formatado = f"{valor_num}"
                        else:
                            valor_formatado = f"{valor_num}"
                    except:
                        pass
                    resultados[abrev] = valor_formatado
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
        st.markdown(f"""<div style='background-color:#fff;padding:10px;border-radius:5px'>
        <strong>{resumo_final}</strong></div>""", unsafe_allow_html=True)

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
