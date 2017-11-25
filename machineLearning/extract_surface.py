import numpy as np
from .utils import *

def PreprocesarDescripcion(description):
	"""Separa el termino m2"""
	return description.replace('m2', ' m2 ')

def FindProducts(words, size):
	"""Devuelve una lista de duplas (numero1, numero2) para toda aparicion del patron '<numero1> x <numero2>' """
	listOfProducts = []
	for i in range(0, size-2):
		a = words[i]
		b = words[i+2]
		if a[0].isdigit() and (words[i+1] == 'x') and b[0].isdigit():
			listOfProducts.append((LimpiarNumero(a), LimpiarNumero(b)))
	return listOfProducts

def FindSurfaces(words, size):
	"""Devuelve un diccionario con un termino asociado y una terna, (palabra-2, palabra-1, superficie)"""
	dictOfSurfaces = {}
	for i in range(2, size-1):
		a = words[i].lower()
		b = words[i+1].lower()
		if a[0].isdigit() and b.startswith('m2'):
			palabra_menos1 = words[i-1].lower()
			palabra_menos2 = words[i-2].lower()
			if palabra_menos1 == 'de':
				identificador = palabra_menos2
			else:
				identificador = palabra_menos1
			dictOfSurfaces[identificador] = (palabra_menos2, palabra_menos1, LimpiarNumero(a))
		if a.startswith('total'):
			if b[0].isdigit():
				palabra_menos1 = words[i-1].lower()
				dictOfSurfaces[a] = (palabra_menos1, a, LimpiarNumero(b))
	return dictOfSurfaces

def GetSurface(description):
	"""Devuelve la maxima superficie total"""
	words = PreprocesarDescripcion(str(description)).split()
	size = len(words)
	productos = Map(FindProducts(words, size), lambda x: x[0] * x[1])
	totalCalculada = Reduce(productos, lambda x, y: x + y, np.NaN)

	try:
		encontradas = max(Map(FindSurfaces(words, size).values(), lambda x: x[2]))
	except ValueError:
		encontradas = np.NaN

	return max(totalCalculada, encontradas)
