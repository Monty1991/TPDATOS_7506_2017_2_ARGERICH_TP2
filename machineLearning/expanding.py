from .dataFrameUtils import *
from .descriptionExpansion import Parsear_Descripcion, Inicializar_Diccionario

def ExpandirFechaCreacion(dataFrame):
	dataFrame['created_on_year'] = MapearColumna(dataFrame['created_on'], lambda x: int(x.split('-')[0]))
	dataFrame['created_on_month'] = MapearColumna(dataFrame['created_on'], lambda x: int(x.split('-')[1]))

def ExpandirFechaVolcado(dataFrame, archivo):
	archiveParts = archivo.split('-')
	dataFrame['dump_date_year'] = pd.Series(int(archiveParts[2]), index = dataFrame.index)
	dataFrame['dump_date_month'] = pd.Series(int(archiveParts[3]), index = dataFrame.index)

def ExpandirPais(dataFrame):
	if not 'country_name' in dataFrame:
		dataFrame['country_name'] = MapearColumna(dataFrame['place_with_parent_names'], lambda x: x.split('|')[1])

def ExpandirProvincia(dataFrame):
	if not 'state_name' in dataFrame:
		dataFrame['state_name'] = MapearColumna(dataFrame['place_with_parent_names'], lambda x: x.split('|')[2])

def ExpandirBarrio(dataFrame):
	dataFrame['barrio'] = MapearColumna(dataFrame['place_with_parent_names'], lambda x: x.split('|')[3])

def ExpandirDescripcion(dataFrame, claves):
	if 'description' in dataFrame:
		columnaDescription = [Parsear_Descripcion(value) for value in dataFrame['description']]
	else:
		diccionario = Inicializar_Diccionario(claves)
		columnaDescription = [diccionario for i in range(0, len(dataFrame.index))]

	for k in claves:
		dataFrame[k] = pd.Series([diccionario[k] for diccionario in columnaDescription], index = dataFrame.index)
