import pytesseract
from PIL import Image
import logging
import os

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path):
    """
    Extrai texto de imagem usando Tesseract OCR
    """
    try:
        logger.info(f"Iniciando extração de texto da imagem: {image_path}")
        
        # Verificar se arquivo existe
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
        
        # Abrir e processar imagem
        img = Image.open(image_path)
        
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Configurações do Tesseract para melhor OCR em português
        custom_config = r'--oem 3 --psm 6 -l por'
        
        # Extrair texto
        texto = pytesseract.image_to_string(img, config=custom_config)
        
        logger.info(f"Texto extraído com sucesso. Tamanho: {len(texto)} caracteres")
        logger.debug(f"Texto extraído: {texto[:200]}...")  # Log dos primeiros 200 caracteres
        
        return texto.strip()
        
    except Exception as e:
        logger.error(f"Erro na extração de texto: {str(e)}")
        raise Exception(f"Erro no OCR: {str(e)}")

def preprocess_image(image_path):
    """
    Pré-processa imagem para melhorar OCR (opcional)
    """
    try:
        img = Image.open(image_path)
        
        # Converter para escala de cinza
        img = img.convert('L')
        
        # Redimensionar se muito pequena
        width, height = img.size
        if width < 800 or height < 600:
            new_width = max(800, width * 2)
            new_height = max(600, height * 2)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
        
    except Exception as e:
        logger.error(f"Erro no pré-processamento: {str(e)}")
        return Image.open(image_path)