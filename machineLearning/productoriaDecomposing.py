import numpy as np
import pandas as pd
import math
from .dataFrameUtils import *

# Calculo de coeficientes
def GenerarDiccionarioCoeficientes(dataFrame, listaNombresCoeficientes):
	diccionarioCoeficientes = {}
	for nombreCoeficiente in listaNombresCoeficientes:
		df = dataFrame[['property_type', 'coeficiente_global']].assign(variable = dataFrame[nombreCoeficiente], coeficiente = pd.Series(1, index = dataFrame.index))
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
	coeficienteDF = coeficienteDF.merge(coeficiente, left_on = ['property_type', 'variable'], right_on = ['property_type', 'variable'], how = 'left')
	coeficienteDF['coeficiente'].fillna(1, inplace = True)
	diccionarioCoeficientes[nombreCoeficiente] = coeficienteDF

def ExtraerCoeficientes(coeficienteDF, column):
	"""Obtiene un dataFrame con los coeficientes"""
	return coeficienteDF[['property_type', 'variable', column]].groupby(by = ['property_type', 'variable'])[column].mean().reset_index(name = 'coeficiente')

def Iterar(diccionarioCoeficientes):
	for k in diccionarioCoeficientes:
		ActualizarNuevoCoeficiente(diccionarioCoeficientes, k)

def CalcularMaximoIteraciones(cantidadCoeficientes):
	#return int(math.ceil(math.sqrt(cantidadCoeficientes)))
	return cantidadCoeficientes
