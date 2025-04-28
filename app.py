import streamlit as st
import fitz
import re
import streamlit.components.v1 as components
from typing import List, Dict
from io import BytesIO

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

# Lista de abreviações conhecidas
abreviacoes = {
    "Hemoglobina": "Hb", "Hematócrito": "Ht", "Leucócitos": "Leuco", "Plaquetas": "Plaq",
    "Creatinina": "Cr", "Ureia": "U", "Glicose": "Gj", "Hemoglobina glicada": "HbA1c",
    "Colesterol total": "CT", "HDL colesterol": "HDL", "LDL colesterol": "LDL",
    "VLDL": "VLDL", "Triglicerídeos": "Tg", "Sódio": "Na", "Potássio": "K",
    "Cálcio": "Ca", "Cálcio ionizado": "Ca ionizado", "Magnésio": "Mg", "Ácido Úrico": "AcU",
    "Ferro": "Ferro", "Ferritina": "Ferritina", "Vitamina D": "Vit D", "Vitamina B12": "Vit B12",
    "Proteína C reativa": "PCR", "Fosfatase alcalina": "FAL", "Gama GT": "GGT",
    "TGO": "TGO", "TGP": "TGP", "TSH": "TSH", "T4 livre": "T4L", "T3": "T3",
    "FSH": "FSH", "LH": "LH", "Estradiol": "E2", "Progesterona": "Prog", "Testosterona total": "Testo",
    "Paratormônio": "PTH", "HCG": "HCG", "HIV 1/2": "HIV", "Anti-HCV": "Anti-HCV",
    "Sífilis": "Sífilis", "VDRL": "Sífilis", "AgHBs": "AgHBs", "Anti-HBs": "Anti-HBs",
    "Anti-HBe": "Anti-HBe", "Anti-HBc IgG": "Anti-HBc IgG", "Anti-HBc IgM": "Anti-HBc IgM"
}

# Palavras proibidas (linhas que devem ser ignoradas)
proibidos = [
    "CRM", "Página", "Assinatura", "Responsável Técnico", "Imunoturbidimetria",
    "Data de Nascimento", "Médico", "Paciente", "RDC", "Norma", "Emitido", "Ficha",
    "Método", "Referência", "Unidade", "Coleta", "Nascimento", "Sexo", "CPF", "Convênio"
]

def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def is_valid_exam(line: str) -> bool:
    line_lower = line.lower()
    if any(palavra.lower() in line_lower for palavra in proibidos):
        return False
    if re.search(r'\d', line) or re.search(r'(Reagente|Não Reagente|Positivo|Negativo)', line, re.IGNORECASE):
        return True
    return False

def parse_exam_data(text: str) -> List[Dict[str, str]]:
    exams = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not is_valid_exam(line):
            continue
        
        # Padrão de nome: valor
        match = re.match(r'([^:\n=]+)\s*[:=]\s*(.+)', line)
        if match:
            name = match.group(1).strip()
            result = match.group(2).strip()
            exams.append({'name': name, 'result': result})
        else:
            # Padrão de reagente/não reagente
            reagente = re.search(r'(.*?)(Reagente|Não Reagente|Positivo|Negativo)', line, re.IGNORECASE)
            if reagente:
                name = reagente.group(1).strip()
                result = reagente.group(2).strip()
                exams.append({'name': name, 'result': result})
    
    return exams

def main():
    st.title("Transcritor de Exames Médicos")

    uploaded_file = st.file_uploader("Envie o arquivo PDF do exame", type="pdf")

    if uploaded_file:
        try:
            text = extract_text_from_pdf(uploaded_file)
            exams = parse_exam_data(text)
            
            if exams:
                resumo_lista = []
                for exam in exams:
                    nome = exam['name']
                    resultado = exam['result']
                    nome_abreviado = abreviacoes.get(nome, nome)  # Usa abreviação se existir
                    resumo_lista.append(f"{nome_abreviado} {resultado}")
                
                resumo = " | ".join(resumo_lista)

                st.subheader("Resumo gerado")
                st.text_area("Resumo:", resumo, height=250)

                components.html(f"""
                    <textarea id="to_copy" style="opacity:0;">{resumo}</textarea>
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
                st.warning("Nenhum exame encontrado.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")

if __name__ == "__main__":
    main()
