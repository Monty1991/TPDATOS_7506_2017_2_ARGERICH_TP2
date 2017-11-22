import numpy as np
import math
from .descriptionUtils import LimpiarNumero

def PreprocesarDescripcion(description):
	#Algunos usuarios publican ambientes fraccionarios, como 3 1/2. Raro, no?
	return description.replace('1/2', '').replace('m2', ' m2 ').replace('.', '. ').replace('$ ', '$').strip()

#Pequeño hack que permite 'decodificar' una palabra a numero
keys = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
values = [x for x in range(1, 10)]
dictPalabrasANumeros = {x:y for x, y in zip(keys, values)}

# ------------------------------------------------------------------------------
# FIND ROOMS 
# ------------------------------------------------------------------------------
def FindRooms(words, size):
	"""Devuelve una lista de numeros con los posibles ambientes"""
	listOfAmbientes = []
	for i in range(0, size-1):
		palabra = words[i].lower()
		if palabra.startswith('amb'):
			if i > 0:
				a = words[i-1].lower()
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
			a = words[i+1].lower()
			if a.startswith('divisible'):
				listOfAmbientes.append(1)
			elif a[0].isdigit():
				numero = LimpiarNumero(a)
				if numero < 13:
					listOfAmbientes.append(numero)
		elif palabra.startswith('monoambiente'):
			listOfAmbientes.append(1)
	return listOfAmbientes

# ------------------------------------------------------------------------------
# GET ROOMS
# ------------------------------------------------------------------------------
def GetRooms(description):
	"""Devuelve el maximo de ambientes posible"""
	words = PreprocesarDescripcion(str(description)).split()
	size = len(words)

	try:
		ambientes = max(FindRooms(words, size))
	except ValueError:
		ambientes = np.NaN

	return ambientes
