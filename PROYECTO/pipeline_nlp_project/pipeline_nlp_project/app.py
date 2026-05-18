# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import spacy
import unicodedata

app = Flask(__name__)
nlp = spacy.load("es_core_news_sm")

CORRECCIONES_POS = {
    "calamar": "NOUN"
}

STOPWORDS_ADICIONALES = {"sin", "embargo", "así", "más", "menos", "muy", "tan", "todo"}

CONECTORES_DISCURSIVOS = [
    ("ni siquiera", "ni siquiera"),
    ("sin embargo", "sin embargo"),
    ("no obstante", "no obstante"),
    ("por otra parte", "por otra parte"),
    ("así mismo", "así mismo"),
    ("por ende", "por ende"),
    ("en consecuencia", "en consecuencia"),
    ("por lo tanto", "por lo tanto")
]

def segmentar_por_conectores(texto):
    frases = []
    texto_lower = texto.lower()
    posiciones = []
    for palabra, _ in CONECTORES_DISCURSIVOS:
        idx = 0
        while True:
            pos = texto_lower.find(palabra, idx)
            if pos == -1:
                break
            if pos == 0 or not texto_lower[pos-1].isalnum():
                if pos + len(palabra) >= len(texto_lower) or not texto_lower[pos + len(palabra)].isalnum():
                    posiciones.append(pos)
                    break
            idx = pos + 1
    if posiciones:
        posiciones.sort()
        ultimo_idx = 0
        for pos in posiciones:
            if pos > ultimo_idx:
                frases.append(texto[ultimo_idx:pos].strip())
            ultimo_idx = pos
        if ultimo_idx < len(texto):
            frases.append(texto[ultimo_idx:].strip())
        frases = [f for f in frases if f.strip()]
    if not frases:
        frases = [texto]
    return frases

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto.lower()).encode('ASCII', 'ignore').decode('ASCII')

def process_nlp(text):
    doc = nlp(text)

    etapa4_pos = []
    for token in doc:
        pos_original = token.pos_
        texto_normalizado = normalizar(token.text)
        pos_corregido = CORRECCIONES_POS.get(texto_normalizado, pos_original)
        corregido = pos_corregido != pos_original
        etapa4_pos.append({
            "token": token.text,
            "pos": pos_corregido,
            "desc": spacy.explain(pos_corregido) or "",
            "corregido": corregido
        })

    stopwords_base = set(token.text.lower() for token in doc if token.is_stop)
    stopwords_total = stopwords_base | STOPWORDS_ADICIONALES

    tokens_filtrados = []
    stopwords_encontradas = []
    for token in doc:
        if token.text.lower() in stopwords_total:
            stopwords_encontradas.append(token.text)
        else:
            tokens_filtrados.append({
                "token": token.text,
                "lema": token.lemma_
            })

    result = {
        "original": text,
        "etapa1_segmentacion": [{"id": i+1, "texto": frase} for i, frase in enumerate(segmentar_por_conectores(text))],
        "etapa1_original": text,
        "etapa2_tokenizacion": [{"token": token.text, "indice": token.i + 1} for token in doc],
        "etapa3_lematizacion": [{"token": token.text, "lema": token.lemma_} for token in doc],
        "etapa4_pos": etapa4_pos,
        "etapa5_stopwords": {
            "total_tokens": len(doc),
            "stopwords_base": list(stopwords_base),
            "stopwords_adicionales": list(STOPWORDS_ADICIONALES & set(t.text.lower() for t in doc)),
            "stopwords_encontradas": stopwords_encontradas,
            "tokens_filtrados": tokens_filtrados
        }
    }
    return result

@app.route('/')
def index():
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/procesar', methods=['POST'])
def procesar():
    data = request.get_json()
    texto = data.get('texto', '')
    if not texto:
        return jsonify({"error": "Texto vacío"}), 400
    resultado = process_nlp(texto)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, port=5000)