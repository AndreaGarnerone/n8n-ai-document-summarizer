"""
Procesador de archivos para extraer texto de PDFs, DOCX y TXT
"""
import os
import pdfplumber
from PyPDF2 import PdfReader
from docx import Document
import pytesseract
from PIL import Image
import io
import re


class FileProcessor:
    """Clase para procesar diferentes tipos de archivos"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.doc']
    
    def detect_file_type(self, filepath):
        """Detecta el tipo de archivo"""
        _, ext = os.path.splitext(filepath)
        return ext.lower()
    
    def process_file(self, filepath):
        """
        Procesa un archivo y extrae el texto
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            dict: {
                'text': str,
                'word_count': int,
                'file_type': str,
                'success': bool,
                'error': str (si hay error)
            }
        """
        try:
            file_type = self.detect_file_type(filepath)
            
            if file_type == '.pdf':
                text = self._process_pdf(filepath)
            elif file_type in ['.docx', '.doc']:
                text = self._process_docx(filepath)
            elif file_type == '.txt':
                text = self._process_txt(filepath)
            else:
                return {
                    'success': False,
                    'error': f'Formato no soportado: {file_type}'
                }
            
            # Limpiar texto
            text = self._clean_text(text)
            
            return {
                'success': True,
                'text': text,
                'word_count': len(text.split()),
                'file_type': file_type,
                'char_count': len(text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_pdf(self, filepath):
        """Extrae texto de PDF"""
        text = ""
        
        try:
            # Intento 1: pdfplumber (mejor para PDFs con texto)
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Si no se extrajo texto, intentar con PyPDF2
            if not text.strip():
                reader = PdfReader(filepath)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
        except Exception as e:
            print(f"Error procesando PDF: {e}")
            text = f"Error: {str(e)}"
        
        return text
    
    def _process_docx(self, filepath):
        """Extrae texto de DOCX"""
        try:
            doc = Document(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            return f"Error procesando DOCX: {str(e)}"
    
    def _process_txt(self, filepath):
        """Lee archivo de texto plano"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Intentar con otra codificación
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _clean_text(self, text):
        """Limpia y normaliza el texto extraído"""
        # Eliminar múltiples espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar múltiples saltos de línea
        text = re.sub(r'\n+', '\n', text)
        
        # Eliminar espacios al inicio y final
        text = text.strip()
        
        return text
    
    def get_document_stats(self, text):
        """Obtiene estadísticas del documento"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'char_count': len(text),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1)
        }


# Función standalone para usar desde n8n
def extract_text_from_file(filepath):
    """
    Función simple para extraer texto de un archivo
    
    Args:
        filepath: Ruta al archivo
        
    Returns:
        str: Texto extraído
    """
    processor = FileProcessor()
    result = processor.process_file(filepath)
    
    if result['success']:
        return result['text']
    else:
        raise Exception(result['error'])


if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        processor = FileProcessor()
        result = processor.process_file(filepath)
        
        if result['success']:
            print(f" Texto extraído exitosamente")
            print(f" Palabras: {result['word_count']}")
            print(f" Tipo: {result['file_type']}")
            print("\n" + "="*50)
            print(result['text'][:500] + "...")
        else:
            print(f" Error: {result['error']}")
    else:
        print("Uso: python file_processor.py <ruta_archivo>")