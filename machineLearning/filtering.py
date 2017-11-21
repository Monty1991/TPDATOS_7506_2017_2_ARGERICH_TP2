from .dataFrameUtils import *

def FiltrarPais(dataFrame, listaPaises):
	return dataFrame[FiltrarColumna(dataFrame['country_name'], listaPaises)]

def FiltrarProvincia(dataFrame, listaProvincias):
	return dataFrame[FiltrarColumna(dataFrame['state_name'], listaProvincias)]

def FiltrarBarrioNulo(dataFrame):
	"""Cuando el barrio es nulo. Sin embargo, usar dataFrame[~dataFrame['barrio'].isnull()] no funciona!!"""
	return dataFrame[dataFrame['place_name'] != dataFrame['state_name']]

def CalcularDiferencia(dataFrame):
	return (dataFrame['dump_date_year'] - dataFrame['created_on_year']) * 12 \
		+ (dataFrame['dump_date_month'] - dataFrame['created_on_month'])

def FiltrarDiferenciaTemporal(dataFrame, maximaDiferenciaEnMeses):
	return dataFrame[CalcularDiferencia(dataFrame) <= maximaDiferenciaEnMeses]

def FiltrarPrecioUnitario(dataFrame):
	if 'price_usd_per_m2' in dataFrame:
		return dataFrame[~dataFrame['price_usd_per_m2'].isnull()]
	else:
		return dataFrame
