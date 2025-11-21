# 📄 Generador Automático de Resúmenes Ejecutivos

Sistema inteligente que convierte documentos largos (PDF, DOCX, TXT) en resúmenes ejecutivos profesionales utilizando IA.

##  Problema que Resuelve

Leer y procesar documentos extensos (informes, contratos, investigaciones) consume mucho tiempo. Este sistema automatiza la creación de resúmenes ejecutivos de calidad, permitiendo a profesionales y ejecutivos obtener insights clave en minutos.

##  Características Principales

-  **Múltiples Formatos**: Procesa PDF, DOCX, DOC y TXT
-  **IA Avanzada**: Usa GitHub Models (GPT-4) para resúmenes contextuales
-  **Automatización**: Workflow completo en n8n sin intervención manual
-  **Containerizado**: Todo corre en Docker, fácil de desplegar
-  **Estadísticas**: Análisis de palabras, caracteres y estructura
-  **Persistencia**: Guarda resúmenes en formato Markdown

##  Arquitectura Técnica

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Usuario   │────▶│  n8n Webhook │────▶│ PDF Processor   │────▶│ Google Gemini│
│  (Upload)   │     │  (Orquesta)  │     │ (Extrae Texto)  │     │  (Resumen IA)│
└─────────────┘     └──────────────┘     └─────────────────┘     └──────────────┘
                                                                          │
                                                                          ▼
                    ┌──────────────┐                              ┌──────────────┐
                    │  Guarda MD   │◀─────────────────────────────│ Formateo     │
                    │  /data/out   │                              │ Respuesta    │
                    └──────────────┘                              └──────────────┘
```

### Componentes:

1. **n8n** (Puerto 5678): Orquestador de workflows
2. **PDF Processor API** (Puerto 8000): Servicio Python para extraer texto
3. **GitHub Models**: API de IA para generación de resúmenes. Google Gemini 2.0 flash por este proyecto.
4. **Volúmenes Docker**: Persistencia de datos y workflows

##  Instalación y Uso

### Pre-requisitos

- Docker Desktop instalado y corriendo
- Git configurado
- Token de GitHub

### Instalación Rápida

```bash
# 1. Clonar repositorio
git clone <este-repo>
cd generador-resumenes-ia

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GITHUB_TOKEN

# 3. Levantar servicios
docker-compose up -d

# 4. Verificar que están corriendo
docker-compose ps
```

### Acceder a n8n

1. Abrir navegador: http://localhost:5678
2. Crear cuenta (primera vez):
   - Email: admin@localhost
   - Password: admin123

3. Importar workflow:
   - Click en "..." → Import from File
   - Seleccionar: `n8n/workflows/generador-resumenes.json`

4. Configurar credencial de GitHub:
   - Settings → Credentials → Add Credential
   - Tipo: "HTTP Header Auth"
   - Nombre: "GitHub Models API"
   - Header Name: `Authorization`
   - Header Value: `Bearer token`

5. Activar workflow:
   - Click en el toggle "Active" en la esquina superior derecha

### Usar el Sistema

#### Opción 1: Usando cURL

```bash
# Copiar un PDF de prueba
cp tu-documento.pdf data/input/

# Llamar al webhook de n8n
curl -X POST http://localhost:5678/webhook/generar-resumen \
  -F "file=@data/input/tu-documento.pdf"
```

#### Opción 2: Usando Python

```python
import requests

# Subir documento
with open('data/input/documento.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5678/webhook/generar-resumen',
        files=files
    )

print(response.json())
```

#### Opción 3: Directamente con API

```bash
# Procesar archivo que ya está en /data/input
curl -X POST http://localhost:8000/process-path \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/data/input/documento.pdf"}'
```

##  Testing

### Probar Extracción de Texto

```bash
# Entrar al contenedor
docker exec -it pdf-processor bash

