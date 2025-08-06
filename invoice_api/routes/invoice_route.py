from flask import Blueprint, request, jsonify
import os
from services.ocr_service import extract_text_from_image
from services.nlp_service import process_text_and_generate_json
from werkzeug.utils import secure_filename
import shutil
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

invoice_bp = Blueprint('invoice', __name__)

UPLOAD_FOLDER = 'uploads'
DEST_FOLDER = 'classificadas'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@invoice_bp.route('/api/v1/invoice', methods=['POST'])
def upload_invoice():
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            logger.warning("Tentativa de upload sem arquivo")
            return jsonify({"error": "Arquivo não enviado"}), 400

        file = request.files['file']
        
        # Verificar se arquivo foi selecionado
        if file.filename == '':
            logger.warning("Nenhum arquivo selecionado")
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
            
        # Verificar extensão do arquivo
        if not allowed_file(file.filename):
            logger.warning(f"Tipo de arquivo não permitido: {file.filename}")
            return jsonify({"error": "Tipo de arquivo não permitido"}), 400

        # Salvar arquivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        logger.info(f"Arquivo salvo: {filepath}")

        # Extrair texto da imagem usando OCR
        logger.info("Iniciando extração de texto...")
        extracted_text = extract_text_from_image(filepath)
        
        if not extracted_text or extracted_text.strip() == "":
            logger.warning("Não foi possível extrair texto da imagem")
            return jsonify({"error": "Não foi possível extrair texto da imagem"}), 422

        logger.info("Texto extraído com sucesso")

        # Processar texto e gerar JSON
        logger.info("Processando texto com NLP...")
        nota_json = process_text_and_generate_json(extracted_text)
        
        logger.info(f"Dados extraídos: {nota_json}")

        # Classificar por forma de pagamento
        forma = nota_json.get('forma_pgto', 'outros')
        
        if forma in ['dinheiro', 'pix']:
            dest_dir = os.path.join(DEST_FOLDER, 'dinheiro')
        else:
            dest_dir = os.path.join(DEST_FOLDER, 'outros')
        
        # Criar diretório se não existir
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        destino = os.path.join(dest_dir, filename)
        shutil.copy(filepath, destino)
        
        logger.info(f"Arquivo classificado e movido para: {destino}")

        # Limpar arquivo temporário
        os.remove(filepath)
        
        return jsonify(nota_json), 200

    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

@invoice_bp.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "API funcionando"}), 200