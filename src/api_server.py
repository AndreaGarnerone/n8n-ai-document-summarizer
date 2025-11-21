"""
API Server para procesar archivos
Expone endpoints para que n8n pueda llamar
"""
from flask import Flask, request, jsonify
import os
import sys
from werkzeug.utils import secure_filename

# Agregar path para imports
sys.path.append('/app')
from processors.file_processor import FileProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max
app.config['UPLOAD_FOLDER'] = '/data/input'
app.config['OUTPUT_FOLDER'] = '/data/output'

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

processor = FileProcessor()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PDF Processor API',
        'version': '1.0.0'
    })


@app.route('/process', methods=['POST'])
def process_file():
    """
    Procesa un archivo y extrae el texto
    
    Expected: file in multipart/form-data
    Returns: JSON con texto extraído
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Empty filename'
        }), 400
    
    try:
        # Guardar archivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Procesar
        result = processor.process_file(filepath)
        
        # Agregar estadísticas
        if result['success']:
            stats = processor.get_document_stats(result['text'])
            result['stats'] = stats
        
        # Limpiar archivo temporal (opcional)
        # os.remove(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/process-path', methods=['POST'])
def process_file_by_path():
    """
    Procesa un archivo por su ruta
    
    Expected JSON: { "filepath": "/path/to/file" }
    Returns: JSON con texto extraído
    """
    data = request.get_json()
    
    if not data or 'filepath' not in data:
        return jsonify({
            'success': False,
            'error': 'filepath not provided'
        }), 400
    
    filepath = data['filepath']
    
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': f'File not found: {filepath}'
        }), 404
    
    try:
        result = processor.process_file(filepath)
        
        if result['success']:
            stats = processor.get_document_stats(result['text'])
            result['stats'] = stats
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/supported-formats', methods=['GET'])
def supported_formats():
    """Retorna los formatos soportados"""
    return jsonify({
        'formats': processor.supported_formats,
        'description': {
            '.pdf': 'Portable Document Format',
            '.docx': 'Microsoft Word Document',
            '.txt': 'Plain Text File',
            '.doc': 'Microsoft Word Document (Legacy)'
        }
    })


if __name__ == '__main__':
    print(" Starting PDF Processor API...")
    print(f" Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f" Output folder: {app.config['OUTPUT_FOLDER']}")
    app.run(host='0.0.0.0', port=8000, debug=True)