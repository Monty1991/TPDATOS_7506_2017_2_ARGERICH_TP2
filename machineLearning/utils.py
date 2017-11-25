import math

#MapReduce
def Map(columna, funcion):
	"""Es un map sobre arreglos que devuelve otro arreglo. Similar a Spark"""
	return [funcion(x) for x in columna]

def Reduce(columna, funcion, default):
	"""Es un reduce sobre un arreglo que devuelve un valor. Similar a Spark"""
	size = len(columna)
	if size == 0:
		return default
	if size < 2:
		return columna[0]
	if size == 2:
		return funcion(columna[0], columna[1])
	mitad = int(math.floor(size / 2))
	return funcion(Reduce(columna[0:mitad+1], funcion, default), Reduce(columna[mitad + 1:], funcion, default))

def Filter(columna, funcion):
	"""Filtra los elementos de un arreglo y devuelve otro arreglo. Similar a Spark"""
	return [x for x in columna if funcion(x)]

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

def GetValidNumber(number):
	"""Parsea un numero"""
	if type(number) == str:
		if number == '':
			return 0
		return LimpiarNumero(number)
	else:
		return number

def Uniformizar(dataFrame, nombreColumna, funcion, defaultValue):
	dataFrame[nombreColumna] = dataFrame[nombreColumna].map(funcion)
	dataFrame[nombreColumna].fillna(defaultValue, inplace = True)

#Pequeño hack que permite 'decodificar' una palabra a numero
keys = ['uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
values = [x for x in range(1, 10)]
dictPalabrasANumeros = {x:y for x, y in zip(keys, values)}
