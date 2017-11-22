import numpy as np
import pandas as pd
from .dataFrameUtils import *
from .filtering import *
from .descriptionExpansion import gClaves
from .expanding import *
from os import listdir
import math
from . import surfacing

#PrimeraExpansion
def PrimeraExpansion(dataFrame, archivo):
	ExpandirFechaCreacion(dataFrame)
	ExpandirFechaVolcado(dataFrame, archivo)
	ExpandirPais(dataFrame)
	ExpandirProvincia(dataFrame)
	ExpandirBarrio(dataFrame)

	if 'surface_in_m2' in dataFrame:
		RenombrarColumna(dataFrame, 'surface_in_m2', 'surface_total_in_m2')

	#Invalidamos superficies nulas
	dataFrame['surface_total_in_m2'].replace(to_replace = 0, value = np.NaN, inplace = True)
	#Intentamos obtener el maximo de superficies posibles
	if 'description' in dataFrame:
		dataFrame['surface_total_in_m2'].fillna(dataFrame['description'].map(surfacing.GetSurface), inplace = True)

def Filtrar(dataFrame, listaPaises, listaProvincias):
	dataFrame = FiltrarPais(dataFrame, listaPaises)
	dataFrame = FiltrarProvincia(dataFrame, listaProvincias)
	# La consulta tiene barrios nulos (inserte emoji de furia)
	#	dataFrame = FiltrarBarrioNulo(dataFrame)
	dataFrame = FiltrarDiferenciaTemporal(dataFrame, 18)
	dataFrame = FiltrarPrecioUnitario(dataFrame)
	return dataFrame

#PrimeraLimpieza
def EliminarColumnasNoRelevantes(dataFrame):
	SacarListaColumnas(dataFrame, ['properati_url',
								 'operation',
								 'geonames_id',
								 'lat-lon',
								 'currency',
								 'price_aprox_local_currency',
								 'price_aprox_usd',
								 'price_per_m2',
								 'image_thumbnail',
								 'place_with_parent_names',
								 'place_with_parent_names_l1',
								 'place_with_parent_names_l2',
								 'country_name',
								 'id',
								 'created_on',
								 'created_on_year',
								 'created_on_month'])

def LimpiarDataFrame(dataFrame):
	EliminarColumnasNoRelevantes(dataFrame)

#Consistencia
def PrecioUnitarioValido(price, surface, unit_price):
	return ((abs(price - (surface * unit_price)) / price) < 0.01)

def ControlarPrecioUnitario(price, surface, unit_price):
	if PrecioUnitarioValido(price, surface, unit_price):
		return unit_price
	else:
		return (price / surface)

def ControlarConsistenciaPrecio(dataFrame):
	if len(dataFrame.index) > 0:
		if ('price_per_m2' in dataFrame) and ('price' in dataFrame):
			dataFrame['price_usd_per_m2'] = dataFrame[['price', 'surface_total_in_m2', 'price_usd_per_m2']].apply(lambda x: ControlarPrecioUnitario(x[0], x[1], x[2]), axis = 1)

def UniformizarFloor(floor):
	if floor > 999:
		return 0
	if floor > 100:
		return math.floor(floor / 100)
	return floor

def UniformizarFloors(dataFrame):
	dataFrame['floor'] = dataFrame['floor'].map(UniformizarFloor)
	dataFrame['floor'].fillna(0, inplace = True)

def UniformizarExpensa(expensa):
	if type(expensa) == str:
		return expensa.lstrip('$ ').replace('.-', ' ').split(' ')[0]
	return expensa

def UniformizarExpensas(dataFrame):
	dataFrame['expenses'] = dataFrame['expenses'].map(UniformizarExpensa)
	dataFrame['expenses'].fillna(0, inplace = True)

def SegundaExpansion(dataFrame):
	"""TODO: completar con los cruces de dataframes, como los cálculos de distancias"""

	ExpandirDescripcion(dataFrame, gClaves)

def SegundaLimpieza(dataFrame):
	SacarListaColumnas(dataFrame, ['title', 'description', 'extra', 'lat', 'lon'])

def PreprocesarDataFrame(dataFrame, nombreArchivo, listaPaises, listaProvincias):
	PrimeraExpansion(dataFrame, nombreArchivo)
	dataFrame = Filtrar(dataFrame, listaPaises, listaProvincias)
	LimpiarDataFrame(dataFrame)
	ControlarConsistenciaPrecio(dataFrame)
	UniformizarFloors(dataFrame)
	UniformizarExpensas(dataFrame)
	SegundaExpansion(dataFrame)
	SegundaLimpieza(dataFrame)
	return dataFrame

def PreprocesarArchivo(rutaArchivo, nombreArchivo, listaPaises, listaProvincias):
	dataFrame = LeerDataFrame(rutaArchivo)
	return PreprocesarDataFrame(dataFrame, nombreArchivo, listaPaises, listaProvincias)

def PreprocesarCarpeta(rutaCarpetaOrigen, rutaCarpetaDestino, listaPaises, listaProvincias):
	"""Lee los archivos en rutaCarpetaOrigen, los preprocesa y guarda en rutaCarpetaDestino"""
	for archive in listdir(rutaCarpetaOrigen):
		if '.csv' in archive:
			df = PreprocesarArchivo(rutaCarpetaOrigen + archive, archive, listaPaises, listaProvincias)
			df.to_csv(rutaCarpetaDestino + archive, encoding = 'utf-8', index = False)
