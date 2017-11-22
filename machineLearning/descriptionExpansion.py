# ------------------------------------------------------------------------------
# Creado por: Sebastian Blanco
# Modificado por: Maximiliano Montiel
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# INICIALIZAR DICCIONARIO
# ------------------------------------------------------------------------------
# pre: Recibe una lista de claves
# pos: Devuelve un diccionario con las claves recibidas y con sus valores inicializados en 0
# observaciones: De momento, no se distinguen entre null y ausencia del termino
def Inicializar_Diccionario(claves):
	"""Bizarro, pero mas rapido  PEP 274 -- Dict Comprehensions: https://www.python.org/dev/peps/pep-0274/"""
	return { clave: 0 for clave in claves }

# ------------------------------------------------------------------------------
# ENCONTRAR FRASE
# ------------------------------------------------------------------------------
# pre: Recibe un vector de palabras, la posicion en ese vector que se
# esta leyendo, y un vector de frases
# pos: Devuelve una tripla que dice si alguna de las frases en el
# vector "phrases", el offset el cual debe desplazarse la posicion de lectura
# del vector "words" y el indice en donde se encuentra la frase encontrada en el
# vector "phrases"
def Encontrar_Frase(words, i, vector_frases):
	offset = 0
	indice = 0
	for frase in vector_frases:
		if words[i].lower() in frase:
			phrase_split = frase.split()
			size = len(phrase_split)
			offset = size
			indice = vector_frases.index(frase)
			for j in range(0, size):
				if (i + j < size) and (words[i + j] != phrase_split[j]):
					return False, offset, indice
			return True, offset, indice
	return False, offset, indice


gCharacteristics = [
	'living',
	'cochera',
	'comedor',
	'pileta',
	'piscina']
gPhrases = [
	'cancha de tenis',
	'club house',
	'sector de juegos infantiles',
	'futbol 5',
	'seguridad las 24 hs']

#Juntamos todo, mas rapido
gClaves = gCharacteristics + gPhrases

# ------------------------------------------------------------------------------
# Parsear Descripcion
# ------------------------------------------------------------------------------
# pre: Recibe una cadena de texto
# pos: Devuelve un diccionario

def Parsear_Descripcion(description, claves = gCharacteristics, frases = gPhrases):
	diccionario = Inicializar_Diccionario(claves + frases)
	if description == '':
		return diccionario
	if type(description) is not str:
		return diccionario
	vector_palabras = description.split()
	longitud_vector_palabras = len(vector_palabras)
	for indice_Palabra in range(0, longitud_vector_palabras):
		(palabra_pertenece, offset, indice) = Encontrar_Frase(vector_palabras, indice_Palabra, frases)
		if palabra_pertenece:
			indice_Palabra += offset
			if indice_Palabra >= longitud_vector_palabras:
				break
			diccionario[frases[indice]] = 1
		palabra = vector_palabras[indice_Palabra].lower()
		if palabra in claves:
			diccionario[palabra] = 1

	return diccionario

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------