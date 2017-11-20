import pandas as pd
from .dataFrameUtils import *
from os import listdir

#PrimeraExpansion
def AgregarFechaDeVolcado(dataFrame, archivo):
	archiveParts = archivo.split('-')
	dataFrame['dump_date_year'] = pd.Series(int(archiveParts[2]), index = dataFrame.index)
	dataFrame['dump_date_month'] = pd.Series(int(archiveParts[3]), index = dataFrame.index)

def ExpandirFechaCreacion(dataFrame):
	dataFrame['created_on_year'] = MapearColumna(dataFrame['created_on'], lambda x: int(x.split('-')[0]))
	dataFrame['created_on_month'] = MapearColumna(dataFrame['created_on'], lambda x: int(x.split('-')[1]))

def ExpandirBarrioProvinciaYPais(dataFrame):
	if not 'country_name' in dataFrame:
		dataFrame['country_name'] = MapearColumna(dataFrame['place_with_parent_names'], lambda x: x.split('|')[1])
	if not 'state_name' in dataFrame:
		dataFrame['state_name'] = MapearColumna(dataFrame['place_with_parent_names'], lambda x: x.split('|')[2])
	dataFrame['barrio'] = MapearColumna(dataFrame['place_with_parent_names'], lambda x: x.split('|')[3])

def PrimeraExpansion(dataFrame, archivo):
	AgregarFechaDeVolcado(dataFrame, archivo)
	ExpandirFechaCreacion(dataFrame)
	ExpandirBarrioProvinciaYPais(dataFrame)

	if 'surface_in_m2' in dataFrame:
		RenombrarColumna(dataFrame, 'surface_in_m2', 'surface_total_in_m2')

#Filtrado
def CalcularDiferencia(dataFrame):
	return (dataFrame['dump_date_year'] - dataFrame['created_on_year']) * 12 \
		+ (dataFrame['dump_date_month'] - dataFrame['created_on_month'])

def Filtrar(dataFrame, listaPaises, listaProvincias):
	dataFrame = dataFrame[FiltrarColumna(dataFrame['country_name'], listaPaises)]
	dataFrame = dataFrame[FiltrarColumna(dataFrame['state_name'], listaProvincias)]
	dataFrame = dataFrame[CalcularDiferencia(dataFrame) < 18]
	if 'price_usd_per_m2' in dataFrame:
		dataFrame = dataFrame[~dataFrame['price_usd_per_m2'].isnull()]
	"""Cuando el barrio es nulo. Sin embargo, usar dataFrame[~dataFrame['barrio'].isnull()] no funciona!!"""
	dataFrame = dataFrame[dataFrame['place_name'] != dataFrame['state_name']]
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
								 'created_on_month',
								 'extra'])

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

def SegundaExpansion(dataFrame):
	"""TODO: completar con los cruces de dataframes, como los cálculos de distancias, y expandir la descripción"""
	return 2

def SegundaLimpieza(dataFrame):
	SacarListaColumnas(dataFrame, ['title', 'description', 'lat', 'lon'])

def PreprocesarArchivo(rutaArchivo, nombreArchivo, listaPaises, listaProvincias):
	dataFrame = LeerDataFrame(rutaArchivo)
	PrimeraExpansion(dataFrame, nombreArchivo)
	dataFrame = Filtrar(dataFrame, listaPaises, listaProvincias)
	LimpiarDataFrame(dataFrame)
	ControlarConsistenciaPrecio(dataFrame)
	SegundaExpansion(dataFrame)
	SegundaLimpieza(dataFrame)
	return dataFrame

def PreprocesarCarpeta(rutaCarpetaOrigen, rutaCarpetaDestino, listaPaises, listaProvincias):
	"""Lee los archivos en rutaCarpetaOrigen, los preprocesa y guarda en rutaCarpetaDestino"""
	for archive in listdir(rutaCarpetaOrigen):
		if '.csv' in archive:
			df = PreprocesarArchivo(rutaCarpetaOrigen + archive, archive, listaPaises, listaProvincias)
			df.to_csv(rutaCarpetaDestino + archive, encoding = 'utf-8', index = False)
