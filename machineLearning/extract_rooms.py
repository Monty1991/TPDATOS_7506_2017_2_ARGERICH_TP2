import numpy as np
from .utils import LimpiarNumero, dictPalabrasANumeros

def PreprocesarDescripcion(description):
	#Algunos usuarios publican ambientes fraccionarios, como 3 1/2. Raro, no?
	return description.replace('1/2', '').replace('m2', ' m2 ').replace('.', '. ').replace('$ ', '$').strip()

def FindRooms(words, size):
	"""Devuelve una lista de numeros con las posibles cantidades de ambientes"""
	listOfAmbientes = []
	for i in range(0, size-1):
		palabra = words[i]
		if palabra.startswith('amb'):
			if i > 0:
				a = words[i-1]
				if a[0].isdigit():
					numero = LimpiarNumero(a)
					if numero < 13:
						listOfAmbientes.append(numero)
						continue
				elif a in dictPalabrasANumeros:
					listOfAmbientes.append(dictPalabrasANumeros[a])
					continue
				elif a.startswith('amplio'):
					listOfAmbientes.append(1)
					continue
			a = words[i+1]
			if a.startswith('divisible'):
				listOfAmbientes.append(1)
			elif a[0].isdigit():
				numero = LimpiarNumero(a)
				if numero < 13:
					listOfAmbientes.append(numero)
		elif palabra.startswith('monoambiente'):
			listOfAmbientes.append(1)
	return listOfAmbientes

def GetRooms(description):
	"""Devuelve el maximo de ambientes posible"""
	words = PreprocesarDescripcion(str(description).lower()).split()
	size = len(words)

	try:
		ambientes = max(FindRooms(words, size))
	except ValueError:
		ambientes = np.NaN

	return ambientes