# Probar extracción
python /app/processors/file_processor.py /data/input/documento.pdf
```

### Probar GitHub Models

```bash
# Desde tu máquina
cd src
python test_github_models.py
```

### Ver Logs

```bash
# Logs de n8n
docker-compose logs -f n8n

# Logs del procesador
docker-compose logs -f pdf-processor
```

##  Estructura del Proyecto

```
generador-resumenes-ia/
├──  README.md                      # Este archivo
├──  .env                           # Variables de entorno template
├──  docker-compose.yml             # Configuración Docker
├──  .gitignore                     # Archivos ignorados
│
├──  n8n/                           # Workflows y credenciales
│   ├── workflows/
│   │   └── generador-resumenes.json # Workflow principal
│
├──  src/                           # Código fuente
│   ├── Dockerfile                   # Container Python
│   ├── requirements.txt             # Dependencias Python
│   ├── api_server.py                # API Flask
│   ├── processors/
│   │   └── file_processor.py        # Extractor de texto
│
├──  data/                          # Datos persistentes
│   ├── input/                       # Documentos a procesar
│   ├── output/                      # Resúmenes generados
│
└──  docs/                          # Documentación adicional
    | 
    └── instalacion.md               # Guía detallada
```

##  Tecnologías Utilizadas

| Tecnología | Propósito | Justificación |
|------------|-----------|---------------|
| **Docker** | Containerización | Portabilidad y fácil despliegue |
| **n8n** | Automatización | Orquestación visual de workflows |
| **GitHub Models (Google Gemini 2.0 flash)** | IA/LLM | Resúmenes contextuales de calidad |
| **Flask** | API REST | Ligero y fácil de integrar |
| **pdfplumber** | Extracción PDF | Mejor precisión en texto de PDFs |
| **python-docx** | Procesamiento DOCX | Estándar para archivos Word |

##  Variables de Entorno

```bash
# GitHub Models
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx          # Token de GitHub

# n8n
N8N_BASIC_AUTH_USER=admin              # Usuario n8n
N8N_BASIC_AUTH_PASSWORD=admin123       # Password n8n

# Configuración
MAX_SUMMARY_LENGTH=500                 # Palabras máximas
SUMMARY_LANGUAGE=es                    # Idioma (es/en)
```

##  Troubleshooting

### Problema: n8n no inicia

```bash
# Ver logs
docker-compose logs n8n

# Reiniciar servicios
docker-compose restart
```

### Problema: Error al extraer texto de PDF

```bash
# Verificar que el archivo existe
docker exec pdf-processor ls -la /data/input/

# Probar extracción manual
docker exec -it pdf-processor python /app/processors/file_processor.py /data/input/archivo.pdf
```

### Problema: GitHub Models retorna 401

- Verificar que el token es válido
- Verificar que tiene permisos necesarios
- Re-generar token si es necesario

##  Mejoras Futuras

- [ ] Interfaz web para upload de archivos
- [ ] Soporte para OCR en PDFs escaneados
- [ ] Procesamiento batch de múltiples documentos
- [ ] Diferentes estilos de resumen (ejecutivo, técnico, académico)
- [ ] Extracción de gráficos y tablas
- [ ] Traducción automática de resúmenes
- [ ] API con autenticación
- [ ] Dashboard con métricas

##  Limitaciones Conocidas

1. **Tamaño de archivo**: Máximo 50 MB por documento
2. **PDFs escaneados**: Requiere OCR adicional (no implementado)
3. **Tablas complejas**: Extracción limitada de tablas en PDFs
4. **Idiomas**: Optimizado para español, funciona en inglés
5. **Formato**: Resúmenes solo en Markdown

##  Soporte

Para problemas o preguntas:
- Crear issue en GitHub
- Revisar logs: `docker-compose logs`
- Consultar documentación de [n8n](https://docs.n8n.io/)

##  Licencia

MIT License - Proyecto académico para curso Universidad Javeriana

---

**Autor**: Andrea Garnerone