# services/nlp_service.py

import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def process_text_and_generate_json(text):
    """
    Processa o texto extraído da nota fiscal e gera JSON com os dados estruturados
    """
    logger.info("Iniciando processamento NLP do texto")
    
    # Limpar e normalizar texto
    text_clean = text.replace('\n', ' ').replace('\r', ' ')
    text_lower = text.lower()
    
    # Extrair nome do emissor (buscar por razão social ou nome fantasia)
    nome_emissor = extract_company_name(text)
    
    # Extrair CNPJ
    cnpj_emissor = extract_cnpj(text)
    
    # Extrair CPF (do consumidor)
    cpf_consumidor = extract_cpf(text)
    
    # Extrair endereço
    endereco_emissor = extract_address(text)
    
    # Extrair data de emissão
    data_emissao = extract_date(text)
    
    # Extrair número da nota fiscal
    numero_nota_fiscal = extract_invoice_number(text)
    
    # Extrair série da nota fiscal
    serie_nota_fiscal = extract_series(text)
    
    # Extrair valor total
    valor_total = extract_total_value(text)
    
    # Determinar forma de pagamento
    forma_pgto = extract_payment_method(text_lower)
    
    result = {
        "nome_emissor": nome_emissor,
        "CNPJ_emissor": cnpj_emissor,
        "endereco_emissor": endereco_emissor,
        "CNPJ_CPF_consumidor": cpf_consumidor,
        "data_emissao": data_emissao,
        "numero_nota_fiscal": numero_nota_fiscal,
        "serie_nota_fiscal": serie_nota_fiscal,
        "valor_total": valor_total,
        "forma_pgto": forma_pgto
    }
    
    logger.info(f"Processamento NLP concluído: {result}")
    return result

def extract_company_name(text):
    """Extrai o nome da empresa emissora"""
    # Padrões comuns para identificar razão social
    patterns = [
        r'razão social[:\s]*([^\n\r]+)',
        r'nome empresarial[:\s]*([^\n\r]+)',
        r'denominação[:\s]*([^\n\r]+)',
        r'^([A-Z][A-Z\s&.-]+(?:LTDA|S\.A\.|ME|EPP))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if len(name) > 3:  # Nome muito curto provavelmente não é válido
                return name
    
    return None

def extract_cnpj(text):
    """Extrai CNPJ do texto"""
    cnpj_pattern = r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}'
    cnpjs = re.findall(cnpj_pattern, text)
    
    if cnpjs:
        # Normalizar formato
        cnpj = re.sub(r'[^\d]', '', cnpjs[0])
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    
    return None

def extract_cpf(text):
    """Extrai CPF do texto"""
    cpf_pattern = r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}'
    cpfs = re.findall(cpf_pattern, text)
    
    if cpfs:
        # Normalizar formato
        cpf = re.sub(r'[^\d]', '', cpfs[0])
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    return None

def extract_address(text):
    """Extrai endereço do texto"""
    # Padrões para identificar endereço
    address_patterns = [
        r'endere[çc]o[:\s]*([^\n\r]+)',
        r'rua[:\s]*([^\n\r,]+)',
        r'av[^\w]*([^\n\r,]+)',
        r'pra[çc]a[:\s]*([^\n\r,]+)',
    ]
    
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            address = match.group(1).strip()
            if len(address) > 5:
                return address
    
    return None

def extract_date(text):
    """Extrai data de emissão"""
    # Padrões de data
    date_patterns = [
        r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b',
        r'\b(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b',
        r'data[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
        r'emiss[ãa]o[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            date_str = matches[0]
            # Normalizar formato para DD/MM/YYYY
            date_parts = re.split(r'[\/\-\.]', date_str)
            if len(date_parts) == 3:
                if len(date_parts[0]) == 4:  # YYYY/MM/DD
                    return f"{date_parts[2].zfill(2)}/{date_parts[1].zfill(2)}/{date_parts[0]}"
                else:  # DD/MM/YYYY
                    return f"{date_parts[0].zfill(2)}/{date_parts[1].zfill(2)}/{date_parts[2]}"
    
    return None

def extract_invoice_number(text):
    """Extrai número da nota fiscal"""
    patterns = [
        r'n[úu]mero[:\s]*(\d+)',
        r'nf[:\s]*(\d+)',
        r'nota fiscal[:\s]*(\d+)',
        r'n[°º][:\s]*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_series(text):
    """Extrai série da nota fiscal"""
    patterns = [
        r's[éeí]rie[:\s]*(\d+)',
        r'ser[:\s]*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_total_value(text):
    """Extrai valor total"""
    # Padrões para valores monetários
    value_patterns = [
        r'total[:\s]*r\$\s*(\d+[,\.]\d{2})',
        r'valor total[:\s]*r\$\s*(\d+[,\.]\d{2})',
        r'r\$\s*(\d+[,\.]\d{2})',
        r'(\d+[,\.]\d{2})',
    ]
    
    for pattern in value_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Pegar o maior valor encontrado (provavelmente o total)
            values = []
            for match in matches:
                value_str = match.replace(',', '.')
                try:
                    value = float(value_str)
                    values.append(value)
                except ValueError:
                    continue
            
            if values:
                max_value = max(values)
                return f"{max_value:.2f}"
    
    return None

def extract_payment_method(text_lower):
    """Determina forma de pagamento"""
    if any(word in text_lower for word in ['dinheiro', 'espécie', 'cash']):
        return 'dinheiro'
    elif any(word in text_lower for word in ['pix']):
        return 'pix'
    elif any(word in text_lower for word in ['cartão', 'cartao', 'débito', 'crédito', 'credito']):
        return 'outros'
    elif any(word in text_lower for word in ['cheque']):
        return 'outros'
    else:
        return 'outros'