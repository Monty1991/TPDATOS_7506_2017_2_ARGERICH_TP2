import pandas as pd
from os import listdir
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

#Dataframes
def LeerDataFrame(nombreArchivo):
	"""Función que lee un archivo y devuelve un dataframe"""
	return pd.read_csv(nombreArchivo, low_memory = False)

def ConcatenarDataFrames(listaDataFrames):
	"""Concatena una lista de dataframes"""
	return pd.concat(listaDataFrames)

def LeerCarpetaDataFrames(rutaCarpeta):
	"""Lee todos los dataframes de una carpeta y los devuelve como un unico dataframe"""
	listaDataFrames = []
	for archive in listdir(rutaCarpeta):
		if ".csv" in archive:
			df = LeerDataFrame(rutaCarpeta + archive)
			listaDataFrames.append(df)
	return ConcatenarDataFrames(listaDataFrames)

#Columnas
def AgregarColumna(dataFrame, nombreColumna, columna):
	"""Agrega una columna a un dataFrame. Si el nombre ya está usado, no hace nada"""
	if not nombreColumna in dataFrame:
		dataFrame[nombreColumna] = columna

def FiltrarColumna(columna, listaValores):
	"""Filtra una columna por los valores pasados en una lista"""
	return columna.isin(listaValores)

def MapearColumna(columna, function):
	"""Crea una columna a partir de aplicar una función a todos sus elementos"""
	return columna.map(function)

def RenombrarColumna(dataFrame, nombreViejo, nombreNuevo):
	"""Cambia de nombre una columna. Si el nuevo nombre ya está usado, no hace nada"""
	if not nombreNuevo in dataFrame:
		if nombreViejo in dataFrame:
			dataFrame[nombreNuevo] = dataFrame[nombreViejo]
			SacarColumna(dataFrame, nombreViejo)

def SacarColumna(dataFrame, nombreColumna):
	"""Quita una columna de un dataframe"""
	dataFrame.drop(nombreColumna, axis = 1, inplace = True, errors = 'ignore')

def SacarListaColumnas(dataFrame, listaNombreColumna):
	"""Quita una lista de columnas de un dataframe"""
	dataFrame.drop(listaNombreColumna, axis = 1, inplace = True, errors = 'ignore')
