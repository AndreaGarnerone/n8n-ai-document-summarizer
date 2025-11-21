#!/usr/bin/env python3
"""
Script para demo automática del sistema
Ejecutar: python demo_automatica.py
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuración
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/generar-resumen"
API_URL = "http://localhost:8000"

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(step, message):
    """Imprime un paso de la demo"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[PASO {step}]{Colors.END} {message}")
    print("=" * 60)

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN} {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED} {message}{Colors.END}")

def print_info(message):
    """Imprime información"""
    print(f"{Colors.YELLOW}ℹ  {message}{Colors.END}")

def create_test_document():
    """Crea documento de prueba si no existe"""
    test_file = Path("data/input/demo-test.txt")
    
    if test_file.exists():
        print_info(f"Usando documento existente: {test_file}")
        return str(test_file)
    
    content = """
INFORME EJECUTIVO: TRANSFORMACIÓN DIGITAL 2024

RESUMEN DE SITUACIÓN ACTUAL

La empresa ha completado el primer año de transformación digital con resultados 
mixtos pero prometedores. La inversión total fue de $2.5 millones, distribuidos 
en infraestructura cloud (45%), desarrollo de software (30%), capacitación (15%) 
y consultoría (10%).

LOGROS PRINCIPALES

1. Migración a Cloud: Se completó la migración de 85% de los sistemas legacy 
   a AWS, resultando en una reducción del 40% en costos de infraestructura.

2. Automatización de Procesos: Se implementaron 12 workflows automatizados 
   usando n8n, ahorrando aproximadamente 120 horas/semana de trabajo manual.

3. Adopción de IA: Se integraron 3 modelos de IA en producción:
   - Chatbot de soporte: Resuelve el 65% de tickets nivel 1
   - Análisis predictivo: Mejora forecasting en 28%
   - Procesamiento de documentos: Reduce tiempo de revisión en 75%

MÉTRICAS DE RENDIMIENTO

- Disponibilidad de sistemas: 99.7% (objetivo: 99.5%)
- Tiempo de respuesta promedio: -45% vs 2023
- Satisfacción de usuarios internos: 8.2/10
- ROI proyectado a 3 años: 185%
- Reducción de costos operativos: $450,000 anuales

DESAFÍOS IDENTIFICADOS

1. Resistencia al cambio: 30% del personal requiere capacitación adicional
2. Integración de sistemas: 4 aplicaciones legacy pendientes de migrar
3. Seguridad: Se detectaron 12 vulnerabilidades (11 resueltas, 1 en proceso)
4. Presupuesto: Se excedió en 8% respecto al plan original

RECOMENDACIONES PARA 2025

1. PRIORIDAD ALTA - Capacitación continua:
   - Implementar programa de upskilling trimestral
   - Crear centro de excelencia en IA
   - Inversión recomendada: $180,000

2. PRIORIDAD MEDIA - Consolidación tecnológica:
   - Completar migración de sistemas legacy restantes
   - Estandarizar stack tecnológico
   - Timeline: Q1-Q2 2025

3. PRIORIDAD MEDIA - Expansión de automatización:
   - Identificar 20 procesos adicionales para automatizar
   - Objetivo: Ahorrar 200 horas/semana adicionales
   - Inversión: $120,000

4. PRIORIDAD BAJA - Innovación experimental:
   - Explorar blockchain para trazabilidad
   - Probar modelos de IA generativa avanzados
   - Budget: $50,000

PROYECCIÓN FINANCIERA 2025

- Inversión planeada: $1.8M
- Ahorros esperados: $680K
- ROI esperado: 38% anual
- Breakeven: Mes 18 del programa

CONCLUSIÓN

La transformación digital ha demostrado ser una inversión acertada con resultados 
tangibles en eficiencia y reducción de costos. Se recomienda continuar con el 
plan propuesto, enfocando esfuerzos en capacitación y consolidación tecnológica.

El equipo directivo debe priorizar la gestión del cambio organizacional, que 
emerge como el principal factor de riesgo para el éxito continuo del programa.

---
Preparado por: Departamento de Transformación Digital
Fecha: Enero 2025
Confidencial - Uso Interno
"""
    
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(content)
    print_success(f"Documento de prueba creado: {test_file}")
    
    return str(test_file)

def test_api_health():
    """Verifica que la API esté funcionando"""
    print_step(1, "Verificando servicios del sistema...")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("API de procesamiento está funcionando")
            print_info(json.dumps(response.json(), indent=2))
            return True
        else:
            print_error(f"API retornó código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se pudo conectar a la API: {e}")
        print_info("¿Está Docker corriendo? Ejecuta: docker-compose up -d")
        return False

