from .dataFrameUtils import *
import pandas as pd
from .productoriaDecomposing import *

#Variables importantes (ejem, constantes)
gIndex = ['barrio', 'state_name', 'property_type']
gListaColumnasIndiceBarrioPromedios = gIndex + ['dump_date_year', 'dump_date_month']
gListaNombreColumnasCoeficientes = []

#Precios promedios por barrio
def CalcularPrecioUnitarioPromedioPorBarrio(dataFrame):
	"""Genera el dataFrame con los precios promedios unitarios de los barrios en el tiempo"""
	barriosPromedios = dataFrame.groupby(by = gListaColumnasIndiceBarrioPromedios)['price_usd_per_m2'].mean()
	barriosPromedios = barriosPromedios.reset_index(name = 'precio_unitario_promedio')

	#Genera los casos barrio = state_name
	df = barriosPromedios.groupby(by = ['state_name', 'property_type', 'dump_date_year', 'dump_date_month'])['precio_unitario_promedio'].mean()
	df = df.reset_index(name = 'precio_unitario_promedio')
	df['barrio'] = df['state_name']

	#Metemos todo junto
	return barriosPromedios.append(df)

#Superficies promedios por barrio
def CalcularSuperficiePromedioPorBarrio(dataFrame):
	"""Genera el dataFrame con las superficies promedias de los barrios"""
	barriosPromedios = dataFrame.groupby(by = gListaColumnasIndiceBarrioPromedios)['surface_total_in_m2'].mean()
	barriosPromedios = barriosPromedios.reset_index(name = 'superficies_promedio')

	#Genera los casos barrio = state_name
	df = barriosPromedios.groupby(by = ['state_name', 'property_type', 'dump_date_year', 'dump_date_month'])['superficies_promedio'].mean()
	df = df.reset_index(name = 'superficies_promedio')
	df['barrio'] = df['state_name']

	return barriosPromedios.append(df)

def UnirPromediosPorBarrio(promediosPreciosUnitarios, promediosSuperficies):
	return promediosPreciosUnitarios.merge(promediosSuperficies[gListaColumnasIndiceBarrioPromedios + ['superficies_promedio']],
                                        how = 'left', left_on = gListaColumnasIndiceBarrioPromedios,
                                        right_on = gListaColumnasIndiceBarrioPromedios)

def AgregarPromediosPorBarrios(dataFrame, dataFrameBarriosPromedios):
	"""Regresa un join del dataFrame con los precios promedios por barrio"""
	return pd.merge(dataFrame, dataFrameBarriosPromedios, how = 'left', left_on = gListaColumnasIndiceBarrioPromedios, right_on = gListaColumnasIndiceBarrioPromedios)

def CalcularCoeficientesGlobales(dataFrame):
	"""Calcula los coeficientes globales"""
	return dataFrame['price_usd_per_m2'] / dataFrame['precio_unitario_promedio']

def AgregarCoeficientesGlobales(dataFrame):
	dataFrame['coeficiente_global'] = CalcularCoeficientesGlobales(dataFrame)

def ProcesoIterativo(dataFrame, listaNombresCoeficientes):
	diccionarioCoeficientes = GenerarDiccionarioCoeficientes(dataFrame, listaNombresCoeficientes)
	maxIteraciones = CalcularMaximoIteraciones(len(listaNombresCoeficientes))
	for i in range(maxIteraciones):
		Iterar(diccionarioCoeficientes)
	return pd.concat([ ExtraerCoeficientes(diccionarioCoeficientes[k], 'coeficiente').assign(varName = pd.Series(k, index = diccionarioCoeficientes[k].index)) for k in diccionarioCoeficientes])
