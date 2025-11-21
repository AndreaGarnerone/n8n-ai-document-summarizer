# 📦 Guía de Instalación Completa

## Pre-requisitos

### 1. Docker Desktop

#### Windows
```bash
# Descargar desde:
https://www.docker.com/products/docker-desktop

# Verificar instalación
docker --version
docker-compose --version
```

#### Mac
```bash
# Con Homebrew
brew install --cask docker

# O descargar desde:
https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Git

```bash
# Verificar que Git está instalado
git --version

# Si no está instalado:
# Windows: https://git-scm.com/download/win
# Mac: brew install git
# Linux: sudo apt-get install git
```

### 3. Token de GitHub

1. Ve a: https://github.com/settings/tokens
2. Click: **Generate new token (classic)**
3. Nombre: `n8n-resumenes`
4. Permisos mínimos:
   -  `repo` (full control)
   -  `read:user`
5. **Copiar el token** (no lo perderás después)

---

## Instalación Paso a Paso

### PASO 1: Clonar Proyecto

```bash
# Crear carpeta de proyectos
mkdir ~/proyectos-ia
cd ~/proyectos-ia

# Si tienes el repo en GitHub
git clone https://github.com/tu-usuario/generador-resumenes-ia.git
cd generador-resumenes-ia

# Si no tienes repo, crear desde cero
mkdir generador-resumenes-ia
cd generador-resumenes-ia
git init
```

### PASO 2: Crear Estructura

```bash
# Crear todas las carpetas necesarias
mkdir -p n8n/{workflows,credentials}
mkdir -p src/{processors,templates}
mkdir -p data/{input,output,examples}
mkdir -p docs

# Crear archivos vacíos importantes
touch data/input/.gitkeep
touch data/output/.gitkeep
touch n8n/workflows/.gitkeep
```

### PASO 3: Configurar Archivos

#### 3.1 Crear .env

```bash
# Copiar template
cp .env.example .env

# Editar con tu token
nano .env  # o vim, o code .env
```

Contenido del `.env`:
```bash
GITHUB_TOKEN=ghp_TU_TOKEN_REAL_AQUI
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
MAX_SUMMARY_LENGTH=500
SUMMARY_LANGUAGE=es
```

#### 3.2 Copiar todos los archivos del repositorio

Asegúrate de tener:
-  `docker-compose.yml`
-  `.gitignore`
-  `src/Dockerfile`
-  `src/requirements.txt`
-  `src/api_server.py`
-  `src/processors/file_processor.py`
-  `src/test_github_models.py`
-  `n8n/workflows/generador-resumenes.json`

### PASO 4: Construir y Levantar Servicios

```bash
# Construir imágenes (primera vez)
docker-compose build

# Levantar servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

**Output esperado:**
```
NAME                 STATUS         PORTS
n8n-resumenes        Up 2 minutes   0.0.0.0:5678->5678/tcp
pdf-processor        Up 2 minutes   0.0.0.0:8000->8000/tcp
```

### PASO 5: Verificar Servicios

#### 5.1 Verificar n8n

```bash
# Abrir en navegador
open http://localhost:5678

# O con curl
curl http://localhost:5678/healthz
```

#### 5.2 Verificar PDF Processor

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "PDF Processor API",
  "version": "1.0.0"
}
```

### PASO 6: Configurar n8n

#### 6.1 Primera Configuración

1. Abrir: http://localhost:5678
2. Verás login básico:
   - User: `admin`
   - Password: `admin123`

#### 6.2 Importar Workflow

1. Click en menú hamburguesa (☰) arriba izquierda
2. **Workflows** → Click botón "+"
3. Click "..." → **Import from File**
4. Seleccionar: `n8n/workflows/generador-resumenes.json`
5. Click **Import**

#### 6.3 Configurar Credencial GitHub Models

1. En el workflow, click en nodo **"Generar Resumen con IA"**
2. En el panel derecho, buscar sección **"Authentication"**
3. Click en dropdown → **Create New Credential**
4. Seleccionar: **HTTP Header Auth**
5. Llenar campos:
   - **Credential Name**: `GitHub Models API`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer TU_GITHUB_TOKEN`
   
    **IMPORTANTE**: Debes poner `Bearer ` seguido de tu token
   
   Ejemplo: `Bearer ghp_abc123xyz456`

6. Click **Save**
7. Seleccionar la credencial recién creada en el nodo

#### 6.4 Activar Workflow

1. En la esquina superior derecha, activar el toggle **"Active"**
2. Debe cambiar a color verde
3. Verificar que aparece URL del webhook

### PASO 7: Probar el Sistema

#### Test 1: Crear Documento de Prueba

```bash
# Crear un documento TXT simple
cat > data/input/test.txt << 'EOF'
Informe Ejecutivo de Ventas Q4 2024

Las ventas del cuarto trimestre alcanzaron los $5.2 millones, 
representando un crecimiento del 23% comparado con Q4 2023.

Destacados principales:
- Nuevos clientes: 45 empresas
- Tasa de retención: 94%
- Ingreso por cliente promedio: $115,000
- Satisfacción del cliente: 4.8/5.0

Recomendaciones:
1. Expandir equipo de ventas en 30%
2. Invertir en automatización de CRM
3. Lanzar programa de referidos en Q1 2025

El equipo de ventas superó las metas establecidas, y la proyección 
para 2025 es de $25 millones en ingresos totales.
EOF
```

