from .dataFrameUtils import *
from . import preprocessing

import numpy as np
import pandas as pd

gIndex = ['state_name', 'barrio', 'property_type']

def CalcularPromedioBarriosAgosto(dataFramePromediosPorBarrios):
	"""Calcula los posibles precios unitarios promedios para el mes de agosto de 2017"""
	"""TODO: Generalizar funcion"""
	promedios = dataFramePromediosPorBarrios[(dataFramePromediosPorBarrios['dump_date_year'] == 2017) & (dataFramePromediosPorBarrios['dump_date_month'] > 1)]
	listaGroups = []
	for name, group in promedios.groupby(by = gIndex):
		precioUnitarioPromedio = pd.Series([x for x in group['precio_unitario_promedio']]).append(pd.Series([np.NaN]), ignore_index = True)
		try:
			precioUnitarioPromedio = precioUnitarioPromedio.interpolate(method = 'polynomial', order = 1)
		except ValueError:
			1+1
		value = precioUnitarioPromedio[precioUnitarioPromedio.count() - 1]
		df = { 'state_name': name[0], 'barrio': name[1], 'property_type': name[2], 'precio_unitario_promedio': value}
		listaGroups.append(df)
	return pd.DataFrame(listaGroups)

def ObtenerPrecioPromedioBarrio(dataFrameConsulta, dataFramePromediosPorBarrios):
	return dataFrameConsulta.merge(dataFramePromediosPorBarrios, how = 'left', left_on = gIndex, right_on = gIndex)

def ObtenerCoeficiente(dataFrameConsulta, dataFrameCoeficientes, coef):
	return dataFrameConsulta.merge(dataFrameCoeficientes[dataFrameCoeficientes['varName'] == coef], how = 'left', left_on = coef, right_on = 'variable')['coeficiente'].fillna(1)

def ObtenerCoeficienteGlobal(dataFrameConsulta, dataFrameCoeficientes):
	coeficiente_global = pd.Series(1, index = dataFrameConsulta.index)
	for coef in dataFrameCoeficientes['varName'].unique():
		coeficiente_global *= ObtenerCoeficiente(dataFrameConsulta, dataFrameCoeficientes, coef)
	return coeficiente_global

gDiccionarioReconversionTipoPropiedad = {'casa': 'house', 'ph': 'PH', 'departamento': 'apartment', 'tienda': 'store'}
def ReconvertirTipoPropiedad(valor):
	return gDiccionarioReconversionTipoPropiedad[valor]

def ResolverConsulta(dataFrameConsulta, dataFrameCoeficientes, dataFramePromediosPorBarrios):
	preprocessing.PrimeraExpansion(dataFrameConsulta, 'properati-AR-2017-08-01-properties-sell')
	SacarListaColumnas(dataFrameConsulta, ['properati_url',
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
							 'created_on',
							 'created_on_year',
							 'created_on_month',
							 'extra'])
	preprocessing.SegundaExpansion(dataFrameConsulta)
	preprocessing.SegundaLimpieza(dataFrameConsulta)

	#Porque un "gracioso" tradujo los valores
	dataFrameConsulta['property_type'] = dataFrameConsulta['property_type'].map(ReconvertirTipoPropiedad)

	dataFramePromediosPorBarrios = CalcularPromedioBarriosAgosto(dataFramePromediosPorBarrios)
	dataFrameConsulta = ObtenerPrecioPromedioBarrio(dataFrameConsulta, dataFramePromediosPorBarrios)
	dataFrameConsulta['coeficiente_global'] = ObtenerCoeficienteGlobal(dataFrameConsulta, dataFrameCoeficientes)
	dataFrameConsulta['price_usd_per_m2'] = dataFrameConsulta['coeficiente_global'] * dataFrameConsulta['precio_unitario_promedio']
	dataFrameConsulta['price'] = dataFrameConsulta['surface_total_in_m2'] * dataFrameConsulta['price_usd_per_m2']
	return dataFrameConsulta[['id', 'price']]
