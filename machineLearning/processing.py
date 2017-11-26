import pandas as pd
from . import dataFrameUtils
from .productoriaDecomposing import *

#Variables importantes (ejem, constantes)
gIndex = ['barrio', 'state_name', 'property_type']
gListaColumnasIndiceBarrioMedianas = gIndex + ['dump_date_year', 'dump_date_month']
gListaNombreColumnasCoeficientes = []

#Precios promedios por barrio
def CalcularPrecioUnitarioMedianaPorBarrio(dataFrame):
	"""Genera el dataFrame con los precios promedios unitarios de los barrios en el tiempo"""
	barriosMedianas = dataFrame.groupby(by = gListaColumnasIndiceBarrioMedianas)['price_usd_per_m2'].median()
	barriosMedianas = barriosMedianas.reset_index(name = 'precio_unitario_mediana')

	#Genera los casos barrio = state_name
	df = barriosMedianas.groupby(by = ['state_name', 'property_type', 'dump_date_year', 'dump_date_month'])['precio_unitario_mediana'].median()
	df = df.reset_index(name = 'precio_unitario_mediana')
	df['barrio'] = df['state_name']

	#Metemos todo junto
	return barriosMedianas.append(df)

#Superficies promedios por barrio
def CalcularSuperficieMedianaPorBarrio(dataFrame):
	"""Genera el dataFrame con las superficies promedias de los barrios"""
	barriosMedianas = dataFrame.groupby(by = gListaColumnasIndiceBarrioMedianas)['surface_total_in_m2'].median()
	barriosMedianas = barriosMedianas.reset_index(name = 'superficies_mediana')

	#Genera los casos barrio = state_name
	df = barriosMedianas.groupby(by = ['state_name', 'property_type', 'dump_date_year', 'dump_date_month'])['superficies_mediana'].median()
	df = df.reset_index(name = 'superficies_mediana')
	df['barrio'] = df['state_name']

	return barriosMedianas.append(df)

def UnirMedianasPorBarrio(medianasPreciosUnitarios, medianasSuperficies):
	return medianasPreciosUnitarios.merge(medianasSuperficies[gListaColumnasIndiceBarrioMedianas + ['superficies_mediana']],
                                        how = 'left', left_on = gListaColumnasIndiceBarrioMedianas,
                                        right_on = gListaColumnasIndiceBarrioMedianas)

def AgregarMedianasPorBarrios(dataFrame, dataFrameBarriosMedianas):
	"""Regresa un join del dataFrame con los precios promedios por barrio"""
	return pd.merge(dataFrame, dataFrameBarriosMedianas, how = 'left', left_on = gListaColumnasIndiceBarrioMedianas, right_on = gListaColumnasIndiceBarrioMedianas)

def CalcularCoeficientesGlobales(dataFrame):
	"""Calcula los coeficientes globales"""
	return dataFrame['price_usd_per_m2'] / dataFrame['precio_unitario_mediana']

def AgregarCoeficientesGlobales(dataFrame):
	dataFrame['coeficiente_global'] = CalcularCoeficientesGlobales(dataFrame)

def ProcesoIterativo(dataFrame, listaNombresCoeficientes):
	diccionarioCoeficientes = GenerarDiccionarioCoeficientes(dataFrame, listaNombresCoeficientes)
	maxIteraciones = CalcularMaximoIteraciones(len(listaNombresCoeficientes))
	for i in range(maxIteraciones):
		Iterar(diccionarioCoeficientes)
	return pd.concat([ExtraerCoeficientes(diccionarioCoeficientes[k], 'coeficiente').assign(varName = pd.Series(k, index = diccionarioCoeficientes[k].index)) for k in diccionarioCoeficientes])

def ArreglarRoomsUltimoMomento(dataFrame):
	dataFrame['rooms'].update(dataFrame[dataFrame['rooms'] > 19]['rooms'].map(lambda x: math.floor(x / 10)))

def ParametrizarExpensas(columna):
	return math.floor(columna / 1000)

def ParametrizarExpensasUltimoMomento(dataFrame):
	dataFrame['expenses'].update(dataFrame['expenses'].map(lambda x: math.floor(x / 1000)))

def Procesar(carpetaArchivosPreprocesados, nombreArchivoMedianas, nombreArchivoCoeficientes, listaNombresCoeficientes):

	dataFrame = dataFrameUtils.LeerCarpetaDataFrames('./processed/')
	#Yep
	ArreglarRoomsUltimoMomento(dataFrame)
	ParametrizarExpensasUltimoMomento(dataFrame)

	barriosPrecioUnitario = CalcularPrecioUnitarioMedianaPorBarrio(dataFrame)
	barriosSuperficie = CalcularSuperficieMedianaPorBarrio(dataFrame)
	barrios = UnirMedianasPorBarrio(barriosPrecioUnitario, barriosSuperficie)
	barrios.to_csv(nombreArchivoMedianas, encoding = 'utf-8', index = False)

	dataFrame = AgregarMedianasPorBarrios(dataFrame, barriosPrecioUnitario)
	AgregarCoeficientesGlobales(dataFrame)

	coeficientes = ProcesoIterativo(dataFrame, listaNombresCoeficientes)
	coeficientes.to_csv(nombreArchivoCoeficientes, encoding = 'utf-8', index = False)
