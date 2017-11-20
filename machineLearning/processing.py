from .dataFrameUtils import *
import pandas as pd

#Variables importantes (ejem, constantes)
gListaColumnasIndiceBarrioPromedios = ['barrio', 'state_name', 'property_type', 'dump_date_year', 'dump_date_month']
gNombreColumnaCoeficienteGlobal = 'coeficiente_global'
gListaNombreColumnasCoeficientes = []

#Precios promedios por barrio y coeficiente global
def CalculaPrecioUnitarioPromedioPorBarrio(dataFrame):
	"""Genera el dataFrame con los precios promedios unitarios de los barrios en el tiempo"""
	barriosPromedios = dataFrame.groupby(by = gListaColumnasIndiceBarrioPromedios)['price_usd_per_m2'].mean()
	return barriosPromedios.reset_index(name = 'precio_unitario_promedio')

def AgregarPromediosPorBarrios(dataFrame, dataFrameBarriosPromedios):
	"""Regresa un join del dataFrame con los precios promedios por barrio"""
	return pd.merge(dataFrame, dataFrameBarriosPromedios, how = 'left', left_on = gListaColumnasIndiceBarrioPromedios, right_on = gListaColumnasIndiceBarrioPromedios)

def CalcularCoeficientesGlobales(dataFrame):
	"""Calcula los coeficientes globales"""
	return dataFrame['price_usd_per_m2'] / dataFrame['precio_unitario_promedio']

def AgregarCoeficientesGlobales(dataFrame):
	dataFrame[gNombreColumnaCoeficienteGlobal] = CalcularCoeficientesGlobales(dataFrame)

# Calculo de coeficientes
def GenerarDiccionarioCoeficientes(dataFrame, listaNombresCoeficientes):
	diccionarioCoeficientes = {}
	for nombreCoeficiente in listaNombresCoeficientes:
		df = dataFrame[['property_type', gNombreColumnaCoeficienteGlobal]].assign(variable = dataFrame[nombreCoeficiente], coeficiente = pd.Series(1, index = dataFrame.index))
		diccionarioCoeficientes[nombreCoeficiente] = df
	return diccionarioCoeficientes

def CalcularAnticoeficiente(diccionarioCoeficientes, nombreCoeficiente, globalIndex):
	"""Genera el anticoeficiente, que es la productoria de los demas coeficientes"""
	antiCoeficiente = pd.Series(1, index = globalIndex)
	for k in diccionarioCoeficientes:
		if k != nombreCoeficiente:
			antiCoeficiente *= diccionarioCoeficientes[k]['coeficiente']
	return antiCoeficiente

def CalcularNuevoCoeficiente(diccionarioCoeficientes, nombreCoeficiente):
	coeficienteDF = diccionarioCoeficientes[nombreCoeficiente]
	coeficienteDF['antiCoeficiente'] = CalcularAnticoeficiente(diccionarioCoeficientes, nombreCoeficiente, coeficienteDF.index)
	coeficienteDF['coefTemp'] = coeficienteDF['coeficiente_global'] / coeficienteDF['antiCoeficiente']
	return coeficienteDF[['property_type', 'variable', 'coefTemp']].groupby(by = ['property_type', 'variable'])['coefTemp'].mean().reset_index(name = 'coeficiente')

def ActualizarNuevoCoeficiente(diccionarioCoeficientes, nombreCoeficiente):
	coeficienteDF = diccionarioCoeficientes[nombreCoeficiente]
	SacarColumna(coeficienteDF, 'coeficiente')
	coeficiente = CalcularNuevoCoeficiente(diccionarioCoeficientes, nombreCoeficiente)
	diccionarioCoeficientes[nombreCoeficiente] = coeficienteDF.merge(coeficiente, left_on = ['property_type', 'variable'], right_on = ['property_type', 'variable'], how = 'left')

def Iterar(diccionarioCoeficientes):
	for k in diccionarioCoeficientes:
		ActualizarNuevoCoeficiente(diccionarioCoeficientes, k)

def ExtraerCoeficientes(coeficienteDF, column):
	"""Obtiene un dataFrame con los coeficientes"""
	return coeficienteDF[['property_type', 'variable', column]].groupby(by = ['property_type', 'variable'])[column].mean().reset_index(name = 'coeficiente')

def ProcesoIterativo(dataFrame, listaNombresCoeficientes):
	diccionarioCoeficientes = GenerarDiccionarioCoeficientes(dataFrame, listaNombresCoeficientes)
	for i in range(len(listaNombresCoeficientes)):
		Iterar(diccionarioCoeficientes)
	return { k : ExtraerCoeficientes(diccionarioCoeficientes[k], 'coeficiente') for k in diccionarioCoeficientes }
