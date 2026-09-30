import json
import os
import requests

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)
# Asegúrate de que el nombre coincida con el modelo que descargaste en consola
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def procesar_mensaje_ollama(texto_usuario):
    system_prompt = (
        "Clasifica el mensaje del usuario en exactamente una categoría: "
        "Finanzas, Auto o Calendario. Responde únicamente con un objeto JSON "
        'válido que contenga las llaves "modulo", "accion" y "datos". '
        "Regla de Dinero: Si el usuario menciona 'lucas', multiplica por 1000. "
        "Si no especifica unidad, asume Pesos Chilenos (CLP). "
        "Regla de Fechas: Para eventos de calendario, usa SIEMPRE el formato "
        "ISO 8601 (ej: 2026-10-02T20:00:00). "
        "No incluyas Markdown ni texto adicional."
    )
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": texto_usuario,
        "stream": False,
        "format": "json",
    }

    try:
        # Aumentamos a 120 segundos para el "cold start" del modelo local
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        contenido = response.json().get("response", "")
    except requests.RequestException as exc:
        raise RuntimeError("No fue posible comunicarse con Ollama.") from exc
    except ValueError as exc:
        raise ValueError("Ollama devolvió una respuesta HTTP inválida.") from exc

    if not contenido:
        raise ValueError("Ollama no devolvió contenido.")

    try:
        resultado = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ollama no devolvió un JSON válido. Respuesta: {contenido}") from exc

    if not isinstance(resultado, dict):
        raise ValueError("La respuesta de Ollama debe ser un objeto JSON.")
    
    # Sanitizamos el nombre del módulo (ej: "finanzas" -> "Finanzas")
    modulo_extraido = str(resultado.get("modulo", "")).capitalize()
    
    if modulo_extraido not in {"Finanzas", "Auto", "Calendario"}:
        raise ValueError(f"La respuesta contiene un módulo no válido: {modulo_extraido}")
    
    if not isinstance(resultado.get("accion"), str) or not resultado["accion"]:
        raise ValueError("La respuesta no contiene una acción válida.")

    # Reasignamos para asegurar consistencia
    resultado["modulo"] = modulo_extraido

    return resultado