def extract_text(filepath):
    """Extrae texto del documento"""
    print_step(2, f"Extrayendo texto del documento: {filepath}")
    
    try:
        payload = {"filepath": f"/{filepath}"}
        response = requests.post(
            f"{API_URL}/process-path",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Texto extraído exitosamente")
                print_info(f" Palabras: {result['word_count']}")
                print_info(f" Caracteres: {result['char_count']}")
                print_info(f" Tipo: {result['file_type']}")
                
                # Mostrar preview del texto
                preview = result['text'][:300] + "..." if len(result['text']) > 300 else result['text']
                print(f"\n{Colors.YELLOW}Preview del texto:{Colors.END}")
                print("-" * 60)
                print(preview)
                print("-" * 60)
                
                return result
            else:
                print_error(f"Error en extracción: {result.get('error')}")
                return None
        else:
            print_error(f"Error HTTP {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error en la petición: {e}")
        return None

def generate_summary(filepath):
    """Genera resumen usando el workflow completo"""
    print_step(3, "Generando resumen ejecutivo con IA...")
    print_info("Esto puede tomar 10-30 segundos...")
    
    try:
        start_time = time.time()
        
        # Llamar al webhook de n8n
        payload = {"filepath": f"/{filepath}"}
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print_success(f"Resumen generado en {elapsed_time:.2f} segundos")
            
            # Mostrar metadata
            if 'metadata' in result:
                metadata = result['metadata']
                print(f"\n{Colors.BOLD}Metadata:{Colors.END}")
                print(f"   Modelo: {metadata.get('modelo_ia', 'N/A')}")
                print(f"   Fecha: {metadata.get('fecha_generacion', 'N/A')}")
                if 'tokens_usados' in metadata:
                    tokens = metadata['tokens_usados']
                    print(f"  🔢 Tokens: {tokens.get('total_tokens', 'N/A')}")
            
            # Mostrar resumen
            if 'resumen_ejecutivo' in result:
                print(f"\n{Colors.BOLD}{Colors.GREEN}RESUMEN EJECUTIVO GENERADO:{Colors.END}")
                print("=" * 60)
                print(result['resumen_ejecutivo'])
                print("=" * 60)
            
            return result
        else:
            print_error(f"Error HTTP {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.Timeout:
        print_error("Timeout: La solicitud tardó demasiado")
        print_info("Puede ser que GitHub Models esté lento. Intenta de nuevo.")
        return None
    except requests.exceptions.RequestException as e:
        print_error(f"Error en la petición: {e}")
        return None

def check_output():
    """Verifica archivos de output generados"""
    print_step(4, "Verificando archivos generados...")
    
    output_dir = Path("data/output")
    if not output_dir.exists():
        print_error("Carpeta de output no existe")
        return False
    
    md_files = list(output_dir.glob("resumen-*.md"))
    
    if md_files:
        print_success(f"Se encontraron {len(md_files)} archivo(s) de resumen")
        
        # Mostrar el más reciente
        latest = max(md_files, key=lambda p: p.stat().st_mtime)
        print_info(f"Archivo más reciente: {latest.name}")
        
        print(f"\n{Colors.YELLOW}Contenido:{Colors.END}")
        print("-" * 60)
        print(latest.read_text()[:500] + "...")
        print("-" * 60)
        
        return True
    else:
        print_error("No se encontraron archivos de resumen")
        return False

def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print(" DEMO AUTOMÁTICA - GENERADOR DE RESÚMENES EJECUTIVOS")
    print("=" * 60)
    print(Colors.END)
    
    # Test de salud
    if not test_api_health():
        print_error("\n El sistema no está disponible")
        sys.exit(1)
    
    # Crear documento de prueba
    test_file = create_test_document()
    
    time.sleep(1)
    
    # Extraer texto
    extract_result = extract_text(test_file)
    if not extract_result:
        print_error("\n Falló la extracción de texto")
        sys.exit(1)
    
    time.sleep(1)
    
    # Generar resumen
    summary_result = generate_summary(test_file)
    if not summary_result:
        print_error("\n Falló la generación del resumen")
        print_info("Verifica que:")
        print_info("  1. n8n esté corriendo y el workflow activado")
        print_info("  2. La credencial de GitHub Models esté configurada")
        print_info("  3. El token de GitHub sea válido")
        sys.exit(1)
    
    time.sleep(1)
    
    # Verificar outputs
    check_output()
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("=" * 60)
    print("  DEMO COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print(Colors.END)
    
    print(f"\n{Colors.YELLOW} Próximos pasos:{Colors.END}")
    print("  1. Revisa el resumen generado en data/output/")
    print("  2. Prueba con tus propios documentos PDF o DOCX")
    print("  3. Ajusta el prompt en n8n si quieres cambiar el estilo")
    print("  4. Practica la demo para tu presentación")
    
    print(f"\n{Colors.GREEN} ¡El sistema está listo para la presentación final!{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrumpida por el usuario{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)