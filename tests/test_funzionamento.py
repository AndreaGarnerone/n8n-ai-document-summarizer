import requests

# Subir documento
with open('data/input/documento.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5678/webhook/generar-resumen',
        files=files
    )

print(response.json())