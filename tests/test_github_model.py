"""
Script para probar GitHub Models API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
API_URL = "https://models.inference.ai.azure.com/chat/completions"

def test_github_models(text_sample):
    """
    Prueba la API de GitHub Models con un texto de ejemplo
    
    Args:
        text_sample: Texto para resumir
        
    Returns:
        str: Resumen generado
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    
    # Prompt para resumen ejecutivo
    prompt = f"""Eres un experto en crear resúmenes ejecutivos profesionales.

Analiza el siguiente texto y crea un resumen ejecutivo estructurado en español que incluya:

1. **Contexto**: Breve descripción del tema principal
2. **Puntos Clave**: Los 3-5 puntos más importantes (usa viñetas)
3. **Datos Relevantes**: Métricas, números o estadísticas importantes
4. **Conclusiones**: Principales hallazgos o recomendaciones

El resumen debe ser conciso (máximo 400 palabras) y mantener un tono profesional.

TEXTO A RESUMIR:
{text_sample}

RESUMEN EJECUTIVO:"""

    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        summary = result['choices'][0]['message']['content']
        
        return {
            'success': True,
            'summary': summary,
            'model': result.get('model', 'unknown'),
            'tokens_used': result.get('usage', {})
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_summary(text, summary_type="ejecutivo"):
    """
    Genera resumen usando GitHub Models
    
    Args:
        text: Texto completo a resumir
        summary_type: Tipo de resumen (ejecutivo, técnico, académico)
        
    Returns:
        dict: Resultado con resumen generado
    """
    
    # Prompts según tipo de resumen
    prompts = {
        "ejecutivo": """Crea un RESUMEN EJECUTIVO profesional con:
- Contexto y situación actual
- 3-5 puntos clave más importantes
- Datos y métricas relevantes
- Conclusiones y recomendaciones
Máximo 400 palabras, tono profesional.""",

        "técnico": """Crea un RESUMEN TÉCNICO con:
- Objetivo del documento
- Metodología o enfoque técnico
- Resultados principales
- Implicaciones técnicas
Máximo 400 palabras, tono técnico.""",

        "académico": """Crea un RESUMEN ACADÉMICO con:
- Objetivos de la investigación
- Metodología empleada
- Resultados principales
- Conclusiones e implicaciones
Máximo 400 palabras, tono académico."""
    }
    
    base_prompt = prompts.get(summary_type, prompts["ejecutivo"])
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    
    full_prompt = f"""{base_prompt}

TEXTO A RESUMIR:
{text[:4000]}  # Limitar para no exceder tokens

RESUMEN:"""

    payload = {
        "messages": [{"role": "user", "content": full_prompt}],
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return {
            'success': True,
            'summary': result['choices'][0]['message']['content'],
            'type': summary_type,
            'tokens_used': result.get('usage', {})
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Texto de prueba
    test_text = """
    La inteligencia artificial (IA) está transformando radicalmente el sector 
    empresarial. Según el último informe de McKinsey, el 72% de las empresas 
    Fortune 500 ya implementaron soluciones de IA en al menos un área de negocio.
    
    Los principales beneficios reportados incluyen: reducción de costos operativos 
    del 30%, mejora en la precisión de predicciones del 45%, y aumento en la 
    satisfacción del cliente del 28%.
    
    Sin embargo, existen desafíos significativos. El 63% de las empresas reportan 
    dificultades para encontrar talento especializado. La inversión promedio en 
    proyectos de IA es de $2.5 millones anuales.
    
    Las recomendaciones principales son: invertir en capacitación del personal, 
    comenzar con proyectos piloto pequeños, y establecer equipos multidisciplinarios.
    """
    
    print(" Probando GitHub Models API...\n")
    
    result = test_github_models(test_text)
    
    if result['success']:
        print(" Conexión exitosa!")
        print(f" Modelo: {result['model']}")
        print(f" Tokens usados: {result['tokens_used']}")
        print("\n" + "="*60)
        print("RESUMEN GENERADO:")
        print("="*60)
        print(result['summary'])
    else:
        print(f" Error: {result['error']}")