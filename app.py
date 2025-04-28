
import streamlit as st
import fitz
import re
import logging
from typing import Dict, List
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_exam_data(text: str) -> List[Dict[str, str]]:
    exams = []
    
    # Patterns for different exam formats
    patterns = [
        r'([^:
]+):\s*([^
]+)',
        r'([^=
]+)=\s*([^
]+)',
        r'([^:
]+)\s*(?::|=)\s*([0-9,.]+(?:\s*[a-zA-Z/%]+)?)',
        r'([^:
]+):\s*((?:Reagente|Não Reagente|Positivo|Negativo))'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            name = match.group(1).strip()
            result = match.group(2).strip()
            
            if len(name) < 2 or len(result) < 1:
                continue
                
            logger.info(f"Found exam: {name} = {result}")
            exams.append({
                'name': name,
                'result': result
            })
    
    return exams

def main():
    st.title("Analisador de Exames Médicos")
    
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")
    
    if uploaded_file:
        try:
            text = extract_text_from_pdf(uploaded_file)
            exams = parse_exam_data(text)
            
            st.subheader("Resultados Encontrados")
            for exam in exams:
                st.write(f"**{exam['name']}:** {exam['result']}")
                
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")

if __name__ == "__main__":
    main()
