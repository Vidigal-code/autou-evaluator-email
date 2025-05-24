import os
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src.classifier import classify_email
from src.responder import generate_response
from src.utils import extract_text_from_file, clean_text


# ---------------------- CONFIG ----------------------
class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    FRONTEND_FOLDER = os.path.join(BASE_DIR, '..', 'frontend')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB


# ------------------ FILE HANDLING -------------------
class FileService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def save(file_storage):
        filename = secure_filename(file_storage.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_storage.save(file_path)
        return file_path

    @staticmethod
    def extract_text(file_storage):
        if not FileService.allowed_file(file_storage.filename):
            raise ValueError("Arquivo não suportado. Use apenas PDF ou TXT.")

        file_path = FileService.save(file_storage)
        try:
            text = extract_text_from_file(file_path)
        finally:
            try:
                os.remove(file_path)
            except OSError:
                pass

        if not text or not text.strip():
            raise ValueError("O arquivo está vazio ou ilegível.")

        return text


# ------------------ PROCESSING SERVICE -------------------
class EmailProcessor:
    @staticmethod
    def get_text_from_request(req):
        if 'file' in req.files and req.files['file'].filename != '':
            return FileService.extract_text(req.files['file'])

        text = req.form.get('text') or (req.json.get('text') if req.is_json else None)
        if not text or not text.strip():
            raise ValueError('Nenhum texto ou arquivo válido enviado.')
        return text

    @staticmethod
    def process(text):
        if not text or not text.strip():
            raise ValueError('Texto vazio ou arquivo sem conteúdo.')

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


# ------------------ FLASK APP FACTORY -------------------
def create_app(config_class=Config):
    app = Flask(__name__, static_folder=config_class.FRONTEND_FOLDER, static_url_path='')
    app.config.from_object(config_class)
    app.config['MAX_CONTENT_LENGTH'] = config_class.MAX_CONTENT_LENGTH
    CORS(app)
    register_routes(app)
    return app


# ------------------ ROUTES -------------------
def register_routes(app):
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/process', methods=['POST'])
    def process_email():
        try:
            text = EmailProcessor.get_text_from_request(request)
            result = EmailProcessor.process(text)
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


# ------------------ MAIN -------------------
if __name__ == '__main__':
    app = create_app()
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    print(f"Upload folder: {Config.UPLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=5000)
