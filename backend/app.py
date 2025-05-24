import os
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src.classifier import classify_email
from src.responder import generate_response
from src.utils import extract_text_from_file, clean_text

# -------------- CONFIGURAÇÕES -----------------
class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    FRONTEND_FOLDER = os.path.join(BASE_DIR, '..', 'frontend')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

# -------------- UTILITÁRIOS -------------------
def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage, upload_folder):
    """Salva o arquivo enviado para a pasta de uploads."""
    filename = secure_filename(file_storage.filename)
    file_path = os.path.join(upload_folder, filename)
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(file_path)
    return file_path

def extract_input_text(request):
    """
    Extrai o texto do arquivo enviado ou do campo 'text'.
    Dá prioridade ao arquivo, se enviado.
    """
    # Se for upload de arquivo
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '' and allowed_file(file.filename):
            file_path = save_uploaded_file(file, Config.UPLOAD_FOLDER)
            try:
                text = extract_text_from_file(file_path)
            finally:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            if not text or not text.strip():
                raise ValueError('O arquivo enviado está vazio ou não pôde ser lido.')
            return text
        elif file and file.filename != '':
            raise ValueError('Arquivo não suportado. Use apenas PDF ou TXT.')
    # Se for texto simples via formulário/JSON
    text = request.form.get('text') or (request.json.get('text') if request.is_json else None)
    if not text or not text.strip():
        raise ValueError('Nenhum texto ou arquivo válido enviado')
    return text

def generate_result(text):
    """
    Executa todo o processamento: classificação e resposta automática.
    """
    if not text or not text.strip():
        raise ValueError('Texto vazio ou arquivo sem conteúdo')
    categoria = classify_email(text)
    try:
        resposta = generate_response(text, categoria)
    except Exception as e:
        print(f"Erro ao gerar resposta: {str(e)}")
        resposta = "Erro ao gerar resposta automática. Por favor, tente novamente."
    texto_processado = text[:200] + "..." if len(text) > 200 else text
    return {
        'categoria': categoria,
        'resposta': resposta,
        'texto_processado': texto_processado
    }

# -------------- FLASK APP ---------------------
def create_app(config_class=Config):
    app = Flask(__name__, static_folder=config_class.FRONTEND_FOLDER, static_url_path='')
    app.config.from_object(config_class)
    app.config['MAX_CONTENT_LENGTH'] = config_class.MAX_CONTENT_LENGTH
    CORS(app)
    register_routes(app)
    return app

def register_routes(app):
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/process', methods=['POST'])
    def process_email():
        try:
            text = extract_input_text(request)
            result = generate_result(text)
            return jsonify(result)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            print(f"Error in process_email: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

    @app.route('/<path:path>', methods=['GET'])
    def static_proxy(path):
        try:
            return send_from_directory(app.static_folder, path)
        except FileNotFoundError:
            return jsonify({'error': 'Arquivo não encontrado'}), 404

if __name__ == '__main__':
    app = create_app()
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    print(f"Upload folder: {Config.UPLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=5000)