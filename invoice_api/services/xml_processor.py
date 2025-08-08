import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def process_xml_nfe(xml_content):
    """
    Processa XML de NFe e extrai dados estruturados
    """
    try:
        # Parse do XML
        root = ET.fromstring(xml_content)
        
        # Namespaces comuns em NFe
        ns = {
            'nfe': 'http://www.portalfiscal.inf.br/nfe',
            'ds': 'http://www.w3.org/2000/09/xmldsig#'
        }
        
        # Buscar dados do emissor
        emit = root.find('.//nfe:emit', ns)
        nome_emissor = None
        cnpj_emissor = None
        endereco_emissor = None
        
        if emit is not None:
            nome_tag = emit.find('nfe:xNome', ns)
            if nome_tag is not None:
                nome_emissor = nome_tag.text
                
            cnpj_tag = emit.find('nfe:CNPJ', ns)
            if cnpj_tag is not None:
                cnpj = cnpj_tag.text
                if len(cnpj) == 14:
                    cnpj_emissor = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
            
            # Endereço
            endereco = emit.find('nfe:enderEmit', ns)
            if endereco is not None:
                logr = endereco.find('nfe:xLgr', ns)
                nro = endereco.find('nfe:nro', ns)
                if logr is not None:
                    endereco_emissor = logr.text
                    if nro is not None:
                        endereco_emissor += f", {nro.text}"
        
        # Buscar dados do destinatário
        dest = root.find('.//nfe:dest', ns)
        cpf_cnpj_consumidor = None
        
        if dest is not None:
            cpf_tag = dest.find('nfe:CPF', ns)
            if cpf_tag is not None:
                cpf = cpf_tag.text
                if len(cpf) == 11:
                    cpf_cnpj_consumidor = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            else:
                cnpj_tag = dest.find('nfe:CNPJ', ns)
                if cnpj_tag is not None:
                    cnpj = cnpj_tag.text
                    if len(cnpj) == 14:
                        cpf_cnpj_consumidor = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        
        # Buscar dados da nota
        ide = root.find('.//nfe:ide', ns)
        data_emissao = None
        numero_nota_fiscal = None
        serie_nota_fiscal = None
        
        if ide is not None:
            data_tag = ide.find('nfe:dhEmi', ns)
            if data_tag is not None:
                # Data no formato ISO, converter para DD/MM/YYYY
                data_iso = data_tag.text[:10]  # Pegar só a data
                if '-' in data_iso:
                    year, month, day = data_iso.split('-')
                    data_emissao = f"{day}/{month}/{year}"
            
            nf_tag = ide.find('nfe:nNF', ns)
            if nf_tag is not None:
                numero_nota_fiscal = nf_tag.text
                
            serie_tag = ide.find('nfe:serie', ns)
            if serie_tag is not None:
                serie_nota_fiscal = serie_tag.text
        
        # Buscar valor total
        total = root.find('.//nfe:vNF', ns)
        valor_total = None
        if total is not None:
            valor_total = total.text
        
        # Buscar forma de pagamento
        pag = root.find('.//nfe:pag', ns)
        forma_pgto = "outros"
        
        if pag is not None:
            tpag = pag.find('nfe:tPag', ns)
            if tpag is not None:
                tipo_pag = tpag.text
                if tipo_pag == "01":  # Dinheiro
                    forma_pgto = "dinheiro"
                elif tipo_pag == "17":  # PIX
                    forma_pgto = "pix"
        
        result = {
            "nome_emissor": nome_emissor,
            "CNPJ_emissor": cnpj_emissor,
            "endereco_emissor": endereco_emissor,
            "CNPJ_CPF_consumidor": cpf_cnpj_consumidor,
            "data_emissao": data_emissao,
            "numero_nota_fiscal": numero_nota_fiscal,
            "serie_nota_fiscal": serie_nota_fiscal,
            "valor_total": valor_total,
            "forma_pgto": forma_pgto
        }
        
        logger.info(f"XML processado com sucesso: {result}")
        return result
        
    except ET.ParseError as e:
        logger.error(f"Erro no parse do XML: {str(e)}")
        raise Exception(f"XML inválido: {str(e)}")
    except Exception as e:
        logger.error(f"Erro no processamento do XML: {str(e)}")
        raise Exception(f"Erro no processamento: {str(e)}")