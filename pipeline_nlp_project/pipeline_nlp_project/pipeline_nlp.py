# -*- coding: utf-8 -*-
import spacy
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

nlp = spacy.load("es_core_news_sm")

import unicodedata

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto.lower()).encode('ASCII', 'ignore').decode('ASCII')

CORRECCIONES_POS = {
    "calamar": "NOUN",
    "indignacion": "NOUN",
    "indignaci n": "NOUN",
    "indignaci": "NOUN",
    "publico": "NOUN",
    "p blico": "NOUN",
    "public": "NOUN"
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

def mostrar_separador(titulo):
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)

def etapa1_segmentacion_frases(doc):
    mostrar_separador("ETAPA 1: SEGMENTACIÓN EN FRASES")
    print("\nSegmentación basada en conectores discursivos:\n")
    texto_original = doc.text
    frases = segmentar_por_conectores(texto_original)
    for i, frase in enumerate(frases, 1):
        print(f"  Frase {i}: {frase}")
    print(f"\n  Total de frases: {len(frases)}")

def etapa2_tokenizacion(doc):
    mostrar_separador("ETAPA 2: TOKENIZACIÓN")
    print("\nTokens generados:\n")
    print(f"{'TOKEN':<20} {'ÍNDICE':<10}")
    print("-" * 30)
    for token in doc:
        print(f"{token.text:<20} {token.i + 1:<10}")

def etapa3_lematizacion(doc):
    mostrar_separador("ETAPA 3: LEMATIZACIÓN")
    print("\nLemas de cada token:\n")
    print(f"{'TOKEN':<20} {'LEMA':<20}")
    print("-" * 40)
    for token in doc:
        print(f"{token.text:<20} {token.lemma_:<20}")

def etapa4_pos_tagging(doc):
    mostrar_separador("ETAPA 4: ETIQUETADO GRAMATICAL (POS)")
    print("\nCategoría gramatical de cada token:\n")
    print(f"{'TOKEN':<15} {'POS':<10} {'DESCRIPCIÓN':<15}")
    print("-" * 40)
    for token in doc:
        pos_original = token.pos_
        texto_normalizado = normalizar(token.text)
        pos_corregido = CORRECCIONES_POS.get(texto_normalizado, pos_original)
        if pos_corregido != pos_original:
            print(f"{token.text:<15} {pos_corregido:<10} {spacy.explain(pos_corregido):<15} [CORREGIDO]")
        else:
            print(f"{token.text:<15} {pos_original:<10} {spacy.explain(pos_original):<15}")

def etapa5_filtrado_stopwords(doc):
    mostrar_separador("ETAPA 5: FILTRADO DE STOPWORDS")
    stopwords_base = nlp.Defaults.stop_words
    stopwords_total = stopwords_base | STOPWORDS_ADICIONALES
    tokens_sin_sw = [token for token in doc if token.text.lower() not in stopwords_total]
    print(f"\nStopwords identificadas en el texto: {len(doc) - len(tokens_sin_sw)}")
    print(f"Tokens restantes (sin stopwords): {len(tokens_sin_sw)}\n")
    print(f"Stopwords base detectadas: {len([t for t in doc if t.text.lower() in stopwords_base])}")
    print(f"Stopwords adicionales (conectores): {len([t for t in doc if t.text.lower() in STOPWORDS_ADICIONALES])}\n")
    print(f"{'TOKEN':<20} {'LEMA':<20}")
    print("-" * 40)
    for token in tokens_sin_sw:
        print(f"{token.text:<20} {token.lemma_:<20}")

def procesar_texto(texto):
    doc = nlp(texto)
    etapa1_segmentacion_frases(doc)
    etapa2_tokenizacion(doc)
    etapa3_lematizacion(doc)
    etapa4_pos_tagging(doc)
    etapa5_filtrado_stopwords(doc)
    mostrar_separador("PROCESAMIENTO COMPLETADO")

def main():
    print("\n" + "#" * 70)
    print("  PIPELINE NLP - PROCESAMIENTO DE LENGUAJE NATURAL")
    print("  SpaCy - Español (es_core_news_sm)")
    print("#" * 70)
    print("\nIngrese un texto en español para procesar (o 'salir' para terminar):\n")

    while True:
        texto = input("> ")
        if texto.lower() == "salir":
            print("\n¡Hasta luego!")
            break
        if texto.strip():
            print("\n")
            procesar_texto(texto)
            print("\n" + "-" * 70)
            print("Ingrese otro texto (o 'salir' para terminar):")
        else:
            print("Por favor, ingrese un texto válido.")

if __name__ == "__main__":
    main()