#### Test 2: Procesar con API Directa

```bash
# Probar extracción de texto
curl -X POST http://localhost:8000/process-path \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/data/input/test.txt"}' \
  | jq .
```

**Respuesta esperada:**
```json
{
  "success": true,
  "text": "Informe Ejecutivo de Ventas...",
  "word_count": 87,
  "file_type": ".txt",
  "stats": {
    "word_count": 87,
    "sentence_count": 12,
    "paragraph_count": 4
  }
}
```

#### Test 3: Workflow Completo (con IA)

```bash
# Copiar la URL del webhook desde n8n
# Debería verse como: http://localhost:5678/webhook/generar-resumen

# Test con curl
curl -X POST http://localhost:5678/webhook/generar-resumen \
  -F "filepath=/data/input/test.txt"
```

**Si funciona, deberías ver:**
```json
{
  "success": true,
  "resumen_ejecutivo": "# Resumen Ejecutivo...",
  "metadata": {
    "fecha_generacion": "2025-01-20T...",
    "modelo_ia": "gpt-4o"
  }
}
```

### PASO 8: Verificar Output

```bash
# Ver archivos generados
ls -la data/output/

# Leer último resumen
cat data/output/resumen-*.md
```

---

##  Verificación Completa

### Checklist de Instalación

- [ ] Docker Desktop corriendo
- [ ] `docker-compose ps` muestra 2 servicios UP
- [ ] http://localhost:5678 carga n8n
- [ ] http://localhost:8000/health retorna 200
- [ ] Workflow importado en n8n
- [ ] Credencial GitHub configurada
- [ ] Workflow activado (toggle verde)
- [ ] Test con documento TXT funciona
- [ ] Se genera archivo en `data/output/`

### Si TODO está 

¡Felicitaciones! Tu sistema está funcionando.

**Próximos pasos:**
1. Probar con un PDF real
2. Ajustar prompt de IA si es necesario
3. Preparar documentación para demo
4. Practicar presentación

---

## 🐛 Solución de Problemas Comunes

### Problema 1: Docker no inicia

```bash
# Ver logs
docker-compose logs

# Reiniciar Docker Desktop
# Windows/Mac: Abrir Docker Desktop → Click icono → Restart

# Limpiar y reiniciar
docker-compose down
docker-compose up -d
```

### Problema 2: n8n muestra "Connection refused"

```bash
# Ver logs específicos
docker-compose logs n8n

# Verificar puerto
netstat -an | grep 5678

# Reiniciar solo n8n
docker-compose restart n8n
```

### Problema 3: PDF Processor no responde

```bash
# Ver logs
docker-compose logs pdf-processor

# Entrar al contenedor
docker exec -it pdf-processor bash

# Instalar dependencias manualmente
pip install -r /app/requirements.txt
```

### Problema 4: GitHub Models retorna 401

```bash
# Verificar token
echo $GITHUB_TOKEN

# Re-generar token en GitHub
# Actualizar .env
# Reiniciar n8n
docker-compose restart n8n
```

### Problema 5: "Module not found" en Python

```bash
# Reconstruir imagen
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problema 6: Workflow no se activa

1. Verificar que credencial está configurada
2. Hacer click en "Execute Workflow" para testear
3. Revisar logs en n8n (panel inferior)
4. Verificar URL del webhook

---

##  Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo de n8n
docker-compose logs -f n8n

# Reiniciar todo
docker-compose restart

# Detener todo
docker-compose down

# Limpiar volúmenes ( borra datos)
docker-compose down -v

# Ver uso de recursos
docker stats

# Entrar a contenedor
docker exec -it n8n-resumenes sh
docker exec -it pdf-processor bash

# Backup del volumen de n8n
docker run --rm -v generador-resumenes-ia_n8n_data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/n8n-backup.tar.gz -C /data .
```

---

##  Optimizaciones Opcionales

### Aumentar Memoria de Docker

**Windows/Mac:**
1. Docker Desktop → Settings → Resources
2. Memory: 4 GB → 6 GB
3. Apply & Restart

### Configurar Dominio Local

```bash
# Agregar a /etc/hosts (Mac/Linux) o C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 n8n.local
127.0.0.1 api.local

# Acceder con:
http://n8n.local:5678
http://api.local:8000
```

### Habilitar HTTPS (Producción)

Ver: `docs/https-setup.md` (crear después si es necesario)

---

##  Instalación Completa

Si llegaste aquí y todo funciona: **¡Excelente trabajo!** 🎉

Tu sistema está listo para:
- Procesar documentos
- Generar resúmenes con IA
- Demostrar en la presentación final

**Siguiente paso**: Practicar la demo y preparar documentos de prueba interesantes.