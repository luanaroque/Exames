import streamlit as st
import fitz
import re
import streamlit.components.v1 as components
from typing import Dict, List
from io import BytesIO

def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_exam_data(text: str) -> List[Dict[str, str]]:
    exams = []

    # Corrigi aqui as regex: tudo dentro de uma lista normal
    patterns = [
        r'([^:\n]+):\s*([^:\n]+)',
        r'([^=\n]+)=\s*([^=\n]+)',
        r'([^:\n]+)\s*(?::|=)\s*([0-9,.]+(?:\s*[a-zA-Z/%]+)?)',
        r'([^:\n]+):\s*((?:Reagente|Não Reagente|Positivo|Negativo))'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            name = match.group(1).strip()
            result = match.group(2).strip()
            if len(name) < 2 or len(result) < 1:
                continue
            exams.append({
                'name': name,
                'result': result
            })
    
    return exams

def main():
    st.set_page_config(page_title="Transcritor de exames", layout="wide")
    st.title("Transcritor de Exames Médicos")

    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")
    
    if uploaded_file:
        try:
            text = extract_text_from_pdf(uploaded_file)
            exams = parse_exam_data(text)
            
            if exams:
                # Cria o resumo em linha única
                resumo = " | ".join([f"{exam['name']} {exam['result']}" for exam in exams])

                st.subheader("Resumo gerado")
                st.text_area("Resumo:", resumo, height=250)

                # Botão copiar usando JavaScript
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
