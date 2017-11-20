from dataFrameUtils import *
import pandas as pd

#Variables importantes (ejem, constantes)
gListaColumnasIndiceBarrioPromedios = ['barrio', 'state_name', 'property_type', 'dump_date_year', 'dump_date_month']
gNombreColumnaCoeficienteGlobal = 'coeficiente_global'

def CalcularPromediosBarrios(dataFrame):
	"""Genera el dataFrame con los precios promedios unitarios de los barrios en el tiempo"""
	barriosPromedios = dataFrame.groupby(by = gListaColumnasIndiceBarrioPromedios)['price_usd_per_m2'].mean()
	return barriosPromedios.reset_Index(name = 'precio_unitario_promedio')

def AgregarPromediosPorBarrios(dataFrame, dataFrameBarriosPromedios):
	"""Regresa un join del dataFrame con los precios promedios por barrio"""
	return pd.merge(dataFrame, dataFrameBarriosPromedios, how = 'left', left_on = gListaColumnasIndiceBarrioPromedios, right_on = gListaColumnasIndiceBarrioPromedios)

def CalcularCoeficientesGlobales(dataFrame, dataFrameBarriosPromedios):
	"""Calcula los coeficientes globales"""
	return dataFrame['price_usd_per_m2'] / dataFrame['precio_unitario_promedio']

def AgregarCoeficientesGlobales(dataFrame, dataFrameBarriosPromedios):
	dataFrame[gNombreColumnaCoeficienteGlobal] = CalcularCoeficientesGlobales(dataFrame, dataFrameBarriosPromedios)

# ---OK---

def ArmarListaCoeficientes(dataFrame, nombreColumna):
	df = dataFrame.groupby(by = [tipo_propiedad, nombreColumna])[gNombreColumnaCoeficienteGlobal].mean().resetIndex(name = 'coeficiente')
	df['column'] = nombreColumna
	df['valor'] = df[nombreColumna]
	SacarColumna(df, nombreColumna)
	return df

def ArmarDataFrameCoeficientes(dataFrame, listaNombresColumnas):
	listaDataFrameCoeficientes = []
	for nombreColumna in listaNombresColumnas:
		df = dataFrame.groupby(by = [tipo_propiedad, nombreColumna])[gNombreColumnaCoeficienteGlobal].mean().resetIndex(name = 'coeficiente')
		df['column'] = nombreColumna
		df['valor'] = df[nombreColumna]
		SacarColumna(df, nombreColumna)
		listaDataFrameCoeficientes.append(df)
	dataFrameCoeficientes = pd.DataFrame.concat(listaDataFrameCoeficientes)
	return dataFrameCoeficientes

def CalcularCoeficiente(dataFrame, dataFrameCoeficientes, nombreColumna):
	return dataFrame[nombreColumna].map(lambda x: dataFrameCoeficientes[(dataFrameCoeficientes['column'].isin([nombreColumna])) & (dataFrameCoeficientes['valor'] = x)]['coeficiente'])

def CalcularAntiCoeficiente(dataFrame, dataFrameCoeficientes, listaNombresColumnas, nombreColumna):
	"""Es el producto de todos los demás coeficientes"""
	antiCoeficiente = pd.Serie(1, index = dataFrame.index)
	for nombreColumna in listaNombresColumnas:
		if nombreColumna != nombreColumna:
			antiCoeficiente *= CalcularCoeficiente(dataFrame, dataFrameCoeficientes, nombreColumna)
	return antiCoeficiente;

def CalcularCoeficiente(dataFrame, dataFrameCoeficientes, listaNombresColumnas, nombreColumna, nombreColumnaCoeficienteGlobal):
	"""Calcula el coeficiente pedido a través del anticoeficiente"""
	return dataFrame[nombreColumnaCoeficienteGlobal] / CalcularAntiCoeficiente(dataFrame, dataFrameCoeficientes, listaNombresColumnas, nombreColumna)

def ProcesoIterativo(dataFrame, listaNombresColumnas, nombreColumnaCoeficienteGlobal):
	dataFrameCoeficientes = pd.DataFrame()
	for nombreColumna in listaNombresColumnas:
		coef = CalcularCoeficiente(dataFrame, dataFrameCoeficientes, listaNombresColumnas, nombreColumna, nombreColumnaCoeficienteGlobal)
		"""TODO: Convertir los coef en los valores tipo del dataFrameCoeficientes"""
