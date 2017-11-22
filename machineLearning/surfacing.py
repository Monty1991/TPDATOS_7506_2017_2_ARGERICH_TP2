import numpy as np
import math

# ------------------------------------------------------------------------------
# Mapear
# ------------------------------------------------------------------------------
def Mapear(columna, funcion):
	"""Es un map sobre arreglos que devuelve otro arreglo. Similar al map de pandas"""
	return [funcion(x) for x in columna]

# ------------------------------------------------------------------------------
# Reducir
# ------------------------------------------------------------------------------
def Reducir(columna, funcion, default):
	"""Es un reduce sobre un arreglo que devuelve un valor. Similar a Spark"""
	size = len(columna)
	if size == 0:
		return default
	if size < 2:
		return columna[0]
	if size == 2:
		return funcion(columna[0], columna[1])
	mitad = int(math.floor(size / 2))
	return funcion(Reducir(columna[0:mitad+1], funcion, default), Reducir(columna[mitad + 1:], funcion, default))

# ------------------------------------------------------------------------------
# LIMPIAR NUMERO 
# ------------------------------------------------------------------------------
def LimpiarNumero(word):
	"""Esta funcion magica devuelve un numero, independientemente de toda la basura que le siga"""
	offset = 0
	hasDot = False
	for d in word:
		if d in '.,':
			if hasDot:
				break
			hasDot = True
		elif not d.isdigit():
			break
		offset += 1
	return float(word[0:offset].replace(',', '.'))

# ------------------------------------------------------------------------------
# PREPROCESAR DESCRIPCION
# ------------------------------------------------------------------------------
def PreprocesarDescripcion(description):
	"""Separa el termino m2"""
	return description.replace('m2', ' m2 ').replace('  ', ' ')

# ------------------------------------------------------------------------------
# FIND PRODUCTS
# ------------------------------------------------------------------------------
def FindProducts(words, size):
	"""Devuelve una lista de duplas (numero1, numero2) para toda aparicion del patron '<numero1> x <numero2>' """
	listOfProducts = []
	for i in range(0, size-2):
		a = words[i]
		b = words[i+2]
		if a[0].isdigit() and (words[i+1] == 'x') and b[0].isdigit():
			listOfProducts.append((LimpiarNumero(a), LimpiarNumero(b)))
	return listOfProducts

# ------------------------------------------------------------------------------
# FIND SURFACES 
# ------------------------------------------------------------------------------
def FindSurfaces(words, size):
	"""Devuelve un diccionario con un termino asociado y una terna, (palabra-2, palabra-1, superficie)"""
	dictOfSurfaces = {}
	for i in range(2, size-1):
		a = words[i]
		if a[0].isdigit() and (words[i+1].lower() == 'm2'):
			palabra_menos1 = words[i-1].lower()
			palabra_menos2 = words[i-2].lower()
			if palabra_menos1 == 'de':
				identificador = palabra_menos2
			else:
				identificador = palabra_menos1
			dictOfSurfaces[identificador] = (palabra_menos2, palabra_menos1, LimpiarNumero(a))
	return dictOfSurfaces

# ------------------------------------------------------------------------------
# GET SURFACE
# ------------------------------------------------------------------------------
def GetSurface(description):
	"""Devuelve todas las superficies encontradas, y la 'totalCalculada'"""
	words = PreprocesarDescripcion(str(description)).split()
	size = len(words)
	productos = Mapear(FindProducts(words, size), lambda x: x[0] * x[1])
	totalCalculada = Reducir(productos, lambda x, y: x + y, np.NaN)

	try:
		encontradas = max(Mapear(FindSurfaces(words, size).values(), lambda x: x[2]))
	except ValueError:
		encontradas = np.NaN

	return max(totalCalculada, encontradas)
