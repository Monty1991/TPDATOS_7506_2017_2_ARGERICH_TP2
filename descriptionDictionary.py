false = 0
true = 1


# ------------------------------------------------------------------------------
# INICIALIZAR DICCIONARIO
# ------------------------------------------------------------------------------
# pre: Recibe una lista de claves
# pos: devuelve un diccionario de esas claves recibidas inicializadas en cero
def inicializar_diccionario(keys):
    dicc = {}
    for charac in keys:
        dicc[charac] = 0
    return dicc


# ------------------------------------------------------------------------------
# ENCONTRAR FRASE
# ------------------------------------------------------------------------------
# pre: Recibe un vector de palabras, la posicion en ese vector que se
# esta leyendo, y un vector de frases
# pos: Devuelve una tripla que dice si alguna de las frases en el
# vector "phrases", el offset el cual debe desplazarse la posicion de lectura
# del vector "words" y el indice en donde se encuantrala frase encontrada en el
# vector "phrases"
def encontrar_frase(words, i, phrases):
    offset = 0
    index = 0
    for phrase in phrases:
        if words[i].lower() in phrase:
            phrase_split = phrase.split()
            size = len(phrase_split)
            offset = size
            index = phrases.index(phrase)
            for j in range(0, size):
                if (i + j < size) and (words[i + j] != phrase_split[j]):
                    return False, offset, index
            return True, offset, index
    return False, offset, index


# ------------------------------------------------------------------------------
# CREAR DICCIONARIO DESCRIPCION
# ------------------------------------------------------------------------------
# pre: Recibe un dataframe
# pos: Devuelve una lista de diccionarios
def crear_diccionario_descripcion(df):
    characteristics = [
        "living",
        "cochera",
        "comedor",
        "pileta",
        "piscina"
    ]
    phrases = [
        "cancha de tenis",
        "club house",
        "sector de juegos infantiles",
        "futbol 5",
        "seguridad las 24 hs"
    ]
    size = len(df.index)
    dicc_list = []
    for i in range(0, size):
        dicc = inicializar_diccionario(characteristics + phrases)
        if 'description' not in df:
            dicc_list.append(dicc)
            continue
        description = list(df['description'])
        if type(description[i]) != type(""):
            dicc_list.append(dicc)
            continue
        words = description[i].split()
        lenght = len(words)
        for j in range(0, lenght):
            (wordBelongs, offset, index) = encontrar_frase(words, j, phrases)
            if wordBelongs:
                j += offset
                if j >= lenght:
                    break
                dicc[phrases[index]] = true
            if words[j].lower() in characteristics:
                dicc[words[j].lower()] = true
        dicc_list.append(dicc)
    return dicc_list


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
