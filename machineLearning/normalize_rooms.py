from .utils import *

def isNumber(posibleNumber):
	"""Indica si es un numero valido"""
	if type(posibleNumber) != str:
		return True
	else:
		return posibleNumber[0].isdigit()

def NormalizeRooms(rooms):
	"""Normaliza un valor posible de expensas"""
	if type(rooms) != str:
		return GetValidNumber(rooms)
	if rooms[0].isdigit():
		return GetValidNumber(rooms)
	rooms = rooms.lower().replace('  ', ' ')
	rooms = Filter(rooms.split(), isNumber)
	return Reduce(Map(rooms, GetValidNumber), lambda x,y: x + y, 0)
