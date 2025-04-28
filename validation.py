
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def validate_exam_result(result: str, exam_type: str) -> Tuple[bool, str]:
    if exam_type == 'numeric':
        # Remove common unit patterns and convert to float
        numeric_value = re.sub(r'[^\d.,]', '', result.replace(',', '.'))
        try:
            float(numeric_value)
            return True, result
        except ValueError:
            return False, f"Valor inválido: {result}"
            
    elif exam_type == 'categorical':
        valid_categories = {'positivo', 'negativo', 'reagente', 'não reagente', 'normal', 'alterado'}
        if result.lower() in valid_categories:
            return True, result
        return False, f"Categoria inválida: {result}"
    
    return True, result

def identify_exam_type(exam_name: str, result: str) -> str:
    numeric_patterns = [
        r'\d+(?:[,.]\d+)?(?:\s*[a-zA-Z/%]+)?$',  # Numbers with optional units
        r'(?:maior|menor|igual a)\s*\d+'  # Comparative values
    ]
    
    categorical_patterns = [
        r'^(positivo|negativo|reagente|não reagente|normal|alterado)$',
        r'presente|ausente'
    ]
    
    for pattern in numeric_patterns:
        if re.search(pattern, result.lower()):
            return 'numeric'
            
    for pattern in categorical_patterns:
        if re.search(pattern, result.lower()):
            return 'categorical'
            
    return 'text'

def extract_exam_fields(text: str) -> List[Dict[str, str]]:
    exams = []
    
    # Enhanced patterns for specific fields
    patterns = {
        'exam_date': r'(?:Data da coleta|Coletado em|Data):\s*(\d{2}/\d{2}/\d{4})',
        'exam_time': r'(?:Hora|Horário):\s*(\d{2}:\d{2})',
        'doctor': r'(?:Médico|Dr\.|Dra\.)[\s:]+([^CRM
]+)(?:\s+CRM[:\s]*(\d+))?',
        'reference': r'(?:Valor de referência|Referência)[\s:]+([^
]+)',
        'method': r'(?:Método|Metodologia)[\s:]+([^
]+)',
        'exam_result': [
            r'(?:Resultado|Valor)[\s:]+([^
]+)',
            r'([^:
]+):\s*([^
]+)',  # Generic pattern
            r'([^=
]+)=\s*([^
]+)',  # Equals format
            r'([^:
]+)\s*(?::|=)\s*([0-9,.]+(?:\s*[a-zA-Z/%]+)?)',  # Numeric
            r'([^:
]+):\s*((?:Reagente|Não Reagente|Positivo|Negativo))'  # Qualitative
        ]
    }
    
    # Extract structured fields
    exam_data = {}
    for field, pattern in patterns.items():
        if isinstance(pattern, list):
            for p in pattern:
                matches = re.finditer(p, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    exam_name = match.group(1).strip()
                    result = match.group(2).strip() if len(match.groups()) > 1 else match.group(1).strip()
                    
                    if len(exam_name) < 2 or len(result) < 1:
                        continue
                        
                    exam_type = identify_exam_type(exam_name, result)
                    is_valid, validated_result = validate_exam_result(result, exam_type)
                    
                    exam_data = {
                        'name': exam_name,
                        'result': validated_result,
                        'type': exam_type,
                        'is_valid': is_valid
                    }
                    exams.append(exam_data)
        else:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                exam_data[field] = match.group(1).strip()
    
    return exams

