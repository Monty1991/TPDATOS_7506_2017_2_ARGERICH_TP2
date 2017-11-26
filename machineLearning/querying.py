from .dataFrameUtils import *
from . import preprocessing
from . import extract_surface
from . import processing
from . import expanding

import numpy as np
import pandas as pd

import json

gIndex = ['state_name', 'barrio', 'property_type']

def CalcularMedianaBarriosAgosto(dataFrameMedianasPorBarrios):
	"""Calcula los posibles precios unitarios medianas para el mes de agosto de 2017"""
	"""TODO: Generalizar funcion"""
	medianas = dataFrameMedianasPorBarrios[(dataFrameMedianasPorBarrios['dump_date_year'] == 2017) & (dataFrameMedianasPorBarrios['dump_date_month'] > 1)]
	listaGroups = []
	for name, group in medianas.groupby(by = gIndex):
		precioUnitarioMediana = pd.Series([x for x in group['precio_unitario_mediana']]).append(pd.Series([np.NaN]), ignore_index = True)
		try:
			precioUnitarioMediana = precioUnitarioMediana.interpolate(method = 'polynomial', order = 1)
		except ValueError:
			1+1
		value = precioUnitarioMediana[precioUnitarioMediana.count() - 1]
		df = { 'state_name': name[0], 'barrio': name[1], 'property_type': name[2], 'precio_unitario_mediana': value}
		listaGroups.append(df)
	return pd.DataFrame(listaGroups)

def ObtenerPrecioMedianaPorBarrio(dataFrameConsulta, dataFrameMedianasPorBarrios):
	return dataFrameConsulta.merge(dataFrameMedianasPorBarrios, how = 'left', left_on = gIndex, right_on = gIndex)

def ObtenerCoeficiente(dataFrameConsulta, dataFrameCoeficientes, coef):
	return dataFrameConsulta.merge(dataFrameCoeficientes[dataFrameCoeficientes['varName'] == coef], how = 'left', left_on = coef, right_on = 'variable')['coeficiente'].fillna(1)

def ObtenerCoeficienteGlobal(dataFrameConsulta, dataFrameCoeficientes):
	coeficiente_global = pd.Series(1, index = dataFrameConsulta.index)
	for coef in dataFrameCoeficientes['varName'].unique():
		coeficiente_global *= ObtenerCoeficiente(dataFrameConsulta, dataFrameCoeficientes, coef)
	return coeficiente_global

gDiccionarioReconversionTipoPropiedad = {'casa': 'house', 'ph': 'PH', 'departamento': 'apartment', 'tienda': 'store', 'house': 'house', 'PH': 'PH', 'apartment': 'apartment', 'store': 'store'}
def ReconvertirTipoPropiedad(valor):
	return gDiccionarioReconversionTipoPropiedad[valor]

def ExtraerSuperficie(dataFrameConsulta, dataFrameMedianasPorBarrios):
	medianas = dataFrameMedianasPorBarrios[(dataFrameMedianasPorBarrios['dump_date_year'] == 2017) & (dataFrameMedianasPorBarrios['dump_date_month'] > 1)]
	medianas = medianas.groupby(by = gIndex)['superficies_mediana'].median().reset_index(name = 'superficies_mediana')

	df = dataFrameConsulta.merge(medianas, how = 'left', left_on = gIndex, right_on = gIndex)
	dataFrameConsulta['superficies_mediana'] = df['superficies_mediana']
	dataFrameConsulta['surface_total_in_m2'].fillna(dataFrameConsulta['superficies_mediana'], inplace = True)

def PreprocesarConsulta(dataFrameConsulta, dataFrameMedianasPorBarrios):
	#Porque un "gracioso" tradujo los valores
	dataFrameConsulta['property_type'] = dataFrameConsulta['property_type'].map(ReconvertirTipoPropiedad)
	expanding.ExpandirProvincia(dataFrameConsulta)
	expanding.ExpandirBarrio(dataFrameConsulta)
	expanding.ExpandirFechaVolcado(dataFrameConsulta, 'properati-AR-2017-08-01-properties-sell')

	preprocessing.ControlarSuperficie(dataFrameConsulta)

	preprocessing.Uniformizar(dataFrameConsulta)
	processing.ArreglarRoomsUltimoMomento(dataFrameConsulta)
	processing.ParametrizarExpensasUltimoMomento(dataFrameConsulta)

	ExtraerSuperficie(dataFrameConsulta, dataFrameMedianasPorBarrios)

	return dataFrameConsulta

def ResolverConsulta(dataFrameConsulta, dataFrameCoeficientes, dataFrameMedianasPorBarrios, rutaCarpetaDataFramesCoordenadas):
	dataFrameConsulta = PreprocesarConsulta(dataFrameConsulta, dataFrameMedianasPorBarrios)
	preprocessing.CruzarDataFrames(dataFrameConsulta, rutaCarpetaDataFramesCoordenadas)

	dataFrameMedianasPorBarrios = CalcularMedianaBarriosAgosto(dataFrameMedianasPorBarrios)
	dataFrameConsulta = ObtenerPrecioMedianaPorBarrio(dataFrameConsulta, dataFrameMedianasPorBarrios)
	dataFrameConsulta['coeficiente_global'] = ObtenerCoeficienteGlobal(dataFrameConsulta, dataFrameCoeficientes)
	dataFrameConsulta['price_usd_per_m2'] = dataFrameConsulta['coeficiente_global'] * dataFrameConsulta['precio_unitario_mediana']
	dataFrameConsulta['price_usd'] = dataFrameConsulta['surface_total_in_m2'] * dataFrameConsulta['price_usd_per_m2']
	return dataFrameConsulta[['id', 'price_usd']]
