#!/bin/bash

# Script de testing completo para el sistema
# Ejecutar: chmod +x test_sistema.sh && ./test_sistema.sh

echo " Iniciando Tests del Sistema de Resúmenes..."
echo "================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de tests
TESTS_PASSED=0
TESTS_FAILED=0

# Función para test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing: $test_name ... "
    
    if eval $test_command > /dev/null 2>&1; then
        echo -e "${GREEN} PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED} FAIL${NC}"
        ((TESTS_FAILED++))
    fi
}

# TEST 1: Docker está corriendo
echo " TEST 1: Docker"
run_test "Docker daemon" "docker info"
run_test "Docker Compose" "docker-compose --version"

# TEST 2: Servicios levantados
echo ""
echo " TEST 2: Servicios"
run_test "n8n container" "docker ps | grep n8n-resumenes"
run_test "pdf-processor container" "docker ps | grep pdf-processor"

# TEST 3: Health checks
echo ""
echo " TEST 3: Health Checks"
run_test "n8n health" "curl -s http://localhost:5678/healthz"
run_test "PDF processor health" "curl -s http://localhost:8000/health | grep healthy"

# TEST 4: Estructura de archivos
echo ""
echo " TEST 4: Estructura de Archivos"
run_test "docker-compose.yml exists" "test -f docker-compose.yml"
run_test "src/api_server.py exists" "test -f src/api_server.py"
run_test "src/processors/file_processor.py exists" "test -f src/processors/file_processor.py"
run_test "data/input/ exists" "test -d data/input"
run_test "data/output/ exists" "test -d data/output"

# TEST 5: Crear y procesar documento de prueba
echo ""
echo " TEST 5: Procesamiento de Documento"

# Crear documento de prueba
TEST_FILE="data/input/test-auto.txt"
cat > $TEST_FILE << 'EOF'
INFORME DE PRUEBA AUTOMATIZADO

Este es un documento de prueba para validar el sistema de resúmenes.
El sistema debe ser capaz de:
1. Extraer este texto correctamente
2. Enviarlo a la IA para análisis
3. Generar un resumen estructurado
4. Guardar el resultado en formato Markdown

Métricas de prueba:
- Palabras: 50
- Caracteres: 250
- Fecha: 2025-01-20
EOF

run_test "Documento de prueba creado" "test -f $TEST_FILE"

# Test de extracción de texto
echo -n "Testing: Extracción de texto ... "
EXTRACT_RESULT=$(curl -s -X POST http://localhost:8000/process-path \
  -H "Content-Type: application/json" \
  -d "{\"filepath\": \"/data/input/test-auto.txt\"}")

if echo $EXTRACT_RESULT | grep -q "success.*true"; then
    echo -e "${GREEN} PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED} FAIL${NC}"
    echo "Response: $EXTRACT_RESULT"
    ((TESTS_FAILED++))
fi

# TEST 6: GitHub Models (requiere token válido)
echo ""
echo " TEST 6: GitHub Models"
echo -n "Testing: Conexión a GitHub Models ... "

if [ -f ".env" ] && grep -q "GITHUB_TOKEN" .env; then
    source .env
    if [ ! -z "$GITHUB_TOKEN" ] && [ "$GITHUB_TOKEN" != "ghp_tu_token_aqui" ]; then
        TEST_RESPONSE=$(curl -s -X POST https://models.inference.ai.azure.com/chat/completions \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $GITHUB_TOKEN" \
          -d '{
            "messages": [{"role": "user", "content": "Test"}],
            "model": "gpt-4o",
            "max_tokens": 10
          }')
        
        if echo $TEST_RESPONSE | grep -q "choices"; then
            echo -e "${GREEN} PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED} FAIL${NC}"
            echo "GitHub Models no responde correctamente"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${YELLOW}  SKIP (Token no configurado)${NC}"
    fi
else
    echo -e "${YELLOW}  SKIP (Archivo .env no encontrado)${NC}"
fi

# TEST 7: Verificar logs
echo ""
echo " TEST 7: Logs"
run_test "n8n logs accesibles" "docker logs n8n-resumenes --tail 10"
run_test "pdf-processor logs accesibles" "docker logs pdf-processor --tail 10"

# Resumen
echo ""
echo "================================================"
echo " RESUMEN DE TESTS"
echo "================================================"
echo -e "Tests Pasados: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Fallados: ${RED}$TESTS_FAILED${NC}"
TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo "Total Tests: $TOTAL_TESTS"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN} ¡TODOS LOS TESTS PASARON!${NC}"
    echo -e "${GREEN}El sistema está listo para la demo.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}  Algunos tests fallaron.${NC}"
    echo "Revisa los errores arriba y corrige antes de la demo."
    exit 1
fi