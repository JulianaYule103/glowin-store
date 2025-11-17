import os
import json
import openai
from .models import Producto

openai.api_key = os.getenv("OPENAI_API_KEY")

# Mientras estás en local:
URL_BASE = "http://127.0.0.1:8000"
# Cuando publiques tu página, cambias a algo como:
# URL_BASE = "https://tudominio.com"


def _build_catalogo():
    """
    Convierte tus productos de la BD en un catálogo pequeño en JSON
    para que la IA pueda elegir uno.
    Incluimos categoría para que entienda si es ropa, maquillaje, etc.
    """
    catalogo = []
    for p in Producto.objects.all():
        catalogo.append({
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": (p.descripcion or "")[:400],
            "categoria": getattr(getattr(p, "categoria", None), "nombre", ""),
            "url": f"{URL_BASE}/productos/{p.id}/",
            "imagen": p.imagen.url if getattr(p, "imagen", None) else ""
        })
    return catalogo


def _respuesta_texto_simple(mensaje_usuario: str) -> dict:
    """
    Respuesta normal de IA sin catálogo (por si no hay productos).
    """
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres la asistente virtual de Glowin. "
                    "Ayudas a las clientas con dudas sobre cuidado de la piel, "
                    "cabello, maquillaje y ropa. Responde de forma cercana, clara "
                    "y práctica. Puedes hacer 1 o 2 preguntas si necesitas más datos."
                ),
            },
            {"role": "user", "content": mensaje_usuario},
        ],
    )

    texto = completion.choices[0].message.content

    return {
        "tipo": "texto",
        "mensaje": texto,
        "nombre": "",
        "descripcion": "",
        "imagen": "",
        "url": "",
    }


def chatbot_respuesta(mensaje_usuario: str) -> dict:
    """
    Usa IA + catálogo:
    - Si encuentra un producto adecuado → tipo = 'producto' + explicación
    - Si no, responde solo texto → tipo = 'texto'
    - Si le falta información importante, puede hacer preguntas (tipo = 'texto')
    """

    catalogo = _build_catalogo()

    # Si no tienes productos, salimos con respuesta normal
    if not catalogo:
        return _respuesta_texto_simple(mensaje_usuario)

    system_content = (
    "Eres la asistente virtual de la tienda Glowin.\n"
    "Glowin vende: productos de cuidado de la piel, cuidado capilar, maquillaje y ropa.\n\n"

    "Tu objetivo es ayudar a la clienta con recomendaciones reales del catálogo.\n"
    "Debes responder SIEMPRE de forma cálida, amable y profesional.\n\n"

    "=== FUNCIONAMIENTO GENERAL ===\n"
    "1) Lee el mensaje de la usuaria.\n"
    "2) Entiende la intención (piel, cabello, maquillaje, ropa, etc.).\n"
    "3) Usa tu conocimiento real de cosmética, cuidado personal y moda.\n"
    "4) Si el catálogo contiene productos adecuados, elige SOLO 1 (el mejor).\n"
    "5) Explica por qué lo recomiendas, en palabras sencillas.\n"
    "6) Si ningún producto del catálogo sirve, da una recomendación general.\n\n"

    "=== PREGUNTAS (MUY IMPORTANTE) ===\n"
    "• SOLO puedes hacer UNA pregunta si REALMENTE es necesaria.\n"
    "• Si la usuaria ya dijo algo como 'piel grasa', 'piel seca', 'cabello maltratado',\n"
    "  'tengo piel morena', 'quiero vestido elegante', NO preguntes de nuevo.\n"
    "• NO repitas preguntas.\n"
    "• NO entres en bucles.\n"
    "• Si hay alguna pista mínima, asume y recomienda.\n"
    "• Si aun así la información es insuficiente, haz UNA sola pregunta clara.\n\n"

    "=== FORMATO DE RESPUESTA OBLIGATORIO ===\n"
    "Debes devolver SOLO un JSON válido con este formato:\n"
    "{\n"
    '  \"tipo\": \"producto\" o \"texto\",\n'
    '  \"mensaje\": \"Texto amigable explicando o preguntando\",\n'
    '  \"nombre\": \"Nombre del producto o vacío\",\n'
    '  \"descripcion\": \"Descripción corta o vacía\",\n'
    '  \"imagen\": \"URL de imagen o vacío\",\n'
    '  \"url\": \"URL del producto o vacío\"\n'
    "}\n\n"

    "=== REGLAS DE PRODUCTOS ===\n"
    "• NO inventes productos.\n"
    "• NO cambies nombres, imágenes ni precios.\n"
    "• SOLO usa productos del catálogo.\n"
    "• Elige el más adecuado a lo que la usuaria dijo.\n"
    "• Si la usuaria pregunta algo que no es de productos (ej: rutina), usa tipo='texto'.\n\n"

    "=== CATALOGO ===\n"
    f"{json.dumps(catalogo, ensure_ascii=False)}"
)


    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": mensaje_usuario},
        ],
        temperature=0.5,
    )

    raw = completion.choices[0].message.content

    # Intentamos leer la respuesta como JSON
    try:
        data = json.loads(raw)
        return {
            "tipo": data.get("tipo", "texto"),
            "mensaje": data.get("mensaje", ""),
            "nombre": data.get("nombre", ""),
            "descripcion": data.get("descripcion", ""),
            "imagen": data.get("imagen", ""),
            "url": data.get("url", ""),
        }
    except Exception:
        # Si la IA no respetó el formato JSON, devolvemos solo texto
        return {
            "tipo": "texto",
            "mensaje": raw,
            "nombre": "",
            "descripcion": "",
            "imagen": "",
            "url": "",
        }
