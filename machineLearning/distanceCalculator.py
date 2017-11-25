from .utils import Map
import numpy as np
import math

R = 6371 # Earth mean radius [km]
def Haversine(lat1_inRadians, lat_cos, lon1, lat2, lon2):
	"""Calcula la distancia entre 2 coordenadas usando la formula Haversine"""
	delta_long = math.radians(lon2 - lon1)
	delta_lat = (lat2 - lat1_inRadians)
	a = math.sin(delta_lat / 2) ** 2 + lat_cos * math.cos(lat2) * math.sin(delta_long / 2) ** 2
	c = 2 * math.asin(min(1, math.sqrt(a)))
	# Distance in km
	return R * c

def CalcularDistancia(lat1_inRadians, lat_cos, long1, lat2, long2):
	return Haversine(lat1_inRadians, lat_cos, long1,  math.radians(lat2), long2) * 1000

def ObtenerMenorDistancia(lat, lon, barrio, dataFramePuntos, nombreColumnaBarrio, nombreColumnaLat, nombreColumnaLong):
	"""Dados un par de coordenadas y una bases de puntos coordenados con barrio, obtiene el vecino mas cercano"""
	if np.isnan(lat) or np.isnan(lon):
		#Rechazamos nulos
		return 50000
	vecinos = dataFramePuntos
	if barrio != 'any':
		vecinos = vecinos[vecinos[nombreColumnaBarrio] == barrio]
	if len(vecinos) == 0:
		#Si no hay vecinos, devolvemos una distancia enorme
		return 50000

	#Precomputamos valores invariantes
	lat_inRadians = math.radians(lat)
	lat_cos = math.cos(lat_inRadians)
	return min(Map(zip(vecinos[nombreColumnaLat].values, vecinos[nombreColumnaLong].values), lambda x: CalcularDistancia(lat_inRadians, lat_cos, lon, x[0], x[1])))

def NormalizarDistancias(distancia):
	#dividimos todas las distancias en secciones de 500 metros
	return int(math.floor(distancia / 500))
