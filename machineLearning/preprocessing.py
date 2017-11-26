import numpy as np
import pandas as pd
from .dataFrameUtils import *
from .filtering import *
from .descriptionExpansion import gClaves
from .expanding import *
from os import listdir
import math
from . import extract_surface
from . import normalize_rooms, normalize_expenses
from . import utils
from . import distanceCalculator
import time

def Filtrar(dataFrame, nombreArchivo, listaPaises, listaProvincias):
	ExpandirPais(dataFrame)
	ExpandirProvincia(dataFrame)
	ExpandirBarrio(dataFrame)
	ExpandirFechaCreacion(dataFrame)
	ExpandirFechaVolcado(dataFrame, nombreArchivo)

	dataFrame = FiltrarPais(dataFrame, listaPaises)
	dataFrame = FiltrarProvincia(dataFrame, listaProvincias)
	dataFrame = FiltrarDiferenciaTemporal(dataFrame, 18)
	dataFrame = FiltrarPrecioUnitario(dataFrame)
	return dataFrame

#Consistencia
def ControlarSuperficie(dataFrame):
	if 'surface_in_m2' in dataFrame:
		RenombrarColumna(dataFrame, 'surface_in_m2', 'surface_total_in_m2')

	#Controlamos superficies imposibles
	dataFrame['surface_total_in_m2'] = dataFrame['surface_total_in_m2'].map(lambda x: x if x > 10 else x * 10)
	if 'surface_covered_in_m2' in dataFrame:
		#Casos famosos, total menor a cubierta, con cubierta menor a los 1000 metros cuadrados
		condicion = (dataFrame['surface_total_in_m2'] < dataFrame['surface_covered_in_m2']) & (dataFrame['surface_covered_in_m2'] < 1000)
		dataFrame['surface_total_in_m2'].update(dataFrame[condicion]['surface_covered_in_m2'])

	#Invalidamos superficies nulas
	dataFrame['surface_total_in_m2'].replace(to_replace = 0, value = np.NaN, inplace = True)

	#Intentamos obtener el maximo de superficies posibles
	if 'description' in dataFrame:
		dataFrame['surface_total_in_m2'].fillna(dataFrame[dataFrame['surface_total_in_m2'].isnull()]['description'].map(extract_surface.GetSurface), inplace = True)

def PrecioUnitarioValido(price, surface, unit_price):
	return ((abs(price - (surface * unit_price)) / price) < 0.01)

def ControlarPrecioUnitario(price, surface, unit_price):
	if PrecioUnitarioValido(price, surface, unit_price):
		return unit_price
	else:
		return (price / surface)

def ControlarConsistenciaPrecio(dataFrame):
	if len(dataFrame.index) > 0:
		if ('price_usd_per_m2' in dataFrame) and ('price' in dataFrame):
			dataFrame['price_usd_per_m2'] = dataFrame[['price', 'surface_total_in_m2', 'price_usd_per_m2']].apply(lambda x: ControlarPrecioUnitario(x[0], x[1], x[2]), axis = 1)

def NormalizeFloor(floor):
	if floor > 999:
		return 0
	if floor > 100:
		return math.floor(floor / 100)
	return floor

def Uniformizar(dataFrame):
	utils.Uniformizar(dataFrame, 'floor', NormalizeFloor, 0)
	utils.Uniformizar(dataFrame, 'expenses', normalize_expenses.NormalizeExpenses, 0)
	utils.Uniformizar(dataFrame, 'rooms', normalize_rooms.NormalizeRooms, 1)

def ObtenerMenorDistancia(state_name, barrio, lat, lon, dataFrameACruzar):
	if state_name == barrio:
		barrio = 'any'
	valor = distanceCalculator.NormalizarDistancias(distanceCalculator.ObtenerMenorDistancia(lat, lon, barrio, dataFrameACruzar, 'barrio', 'lat', 'lon'))
	#ponemos como limite, 2.5 km
	if valor <= 5:
		return valor
	return np.NaN

def CruzarDataFrame(dataFrame, dataFrameACruzar, nombreCampo):
	dataFrame[nombreCampo] = dataFrame[['state_name', 'barrio', 'lat', 'lon']].apply(lambda x: ObtenerMenorDistancia(x[0], x[1], x[2], x[3], dataFrameACruzar), axis = 1)

def CruzarDataFrames(dataFrame, rutaCarpetaDataFramesCoordenadas):
	listaCamposExtras = []
	for archive in listdir(rutaCarpetaDataFramesCoordenadas):
		if '.csv' in archive:
			df = LeerDataFrame(rutaCarpetaDataFramesCoordenadas + archive)
			campoExtra = archive.replace('.csv', '')
			listaCamposExtras.append(campoExtra)
			CruzarDataFrame(dataFrame, df, campoExtra)
	return listaCamposExtras

def PreprocesarDataFrame(dataFrame, nombreArchivo, listaPaises, listaProvincias, rutaCarpetaDataFramesCoordenadas):
	dataFrame = Filtrar(dataFrame, nombreArchivo, listaPaises, listaProvincias)
	ControlarSuperficie(dataFrame)
	ControlarConsistenciaPrecio(dataFrame)
	Uniformizar(dataFrame)
	ExpandirDescripcion(dataFrame, gClaves)
	listaCamposExtras = CruzarDataFrames(dataFrame, rutaCarpetaDataFramesCoordenadas)	
	return dataFrame, listaCamposExtras

def PreprocesarArchivo(rutaCarpeta, nombreArchivo, listaPaises, listaProvincias, rutaCarpetaDataFramesCoordenadas):
	start = time.time()
	dataFrame = LeerDataFrame(rutaCarpeta + nombreArchivo)
	dataFrame, listaCamposExtras = PreprocesarDataFrame(dataFrame, nombreArchivo, listaPaises, listaProvincias, rutaCarpetaDataFramesCoordenadas)
	end = time.time()
	return dataFrame[['property_type', 'state_name', 'barrio', 'dump_date_year', 'dump_date_month', 'price_usd_per_m2', 'surface_total_in_m2', 'rooms', 'floor', 'expenses'] + gClaves + listaCamposExtras], end - start

def PreprocesarCarpeta(rutaCarpetaOrigen, rutaCarpetaDestino, listaPaises, listaProvincias, rutaCarpetaDataFramesCoordenadas):
	"""Lee los archivos en rutaCarpetaOrigen, los preprocesa y guarda en rutaCarpetaDestino"""
	for archive in listdir(rutaCarpetaOrigen):
		if '.csv' in archive:
			print('Preprocesando <' + archive, end = '>: ')
			df, timeUsed = PreprocesarArchivo(rutaCarpetaOrigen, archive, listaPaises, listaProvincias, rutaCarpetaDataFramesCoordenadas)
			df.to_csv(rutaCarpetaDestino + archive, encoding = 'utf-8', index = False)
			print('Done in ' + str(timeUsed) + ' seconds')
